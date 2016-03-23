#!/usr/bin/python
import sys
import argparse


import numpy as np
import pandas as pd


# Used to avoid issue with missing DISPLAY on the cluster.
import matplotlib
matplotlib.use('Agg')
import pylab



def nonemedian(data):
    # same as numpy but handles None instead of nan
    data = [x for x in data if x is not None]
    return np.median(data)



class PeakTableReader(object):
    """Read a fragment analyser data set

    """
    def __init__(self, filename="2015_07_20_20H_52M_Peak_Table.csv", sigma=50):
        """.. rubric:: Constructor

        :param filename:
        :param sigma:

        """
        self.filename = filename
        self.sigma = sigma

        # guess the mode (CSV input files are in mode alternate or mode standard)
        self._guess_mode()

        # two types of input data (standard or alternate) require specific
        # interpretation:
        self.interpret()

    def _guess_mode(self):
        df = pd.read_csv(self.filename, sep=",")
        if 'Well' in df.columns:
            self.mode = "standard"
        else:
            self.mode = "alternate"

    def _identify_names(self):
        # Each of the 8 plates is labelled by a letter from A to H
        names = [x for x in self.df[0].dropna().unique() if x.strip() and x[0] in 'ABCDEFGH']
        assert len(names) == 12
        # make sure there is no spaces
        self.names = [name.strip() for name in names]

    def _identify_start(self):
        # let us keep track of the starting position of each name
        positions = [self.df.index[(self.df[0] == name)][0] for name in self.names]
        self.start_positions = positions

    def _identify_end(self):
        # READ one file corresponding to one Line that is 12 wells
        ends = []
        for name, position in zip(self.names, self.start_positions):
            # not optimal but let us make it simple and scan the dataframe
            # for each name to retrieve only the data corresponding to the
            # name. Using the position, we can jump to the start 
    
            # find index where the current name ends
            found = -1
            # +1 to skip the row with the name itself
            for index, line in self.df.ix[position+1:].iterrows():
                line = line.fillna("")
                if line[0].strip() in self.names:
                    found = index
                    break
            if found == -1:
                found = index
            ends.append(found)
        self.end_positions = ends

    def interpret(self):
        if self.mode == "alternate":
            self.interpret_alternate()
        elif self.mode == "standard":
            self.interpret_standard()

    def interpret_standard(self):
        print('Standard input data')
        self.df = pd.read_csv(self.filename, sep=",")
        #self.df.fillna('', inplace=True)
        # replaces spaces by empty strings
        #self.df = self.df.applymap(lambda x: x.strip())
        #identify names
        self.names = list(self.df.Well.unique())
        wells = []

        for i, well_name in enumerate(self.names):
            data = self.df.ix[self.df.groupby("Well").groups[well_name]]
            # column TIM contains the unit, redundant with header. Besides,
            # cannot be used as float:
            data['TIM (nmole/L)'] = data['TIM (nmole/L)'].apply(lambda x: x.split(" ")[0])

            # convert all data to the correct type:
            for colname in data.columns:
                if colname in ['Well', 'Sample ID']:
                    pass
                else:
                    data[colname] = data[colname].astype(float)

            well_ID = data['Sample ID'].unique()[0]

            # !! data may be empty once the 0 and 6000 controls are removed
            mask = data['Size (bp)'].apply(lambda x: x>1 and x<5999)
            data = data[mask]

            well = Well(well_name, well_ID, data, sigma=self.sigma)
            wells.append(well)
        self.wells = wells

    def interpret_alternate(self):
        # Read a CSV file
        print('Alternate input data')
        self.df = pd.read_csv(self.filename, sep=",", header=None)
        # replaces spaces or empty spaces by empty na
        self.df = self.df.applymap(lambda x: np.nan if isinstance(x, str) and x.isspace() else x)

        # identify the submatrices in the CSV file
        self._identify_names()
        self._identify_start()
        self._identify_end()

        wells = []

        for i, name in enumerate(self.names):
            subdf = self.df.ix[self.start_positions[i]:self.end_positions[i]-1].copy()

            subdf.reset_index(inplace=True, drop=True)

            # get some data
            well_name = subdf.ix[0][0]
            well_ID = subdf.ix[0][1]

            data = subdf.copy()
            data = data.ix[1:] # drop first line ( well and samples ids)
            # then get next line to set the header
            data.columns = data.ix[1].values
            # drop the row used for the header, note that we start at index 2
            # since indices have names
            data = data.ix[2:]
            # now we will start at zero again
            data.reset_index(inplace=True, drop=True)

            # right now we have a dataframe with all data and metadata (TIV,
            # TIM, Total conc). Let us extract the metadata to get the value
            # of the RIC, TIM, Total conc
            metadata = data[data['Peak ID'].isnull()]

            # access 
            metadata = metadata.iloc[:, [1,2,3]]  # keep columns with data
            metadata = metadata.dropna()
            metadata.reset_index(inplace=True, drop=True)

            # Remove the rows where Size bp is the lower or upper mark (usually
            # at size = 1 or 6000. It has a string LM or UM in it
            self.data= data
            mask = data['Size (bp)'].apply(lambda x: isinstance(x, str) 
                    and 'UM' not in x and 'LM' not in x)

            data = data[mask].copy()

            data['TIC (ng/uL)'] = float(metadata.ix[0][1])
            data['TIM (nmole/L)'] = float(metadata.ix[1][1])
            data['Total Conc.: (ng/uL)'] = float(metadata.ix[2][1])

            # convert all data to the correct type:
            # get rid of rows where there are NAs, so TIC; TIM, Total conc
            # should be dropped 
            data.dropna(inplace=True)

            for colname in data.columns:
                if colname in ['Well', 'Sample ID']:
                    pass
                data[colname] = data[colname].astype(float)
                #except:
                #    data[colname] = data[colname]

            from .well import Well
            well = Well(well_name, well_ID, data, sigma=self.sigma)
            wells.append(well)

        self.wells = wells

    def get_line(self):
        # Returns  only 11 wells instead of 12. The last one one being the
        # control
        from . line import Line
        line = Line()
        for well in self.wells[0:-1]:
            line.append(well)
        line.control = self.wells[-1]
        return line

    def diagnostic(self):
        line = self.get_line()
        line.diagnostic()

    def get_peaks(self):
        line = self.get_line()
        return line.get_peaks()


