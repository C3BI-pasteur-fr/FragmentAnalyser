#!/usr/bin/python

import numpy as np

from .tools import nonemedian

# Used to avoid issue with missing DISPLAY on the cluster.
import matplotlib
matplotlib.use('Agg')
import pylab



class Line(object):
    """Class dedicated to a Line

    A line has 12 :class:`Well`.

    """
    def __init__(self):
        self.wells = []
        self.number = None
        self.number_wells = 12

    def append(self, well):
        self.wells.append(well)

    def guess_peak(self):
        """guess peak position

        assuming that peak is at the same position, we could estimate the
        peak position by taking the median value across the 12 wells.

        None values are ignored if any.

        """
        peaks = self.get_peaks()
        guess = nonemedian(peaks)
        return guess

    def set_guess(self, guess=None):
        if guess is None:
            guess = self.guess_peak()
        for well in self.wells:
            well.guess = guess

    def get_peaks(self):
        peaks = [well.get_peak() for well in self.wells]
        return peaks

    def get_well_names(self):
        return [well.wellID for well in self.wells]

    def get_ng_per_ul(self):
        return [well.get_ng_per_ul() for well in self.wells]

    def diagnostic(self):
        """Shows detected peaks for each well and confidence at 1,2,3
        MAD value


        """
        peaks = [well.get_peak() for well in self.wells]
        names = [well.name for well in self.wells]

        pylab.clf()
        pylab.plot(peaks, 'o-', mfc='red')
        pylab.axhline(self.guess_peak(), linestyle='--', lw=2, color='k')
        pylab.grid(True)
        pylab.xlabel('names')
        pylab.ylabel('Size bp')
        pylab.xticks(range(0, self.number_wells-1), names)
        pylab.ylim([0, pylab.ylim()[1]*1.2])
        pylab.xlim([-0.5, 10.5])

        peaks = pylab.array(self.get_peaks())
        sigma = pylab.std([x for x in peaks if x is not None])
        X = [i for i,x in enumerate(peaks) if x is not None]
        peaks = np.array([x for x in peaks if x is not None])

        # sigma is biased the presence of outliers, so we better off using the MAD
        sigma = self.get_mad()

        pylab.fill_between(X, peaks-sigma*3, peaks+sigma*3, color='red',
                           alpha=0.5)
        pylab.fill_between(X, peaks-sigma*2, peaks+sigma*2, color='orange',
                           alpha=0.5)
        pylab.fill_between(X, peaks-sigma, peaks+sigma, color='green',
                           alpha=0.5)

    def get_mad(self, minimum=25):
        # The crux of the problem is that the standard deviation is based on squared distances, 
        # so extreme points are much more influential than those close to the mean.
        # A good candidate is the median absolute deviation from median, commonly shortened to 
        # the median absolute deviation (MAD). It is the median of the set comprising the absolute 
        #values of the differences between the median and each data point
        peaks = pylab.array(self.get_peaks())

        # we may have None in the list of peaks
        peaks = [x for x in peaks if x is not None]

        sigma = nonemedian(abs(peaks - nonemedian(peaks)))

        if sigma < minimum:
            sigma = minimum
        return sigma






