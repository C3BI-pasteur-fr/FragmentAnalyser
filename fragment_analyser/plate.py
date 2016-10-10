#!/usr/bin/python
from .tools import nonemedian
from .line import Line

import numpy as np
import pandas as pd


class Plate(object):
    """Reads several files (lines) and save a summary file

    A plate contains (at most) 8 :class:`lines` with 12 :class:`well` each.


    """
    def __init__(self, filenames, guess=None, lower_bound=120,
                 upper_bound=6000,  sigma=50, peak_mode="max"):
        self.filenames = filenames
        self.guess = guess
        self.sigma = sigma
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.minmad = 25
        self.mw_dna = 650
        self.peak_mode = peak_mode
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
                line = Line(filename, sigma=self.sigma,
                            lower_bound=self.lower_bound,
                            upper_bound=self.upper_bound,
                            peak_mode=self.peak_mode)

                # THIS LINE IS IMPORTANT TO WEIGHT DOWN OUTLIERS
                if self.peak_mode == "max":
                    line.set_guess(self.guess)
                self.lines.append(line)
            except Exception as err:
                print(err)
                print('WARNING. This file could not be interpreted')

    def analyse(self):
        """Reads the N files and create a summary data set

        Must be called before :meth:`to_csv`.
        """
        data = []
        for line in self.lines:
            for well in line.wells:
                if self.peak_mode == "max":
                    res = well.get_peak_and_index()
                else:
                    res = well.get_most_concentrated_peak()
                if res:
                    peak, index = res
                    data.append(well.df.ix[index])
                else:
                    # If no peak detected, create a line with well name and ID
                    # but no data
                    df = well.df.copy()
                    N = len(df.columns)
                    df.ix[0] = [well.name, well.well_ID] + [None] * (N-2)
                    data.append(df.ix[0])

        df = pd.DataFrame(data)
        df.reset_index(inplace=True, drop=True)

        # new format has no Peak ID
        if "Peak ID" in df.columns:
            df.drop('Peak ID', axis=1, inplace=True)
        self.data = df

    def to_csv(self, filename="results.csv"):
        self.data.to_csv(filename, index=False)

    def filterout(self):
        """Remove entries that are outside the expected range.

        To be used if the data is homogeneous to remove outliers;


        """
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
        med = nonemedian(data.dropna().values)

        mask1 = data < med -3*mad
        mask2 = data > med + 3*mad
        mask = np.logical_or(mask1, mask2) == True

        columns = df.columns
        columns = [x for x in columns if x not in ['Sample ID', 'Well']]
        df.loc[mask,columns] = None

        self.data = df



