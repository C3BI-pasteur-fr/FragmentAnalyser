#!/usr/bin/python
from .tools import nonemedian
from .line import Line

import numpy as np
import pandas as pd


# Used to avoid issue with missing DISPLAY on the cluster.
import matplotlib
matplotlib.use('Agg')
import pylab


class Plate(object):
    """Dedicated class for plates

    A plate contains (at most) 8 :class:`lines` with 12 :class:`well` each.

    This is a Abstract base class and 2 children classes are derived from it to 
    read different types of input data:

        - :class:`PlatePF1`
        - :class:`PlatePFGE`

    """
    def __init__(self, filenames, mode, guess=None, lower_bound=1,
                 upper_bound=1e6,  sigma=50, nwells=12):

        self.filenames = filenames
        self.guess = guess
        self._nwells = nwells
        self.sigma = sigma
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.minmad = 25

        self.mode = mode
        assert mode in ["mix", "uniform"]

        self.mw_dna = 650
        self._get_lines()
    
    def _get_lines(self):
        print("Reading %s file(s):" % len(self.filenames))
        self.lines = []
        for filename in self.filenames:
            print(" - " + filename),
            try:
                line = Line(filename, sigma=self.sigma)

                # THIS LINE IS IMPORTANT TO WEIGHT DOWN OUTLIERS
                line.set_guess(self.guess)
                self.lines.append(line)
                print('...done')
            except Exception as err:
                print(err)
                print('WARNING. This file could not be interpreted')

    def get_data(self):
        data = []
        for line in self.lines:
            for well in line.wells:
                res = well.get_peak_and_index()
                if res:
                    peak, index = res
                    data.append(well.df.ix[index])
                else:
                    # If no peak detected, create a line with well name and ID
                    df = well.df.copy()
                    N = len(df.columns)
                    df.ix[0] = [well.name, well.well_ID] + [None] * 11
                    data.append(df.ix[0])
        df = pd.DataFrame(data)
        df.reset_index(inplace=True, drop=True)
        df.drop('Peak ID', axis=1, inplace=True)
        return df

    def to_csv(self, filename="results.csv"):
        if self.mode == "mix":
            df = self.get_data()
        elif self.mode == "uniform":
            df = self.get_data()
            #df = df[['names', 'conc', 'size', 'amount']]
            #df.columns = ['names', 'ng/uL (QUBIT/FA)', 'Size (bp)', 'nM']
            df = self.filterout(df)

        df.to_csv(filename, index=False)

    def filterout(self, df):

        # Compute the MAD
        from . import tools
        peaks = df['Size (bp)'].dropna()

        mad = tools.get_mad(peaks)
        if mad < self.minmad:
            mad = self.minmad


        data = df['Size (bp)']
        from .tools import nonemedian
        med = nonemedian(data.values)

        mask1 = data < med -3*mad
        mask2 = data > med + 3*mad
        mask = np.logical_or(mask1, mask2) == True

        columns = df.columns
        columns = [x for x in columns if x not in ['Sample ID', 'Well']]
        df.loc[mask,columns] = None

        return df


