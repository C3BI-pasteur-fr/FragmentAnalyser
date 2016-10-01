#!/usr/bin/python
import time
import os
import sys
import argparse
import easydev
from easydev.console import red, purple, darkgreen
from fragment_analyser import version
from .plate import Plate



# Used to avoid issue with missing DISPLAY on the cluster.
import pylab

t3 = time.time()


def print_color(txt, func_color=darkgreen, underline=False):
    try:
        if underline:
            print(easydev.underline(func_color(txt)))
        else:
            print(func_color(txt))
    except:
        print(txt)


class Options(argparse.ArgumentParser):
    """


    """
    def __init__(self, prog=None):
        usage = """

    fragment_analyser.py --pattern 2015*csv
    fragment_analyser.py --pattern 2015*csv --lower-bound 100
    fragment_analyser.py --pattern 2015*csv --guess 650 --tag test

        """
        epilog = """ -- """
        description = """ Reads a set of CSV files from Fragment Analyser systems and created (1) image of detected peaks across each line (each CSV) and (2) 2 CSV files summarising the detected peaks in all input CSV files. The 2 output CSV files  contains the same data but the **filtered** assume a homogeneous set of peaks and crossed the ones that are identified as outliers."""
        super(Options, self).__init__(usage=usage, prog=prog, epilog=epilog,
                                      description=description,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
        group = self.add_argument_group('General', "General options")
        group.add_argument('-p', "--pattern", type=str, dest="pattern", nargs="+",
                           help="A pattern to fetch filenames (e.g. 2016*csv)")
        group.add_argument('-o', "--output", type=str, default="summary.csv",
                           help="The name of the output CSV file. Defaults to summary.csv")
        group.add_argument('-t', "--tag", type=str, default="",
                           help="""The name of a tag to append before the
                           extension .csv. For instance --tag test will
                           create the file summary_test.csv not just summary.csv""")
        group.add_argument('-n', "--no-images",  action="store_false",
                           dest="create_images",
                           help="""For each input file, an image is created.
                                If not required, use this option""")
        group.add_argument('-r', '--precision', type=int, default=8,
                           help="set number of digits in the output CSV")
        group.add_argument('-l', "--lower-bound", default=120, type=int,
                           help="""All fragments below the lower bound are ignored (inclusive)""")
        group.add_argument('-u', "--upper-bound", default=6000, type=int,
                   help="""All fragment above the upper bound are ignored (inclusive)""")
        group.add_argument("-s", "--sigma", default=50, type=float,
                           help="""Peaks are weighted down by a gaussian
distribution centered around the guessed best peak (see --guess) and with a
sigma of 50 by default, which can be changed with this parameter.""")
        group.add_argument("-g", "--guess", default=None, type=float,
                           help="""Position of the peak to be identified. If not
provided, guessed from the median of the maximum across the line.""")




def main(args=None):

    msg = "Welcome to FragmentAnalyser standalone application"
    print_color(msg, purple, underline=True)

    msg = "Version: %s\n" % version
    msg += "Author: Thomas Cokelaer thomas.cokelaer@pasteur.fr\n"
    msg += "Information and documentation on " + \
           "https://github.com/C3BI-pasteur-fr/FragmentAnalyser\n"
    print_color(msg, purple)

    if args is None:
        args = sys.argv[:]
    if len(args) == 1:
        args += ['--help']

    options = Options()
    options = options.parse_args(args[1:])

    # a user may use 2015*csv on the command line, which is expanded into a list
    # of filse unless user place quotes around it "2015*csv". It is highly
    # likely that most users won't understand and forget the quotes

    if "*" in options.pattern or "?" in options.pattern:
        import glob
        filenames = glob.glob(options.pattern)
    else:
        filenames = options.pattern

    print("Info: found %s file(s) to analyse" % len(filenames))
    for filename in filenames:
        print('- %s' % filename)
    output_filename = options.output



    # Save the CSV summary files setting the precision

    plate = Plate(filenames, guess=options.guess,
                  sigma=options.sigma,
                  lower_bound=options.lower_bound,
                  upper_bound=options.upper_bound)
    plate.analyse() # by default keep all data

    # apply precision on numeric data
    for col in plate.data._get_numeric_data().columns:
        data = plate.data[col].apply(lambda x: round(x, options.precision))
        plate.data[col] = data

    if options.tag:

        plate.to_csv(output_filename.replace(".csv",
                                             "_all_%s.csv" % options.tag))
    else:
        plate.to_csv(output_filename.replace(".csv", "_all.csv"))

    # we may also consider that lines are uniform so outliers must be crossed
    plate.filterout()

    if options.tag is not None:
        plate.to_csv(output_filename.replace(".csv",
                                             "_filtered_%s.csv" % options.tag))
    else:
        plate.to_csv(output_filename.replace(".csv", "_filtered.csv"))

    if options.create_images is False:
        pass
    else:
        print("\nCreating images")
        count = 1

        image_filenames = []
        for filename, line in zip(filenames, plate.lines):
            # get the filename
            filename = os.path.split(filename)[1]

            # replace extension csv to png
            lhs, _ext = os.path.splitext(filename)

            if options.tag is None:
                image_filename = lhs + ".png"
            else:
                image_filename = lhs + "_%s.png" % options.tag

            if image_filename not in image_filenames:
                image_filenames.append(image_filename)
            else: # if it exists already, let us append a unique id:
                image_filename = lhs + "_%s.png" % count
                count += 1
                image_filenames.append(image_filename)

            print("Creating image %s out of %s (%s)" %
                  (count, len(plate.lines), image_filename))
            line.diagnostic()
            pylab.savefig(image_filename)



    # Create a log file
    if options.tag is None:
        log_filename = "fa.log"
    else:
        log_filename = "fa_%s.log" % options.tag

    with open(log_filename, "w") as fout:
        fout.write("Command run:\n")
        fout.write("\n%s" % " ".join(args))
        fout.write("\n\n%s file(s) was/were read and interpreted\n" % len(filenames))
        for filename in filenames:
            fout.write(" - %s\n" % filename)
        fout.write("\n%s" % plate.__str__())
        fout.write("\nFragment Analyser version: %s" % version)





