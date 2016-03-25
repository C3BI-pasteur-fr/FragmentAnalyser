#!/usr/bin/python
"""

"""
import numpy as np
import pandas as pd

from .well import Well


class PeakTableReader(object):
    """Read a fragment analyser data set.


    Reads a file with fragment anlyser data::

        from fragment_analyser import PeakTableReader, fa_data
        ptr = PeakTableReader(fa_fata("alternate/peaktable.csv"))
        ptr.df

    This class does not need to be used. It is used by :class:`~fragment_analyser.line.Line`.

    There are 2 possible input formats. One is a pure CSV format, which we will call **standard**.
    The other format is called **alternate**: it mixed CSV tables and sub-tables as shown later.
    Although the alternate files have the extension .csv, there qre not strictly speaking CSV files.
    However, they can be read as CSV and then interpreted.

    This class accepts the 2 formats and will automatically figure out what is the underlying format simply
    looking at the header.

    The alternate format looks like::

        B1,BJ,,,,,
        Peak ID,Size (bp),% (Conc.),nmole/L,ng/ul,RFU,Avg. Size
        1,1 (LM),,21.475,0.0164,1740,1
        2,65,26.4,2.220,0.0875,842,67
        3,168,62.0,2.007,0.2055,541,162
        4,608,11.6,0.104,0.0384,100,610
        5,6000 (UM),,0.001,0.0035,594,6012
        , , ,,,,
        ,TIC: ,0.3314, ng/uL,,,
        ,TIM: ,4.331, nmole/L,,,
        ,Total Conc.: ,0.6760, ng/uL,,,
        ,,,,,,
        B2, BK,,,,,
        .
        .

    The standard format looks like::

        Well,Sample ID,Peak ID,Size (bp),% (Conc.),nmole/L,ng/ul,RFU,Avg. Size,TIC (ng/ul),TIM (nmole/L),Total Conc. (ng/ul)
        B1,203,1,1,,165.013,0.1263,1562,2,46.2333,65.343 nmole/L,46.2689
        B1,203,2,1165,100.0,65.343,46.2333,904,900,46.2333,65.343 nmole/L,46.2689
        B1,203,3,6000,,0.041,0.1493,1608,6085,46.2333,65.343 nmole/L,46.2689
        B2,200,1,1,,165.013,0.1263,1460,1,24.4814,80.962 nmole/L,24.6155
        B2,200,2,498,100.0,80.962,24.4814,359,706,24.4814,80.962 nmole/L,24.6155
        B2,200,3,6000,,0.037,0.1359,1613,6012,24.4814,80.962 nmole/L,24.6155
        B3,199,1,1,,165.013,0.1263,1365,5,47.9139,57.906 nmole/L,47.9479

    Here, the wells are named B1, B2, B3 ... Other lines may be named A1, A2, ...
    Each file contains the data for a single line and uses a single letter from A to H corresponding
    to one of the 8 possible line on a given plate.

    You can get examples from ::

        import fragment_analyser as fa
        fa.fa_data("standard_mix_cases/peaktable.csv")
        fa.fa_data("alternate/peaktable.csv")

    The data are stored in the :attr:`df` dataframe. The columns' names are extracted from the CSV

    .. note:: the data below bp=1 and above bp=6000 are removed.


    """
    def __init__(self, filename, sigma=50, lower_bound=120, upper_bound=6000):
        """.. rubric:: Constructor

        :param filename: a valid fragment analyser input file
        :param sigma:

        """
        self.filename = filename
        self.sigma = sigma
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

        # guess the mode (CSV input files are in mode alternate or mode standard)
        self._guess_mode()

        # two types of input data (standard or alternate) require specific
        # interpretation:
        self.interpret()
        self._nwells = len(self.wells)

    def _guess_mode(self):
        df = pd.read_csv(self.filename, sep=",")
        if 'Well' in df.columns:
            self.mode = "standard"
        else:
            self.mode = "alternate"

    def _identify_names(self):
        # Each of the 8 plates is labelled by a letter from A to H
        names = [x for x in self.df[0].dropna().unique() if x.strip()
                 and x[0] in 'ABCDEFGH']

        # make sure there is no spaces
        self.names = [name.strip() for name in names]

    def _identify_start(self):
        # For the alternate case, let us keep track of the starting position of each name
        positions = [self.df.index[(self.df[0] == name)][0]
                     for name in self.names]
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
            data['TIM (nmole/L)'] = data['TIM (nmole/L)'].apply(lambda x:
                                                                x.split(" ")[0])

            # convert all data to the correct type:
            for colname in data.columns:
                if colname in ['Well', 'Sample ID']:
                    pass
                else:
                    data[colname] = data[colname].astype(float)

            well = Well(data, sigma=self.sigma, lower_bound=self.lower_bound,
                        upper_bound=self.upper_bound)
            wells.append(well)

        self.wells = wells

    def interpret_alternate(self):
        # Read a CSV file
        print('Alternate input data')
        self.df = pd.read_csv(self.filename, sep=",", header=None)
        # replaces spaces or empty spaces by empty na
        self.df = self.df.applymap(lambda x: np.nan if isinstance(x, str)
                                                       and x.isspace() else x)

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
            metadata = metadata.iloc[:, [1,2,3]]  # keep columns with data
            metadata = metadata.dropna()
            metadata.reset_index(inplace=True, drop=True)

            # ul should be uL but keep ul as in the original CSV file for now
            data['TIC (ng/ul)'] = float(metadata.ix[0][1])
            data['TIM (nmole/L)'] = float(metadata.ix[1][1])
            data['Total Conc. (ng/ul)'] = float(metadata.ix[2][1])

            # get rid of TIC; TIM, Total conc rows (where Peak ID is NA)
            data = data[data['Peak ID'].isnull() == False].copy()

            # Get rid of UM and LM in (Siwe bp) column
            data["Size (bp)"] = data["Size (bp)"].apply(lambda x:
                                    x.replace('(UM)', '').replace("(LM)", ""))

            for colname in data.columns:
                if colname in ['Well', 'Sample ID']:
                    pass
                data[colname] = data[colname].astype(float)

            data.insert(0, "Sample ID", well_ID)
            data.insert(0, "Well", well_name)
            well = Well(data, sigma=self.sigma, upper_bound=self.upper_bound,
                        lower_bound=self.lower_bound)
            wells.append(well)

        self.wells = wells










