#!/usr/bin/python
import sys
import argparse
import easydev
from easydev.console import red, purple, darkgreen
from fragment_analyser import version

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
        group.add_argument('-o', "--output", type=str,
                           help="The name of the output CSV file. Defaults to summary.csv")
        group.add_argument('-n', "--no-images",  action="store_false",
                           dest="create_images",
                           help="""For each input file, an image is created.
                                If not required, use this option""")





def main(args=None):
    msg = "Welcome to FragmentAnalyser standalone application\n"
    msg += "Version: %s\n" % version
    msg += "Information and documentation on " +  \
           "https://github.com/C3BI-pasteur-fr/FragmentAnalyser\n"
    print_color(msg, purple, underline=True)

    if args is None:
        args = sys.argv[:]
    if len(args) == 1:
        args += ['--help']



    options = Options()
    options = options.parse_args(args[1:])
    print options.pattern

    # a user may use 2015*csv on the command line, which is expanded into a list
    # of filse unless user place quotes around it "2015*csv". It is highly
    # likely that most users won't understand and forget the quotes

    if "*" in options.pattern or "?" in options.pattern:
        import glob
        filenames = glob.glob(options.pattern)
    else:
        filenames = options.pattern


    print filenames


    output_filename = options.output


    platform = raw_input("What data / platform is this ? (PFGE / PF1):")
    assert platform in ["PFGE", "PF1"]

    from .plate import PlatePF1, PlatePFGE
    if platform == "PFGE":
        plate = PlatePFGE(filenames, output_filename=output_filename)
    else:
        plate = PlatePF1(filenames, output_filename=output_filename)

    plate.to_csv()

    print options.create_images
    if options.create_images is False:
        pass
    else:
        print("Creating images")
        for i, line in enumerate(plate.lines):
            filename = '%s_diagnostic.png' % str(i+1) 
            print("Creating image %s out of %s (%s)" % (i+1, len(plate.lines),
                filename))
            line.diagnostic()
            pylab.savefig(filename)


