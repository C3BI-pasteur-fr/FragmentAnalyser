#!/usr/bin/python

import pylab


# a data structure to handle the Well with a given sample 
class Well(object):
    """Class dedicated to a well


    """
    def __init__(self, name, wellID, data, sigma=50):
        """.. rubric:: Constructor

        """
        self.df = data
        self.name = name
        self.wellID = wellID
        self.tic = None
        self.tim = None
        self.total_concentration = None
        self.guess = None
        self.lower_bp_filter = 120
        self.sigma = sigma

    def get_peak_and_index(self):
        df = self.df.copy()
        mask = df['Size (bp)'].astype(float) > self.lower_bp_filter
        df = df[mask]

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
            weighted_data = pylab.exp(-0.5*( (self.guess-positions.values) /
                self.sigma)**2)
            data = data * weighted_data
            # check it is unique 
            subdata = data
            #if len(subdata) == 1:
            #    found_max = subdata.values[0]
            #    index = subdata.index[0]
            #else:
            #    found_max = naive_max
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

    def plot(self, marker='o', color='red'):
        x = self.df['Size (bp)'].astype(float).values
        y = self.df['RFU'].astype(float).values
        pylab.plot(x, y, marker=marker, color=color)



