#!/usr/bin/python
import pylab


# a data structure to handle the Well with a given sample 
class Well(object):
    """Class dedicated to a well



    In addition to the original data, those columns are added for convenience:

    let us denote X = Size (bp) and C = ng/ul column

    - amount = (C / 1000) / (X [bp] * mv [daltons/bp] / 1000)
    so amount is in ng/ul ?

    where mw = 650 (daltons per base pair)
    """
    def __init__(self, data, sigma=50, lower_bound=120, upper_bound=6000):
        """.. rubric:: Constructor

        """
        self.df = data.copy()
        self.name = data['Well'].unique()[0]
        self.well_ID = data['Sample ID'].unique()[0]

        # !! data may be empty once the 0 and 6000 controls are removed
        #print("Filtering out values <= %s or >= %s" % (lower_bound, upper_bound))
        mask = data['Size (bp)'].apply(lambda x: x>lower_bound and x<upper_bound)
        self.df = self.df[mask]

        self.tic = None
        self.tim = None
        self.total_concentration = None
        self.guess = None
        self.lower_bp_filter = lower_bound
        self.sigma = sigma

        #Compute a new quantity once for all
        # Molecular Weight of  dsDNA  (daltons/base Pair) (constant)
        self.mw_dna = 650

        concs = self.df['ng/ul'].values
        peaks = self.df["Size (bp)"]
        self.df['amount (nM)'] = concs * 1000. / (peaks * self.mw_dna / 1000.)

        # we re-arrange some data for the user convenience
        # swap those two columns: u'RFU', u'Avg. Size' to have the order:
        # ng/ul - Avg Size and RFU
        columns = list(self.df.columns)
        i1 = columns.index('RFU')
        i2 = columns.index('Avg. Size')
        columns[i2], columns[i1] = columns[i1], columns[i2]
        self.df = self.df.loc[:, columns]


    def get_peak_and_index(self):
        df = self.df.copy()
        #mask = df['Size (bp)'].astype(float) > self.lower_bp_filter
        #df = df[mask]

        if len(df) == 0:
            return None

        positions = df['Size (bp)'].astype(float)

        data = df['RFU'].copy()

        # this need to be cast into float
        data = data.astype(float)

        naive_max = data.max()
        index = data.argmax()

        if self.guess is None:
            pass
        else:
            weighted_data = pylab.exp(-0.5*( (self.guess - positions.values) /
                self.sigma)**2)
            data = data * weighted_data
            index = data.argmax()

        peak_pos = float(df['Size (bp)'].ix[index])
        return peak_pos, index

    def get_peak(self):
        try:
            # get_peak_and_index may return None
            maximum, index = self.get_peak_and_index()
            return maximum
        except:
            return None

    def get_ng_per_ul(self):
        try:
            maximum, index = self.get_peak_and_index()
            return float(self.df.ix[index]['ng/ul'])
        except:
            return None

    def get_mw(self, constant=650):
        try:
            return self.get_peak() * constant / 1000.
        except:
            return None

    def plot(self, marker='o', color='red', m=0, M=6000):
        x = self.df['Size (bp)'].astype(float).values
        y = self.df['RFU'].astype(float).values
        if len(x) == 0:
            print("Nothing to plot (no peaks)")
            return
        pylab.stem(x, y, marker=marker, color=color)
        pylab.xlim([m, M])
        pylab.ylim([0, max(y)*1.2])
        pylab.grid(True)
        return x, y