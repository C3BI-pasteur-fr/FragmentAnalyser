#!/usr/bin/python
from .tools import nonemedian
from .line import Line

import numpy as np
import pandas as pd


# Used to avoid issue with missing DISPLAY on the cluster.
import matplotlib
matplotlib.use('Agg')



class Plate(object):
    """Dedicated class for plates

    A plate contains (at most) 8 :class:`lines` with 12 :class:`well` each.

    This is a Abstract base class and 2 children classes are derived from it to 
    read different types of input data:

        - :class:`PlatePF1`
        - :class:`PlatePFGE`

    """
    def __init__(self, filenames, guess=None, lower_bound=1,
                 upper_bound=1e6,  sigma=50):

        self.filenames = filenames
        self.guess = guess
        self.sigma = sigma
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.minmad = 25

        self.mw_dna = 650
        self._get_lines()

    def __str__(self):
        msg = "parameters:\n"
        msg += " - sigma: %s\n" % self.sigma
        msg += " - lower_bound: %s\n" % self.lower_bound
        msg += " - upper_bound: %s\n" % self.upper_bound
        msg += " - minmad : %s\n" % self.minmad
        msg += " - guess: %s\n" % self.guess
        return msg

    def _get_lines(self):
        print("\nReading and Analysing %s file(s):" % len(self.filenames))
        self.lines = []
        for filename in self.filenames:
            print(" - " + filename),
            try:
                line = Line(filename, sigma=self.sigma)

                # THIS LINE IS IMPORTANT TO WEIGHT DOWN OUTLIERS
                line.set_guess(self.guess)
                self.lines.append(line)
            except Exception as err:
                print(err)
                print('WARNING. This file could not be interpreted')

    def analyse(self):
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
            # if there is a ldder/control, let us add it with only the name
            # and id, skipping any data
            if line.control is not None:
                ts = line.control.df.iloc[0].copy()
                for this in ts.index:
                    if this in ['Well', 'Sample ID']: pass
                    else: ts.ix[this] = None
                data.append(ts)

        df = pd.DataFrame(data)
        df.reset_index(inplace=True, drop=True)
        df.drop('Peak ID', axis=1, inplace=True)
        self.data = df

    def to_csv(self, filename="results.csv"):
        self.data.to_csv(filename, index=False)

    def filterout(self):
        # inplace
        df = self.data
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

        self.data = df