def help():
    print("Usage:\n")
    print("fragment_analyser.py --pattern 2015*csv\n")
    print("fragment_analyser.py --pattern 2015*csv --output summary.csv\n")
    print("fragment_analyser.py --pattern 2015*csv --create-images\n")


def main():
    print('youpi')


    import sys
    print("Starting Fragment Analyser:")

    if len(sys.argv) <3 or  '--pattern' not in sys.argv:
        help()
        sys.exit()


    index = sys.argv.index("--pattern")
    pattern = sys.argv[index+1]


    # a user may use 2015*csv on the command line, which is expanded into a list
    # of filse unless user plase quotes around it "2015*csv". It is highly
    # likely that most users won't understand and forget the quotes

    if "*" in pattern or "?" in pattern:
        import glob
        filenames = glob.glob(pattern)
    else:
        # how many files do we have
        filenames = []
        # loop on sys.argv until we have a --
        count = index
        found = True
        while found:
            try:
                newfile = sys.argv[index+count]
                if newfile.startswith('--'):
                    found = False
                else:
                    filenames.append(newfile)
                    count += 1
            except:
                found = False


    if '--output' in sys.argv:
        index = sys.argv.index("--output")
        output_filename = sys.argv[index+1]
    else:
        output_filename = 'results.csv'


    if "--platform" in sys.argv:
        platform = sys.argc.index("--platform")
        output_filename = sys.argv[index+1]
    else:
        platform = raw_input("What data / platform is this ? (PFGE / PF1):")
    assert platform in ["PFGE", "PF1"]

    from .plate import PlatePF1, PlatePFGE
    if platform == "PFGE":

        plate = PlatePFGE(filenames, output_filename=output_filename)
    else:
        plate = PlatePF1(filenames, output_filename=output_filename)

    plate.to_csv()

    if '--no-images' in sys.argv:
        pass
    else:
        print("Creating images")
        for i, line in enumerate(plate.lines):
            filename = '%s_diagnostic.png' % str(i+1) 
            print("Creating image %s out of %s (%s)" % (i+1, len(plate.lines),
                filename))
            line.diagnostic()
            pylab.savefig(filename)





if __name__ == "__main__":
    main(sys.argv)