#!/usr/bin/python
import pylab


# a data structure to handle the Well with a given sample 
class Well(object):
    """Hold data related to a single well

    Most of the time, there is a strong peak at :math:`X=1` and :math:`X=6000`.
    You may then have 1 to N other peaks.

    The goal is to find the relevant peak corresponding to the sample.

    Usually, the peak is around a given :math:`X_0` position but other strong peaks
    may be present, making the automatic detection difficult.

    We therefore multiply the data by a weight function, which is
    a gaussian distribution centered around the expected position (:math:`X_0`)
    and sigma provided as parameters (default to 50).

    Value outside the range [lower_bound, upper_bound] are removed.

    In addition to the original data, a column called **amount** is
    added and is computed as

    .. math::

        (C / 1000) / (X  * MV / 1000)

    with :math:`X` the **Size (bp)** column, :math:`C`  the **ng/ul** column
    and MV a constant set to 650 (daltons per base pair).
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
        """Get the position of the peak with maximum height

        :return: nothing if no peaks found in the valid range otherwise
            returns peak position (in bp) and the index within the dataframe
            :attr:`df`.
        """
        df = self.df.copy()
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
        """Returns peak position if found (otherwise None)"""
        try:
            # get_peak_and_index may return None
            maximum, index = self.get_peak_and_index()
            return maximum
        except:
            return None

    def plot(self, marker='o', color='red', m=0, M=6000):
        """Plots the position / height of the peaks in the well

        .. plot::
            :include-source:

            from fragment_analyser import Line, fa_data
            l = Line(fa_data("alternate/peaktable.csv"))
            well = l.wells[0]
            well.plot()

        """
        x = self.df['Size (bp)'].astype(float).values
        y = self.df['RFU'].astype(float).values
        if len(x) == 0:
            print("Nothing to plot (no peaks)")
            return
        pylab.stem(x, y, marker=marker, color=color)
        pylab.semilogx()
        pylab.xlim([1, M])
        pylab.ylim([0, max(y)*1.2])
        pylab.grid(True)
        return x, y