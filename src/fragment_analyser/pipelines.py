#!/usr/bin/python
import os
import sys
import argparse
import easydev
from easydev.console import red, purple, darkgreen
from fragment_analyser import version
from .plate import Plate

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
        group.add_argument('-t', "--tag", default="", type=str,
                           help="")





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


    print_color("\n\nWhat type of input do you have across the line(s) ? ", darkgreen)
    mode = raw_input("uniform (u) or mix of experiments (m) ? (default is m if you press enter):")

    if mode == "u": mode = "uniform"
    elif mode == "m": mode = "mix"
    else:
        print(red('default mode (mix of experiments) selected'))
        mode = 'mix'

    plate = Plate(filenames, mode)

    plate.to_csv(output_filename)

    if options.create_images is False:
        pass
    else:
        print("Creating images")
        count = 1
        for filename, line in zip(filenames, plate.lines):
            # get the filename
            filename = os.path.split(filename)[1]

            # replace extension csv to png
            lhs, _ext = os.path.splitext(filename)
            filename = '%s_%s.png' % (lhs, count)

            print filename

            print("Creating image %s out of %s (%s)" % (count, len(plate.lines), filename))
            line.diagnostic()
            pylab.savefig(filename)

            count += 1


