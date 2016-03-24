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
    def __init__(self, filenames, guess=None, lower_bp=1, upper_bp=1e6,
        sigma=50, output_filename="results.csv"):

        self.filenames = filenames
        self.guess = guess
        self.number_wells = 12
        self.sigma = sigma
        self.output_filename = output_filename
        self.lower_bp = lower_bp
        self.upper_bp = upper_bp
    
    def get_lines(self):
        print("Reading the %s files:" % len(self.filenames))
        self.lines = []
        for filename in self.filenames:
            print(" - " + filename),
            try:
                line = Line(filename, sigma=self.sigma)

                # THIS LINE IS IMPORTAANT TO WEIGHT DOWN OUTLIERS
                line.set_guess(self.guess)
                self.lines.append(line)
                print('...done')
            except Exception as err:
                print(err)
                print('WARNING. This file could not be interpreted')

    def get_data(self):
        raise NotImplementedError

    def to_csv(self):
        raise NotImplementedError


class PlatePF1(Plate):
    """12 wells times 8 lines

    Input data must look like:todo
    """
    def __init__(self, filenames, guess=None, sigma=50,  output_filename='results.csv'):
        lower_bp = 10
        upper_bp=1e6
        super(PlatePF1, self).__init__(filenames, guess, lower_bp, 
            upper_bp, sigma, output_filename)

        self.get_lines()

    def get_data(self):

        data = []
        for line in self.lines:
            for well in line.wells:
                res = well.get_peak_and_index()
                if res:
                    peak, index = res
                    data.append(well.df.ix[index])
        df = pd.DataFrame(data)
        df.reset_index(inplace=True, drop=True)
        df.drop('Peak ID', axis=1, inplace=True)
        return df

    def to_csv(self, filename="results.csv"):
        df = self.get_data()
        if filename is None:
            df.to_csv(self.output_filename, index=False)
        else:
            df.to_csv(filename, index=False)


class PlatePFGE(Plate):
    """12 wells times 8 lines
    
    Input data must look like:todo
    """
    def __init__(self, filenames, guess=None, lower_bp=150, upper_bp=5999,
            sigma=50,  output_filename='results.csv'):
        super(PlatePFGE, self).__init__(filenames, guess, lower_bp, 
            upper_bp, sigma, output_filename)

        #Molecular Weight of  dsDNA  (daltons/base Pair) (constant)
        self.mw_dna = 650 

        self.get_lines()

    def get_data(self):
        data = {'names':[],'conc':[], 'size':[] , 'amount':[]}
        for line in self.lines:
            peaks = pylab.array(line.get_peaks())
            concs = pylab.array(line.get_ng_per_ul())
            names = line.get_well_names()

            # peak and conc may be none
            #amount = conc * 1000. / (peaks*self.mw_dna/1000.)
            sigma = line.get_mad()

            for i, peak in enumerate(peaks):
                data['names'].append(names[i])

                if peak is None:
                    data['conc'].append(None)
                    data['size'].append(None)
                    data['amount'].append(None)
                elif peak + 3 * sigma < nonemedian(peaks):
                    data['conc'].append(None)
                    data['size'].append(None)
                    data['amount'].append(None)
                elif peak - 3 * sigma > nonemedian(peaks):
                    data['conc'].append(None)
                    data['size'].append(None)
                    data['amount'].append(None)
                else:
                    conc = concs[i]
                    amount = conc * 1000. / (peak*self.mw_dna/1000.)
                    data['conc'].append(conc)
                    data['size'].append(peak)
                    data['amount'].append(amount)

            # add the control
            data['names'].append('Ladder')
            data['conc'].append(None)
            data['size'].append(None)
            data['amount'].append(None)
        return data

    def to_csv(self, filename=None):
        data = self.get_data()
        df = pd.DataFrame(data)
        df = df[['names', 'conc', 'size', 'amount']]
        df.columns = ['names', 'ng/uL (QUBIT/FA)', 'Size (bp)', 'nM']
        df.index = [x+1 for x in df.index]
        if filename is None:
            df.to_csv(self.output_filename, index=False)
        else:
            df.to_csv(filename, index=False)








