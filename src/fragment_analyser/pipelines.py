#!/usr/bin/python
import os
import sys
import argparse
import easydev
from easydev.console import red, purple, darkgreen
from fragment_analyser import version
from .plate import Plate


from easydev import Logging

# Used to avoid issue with missing DISPLAY on the cluster.
import matplotlib
matplotlib.use('Agg')
import pylab


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
    fragment_analyser.py --pattern 2015*csv --output summary.csv
    fragment_analyser.py --pattern 2015*csv --create-images

        """
        epilog = """ -- """
        description = """ todo """
        super(Options, self).__init__(usage=usage, prog=prog, epilog=epilog,
                                      description=description,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
        group = self.add_argument_group('General', "General options")
        group.add_argument('-p', "--pattern", type=str, dest="pattern", nargs="+",
                           help="A pattern to fetch filenames (e.g. 2016*csv)")
        group.add_argument('-o', "--output", type=str, default="summary.csv",
                           help="The name of the output CSV file. Defaults to summary.csv")
        group.add_argument('-n', "--no-images",  action="store_false",
                           dest="create_images",
                           help="""For each input file, an image is created.
                                If not required, use this option""")
        group.add_argument('-r', '--precision', type=int, default=8,
                           help="set number of digits")
        group.add_argument('-l', "--lower-bound", default=120, type=int,
                           help="""All fragment below the lower bound are ignored (inclusive)""")
        group.add_argument('-u', "--upper-bound", default=6000, type=int,
                   help="""All fragment above the upper bound are ignored (inclusive)""")


def main(args=None):

    msg = "Welcome to FragmentAnalyser standalone application"
    print_color(msg, purple, underline=True)

    msg = "Version: %s\n" % version
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

    plate = Plate(filenames)
    plate.analyse() # by default keep all data

    # apply precision on numeric data
    for col in plate.data._get_numeric_data().columns:
        data = plate.data[col].apply(lambda x: round(x, options.precision))
        plate.data[col] = data

    plate.to_csv(output_filename.replace(".csv", "_all.csv"))

    # we may also consider that lines are uniform so outliers must be crossed
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

            image_filename = lhs + ".png"
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
    with open("fa.log", "w") as fout:
        fout.write("Command run:\n")
        fout.write("\n%s" % " ".join(args))
        fout.write("\n\n%s files were read and interpreted\n" % len(filenames))
        for filename in filenames:
            fout.write(" - %s" % filename)
        fout.write("\nParameter: %s" % plate.__str__())





