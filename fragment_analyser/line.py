#!/usr/bin/python

import numpy as np

from .tools import nonemedian

# Used to avoid issue with missing DISPLAY on the cluster.
import pylab

from .peaktable import PeakTableReader


class Line(object):
    """Class dedicated to a Line


    A line has 12 :class:`~fragment_analyser.well.Well`.

    Used by :class:`~fragment_analyser.plate.Plate`
    """
    def __init__(self, filename, sigma=50, lower_bound=120, upper_bound=6000,
                 control="Ladder", peak_mode="max"):
        """.. rubric:: constructor

        :param  peak_mode: if set to max, the peak is found based on the max
            height and the guessed peak based on median maximum across all wells. 
            if set to "concentration", the column "(% Conc)" is used to find the
            peak based on the max concentration irrespetive of other wells.


        """

        self.number = None

        ptr = PeakTableReader(filename, sigma=sigma, lower_bound=lower_bound,
                              upper_bound=upper_bound)
        self._nwells = ptr._nwells
        self.wells = ptr.wells
        self.peak_mode = peak_mode

    def guess_peak(self):
        """guess peak position

        assuming that peak is at the same position, we could estimate the
        peak position by taking the median value of the max peak across
        the 12 wells.

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
        """Return list of max peaks in the N wells"""
        if self.peak_mode == "max":
            peaks = [well.get_peak() for well in self.wells]
        else:
            peaks = [well.get_most_concentrated_peak() for well in self.wells]
            # we want the maximum; some peak are set to None 
            peaks = [x[0] if x else x for x in peaks]
        return peaks

    def get_well_names(self):
        """Return the names of all wells"""
        return [well.well_ID for well in self.wells]

    def diagnostic(self, ymax=None):
        """Shows detected peaks for each well and confidence.


        We use MAD instead of standard deviation since we may have very
        heterogenous data. If there are several types of experiments, the
        enveloppe may not have nay meaning. If we have homogenous experiments,
        then outliers may biased the estimation of the standard deviation
        significantly. We therefore use a MAD metric (see :meth:`get_mad)`.

        .. plot::
            :include-source:

            from pylab import figure
            from fragment_analyser import Line, fa_data
            l = Line(fa_data('alternate/peaktable.csv'))
            l.diagnostic()

            figure(2)
            from fragment_analyser import Line, fa_data
            l = Line(fa_data('standard_with_flat_cases/peak_table.csv'))
            l.diagnostic()

            figure(3)
            from fragment_analyser import Line, fa_data
            l = Line(fa_data('standard_mix_cases/peak_table.csv'))
            l.diagnostic()

        """
        peaks = self.get_peaks()
        names = [well.name for well in self.wells]

        pylab.clf()
        pylab.plot(peaks, 'o-', mfc='red', label="selected peak")
        pylab.axhline(self.guess_peak(), linestyle='--', lw=2, color='k', label='median')
        pylab.grid(True)
        pylab.xlabel('Wells\' names')
        pylab.ylabel('Size bp')
        pylab.xticks(range(0, self._nwells-1), names)
        pylab.ylim([0, pylab.ylim()[1]*1.4])
        pylab.xlim([-0.5, 10.5])

        peaks = pylab.array(self.get_peaks())

        # sigma is biased the presence of outliers, so we better off using the MAD
        sigma = self.get_mad()

        def nanadd(X, value):
            return [x + value if x is not None else x for x in X]

        X = []
        Y = []
        for i, peak in enumerate(peaks):
            if peak is None and len(X) == 0:
                # nothing to do. This may be the first point (len(X)==0)
                continue
            elif peak is None or (i == len(peaks)-1):
                # we ended a chunk of valid data, let us plot it
                if peak is not None:
                    X.append(i)
                    Y.append(peak)

                if len(X) == 1: # expand the window so that fill_between shows something
                    Y.append(Y[0])
                    X = [X[0]-0.5, X[0]+0.5]
                else:
                    X.insert(0, X[0]-0.5)
                    X.append(X[-1] + 0.5)
                    Y.append(Y[-1])
                    Y.insert(0, Y[0])

                X = np.array(X)
                Y = np.array(Y)

                pylab.fill_between(X, nanadd(Y, -sigma * 3), nanadd(Y, sigma * 3),
                                   color='red', alpha=0.5)
                pylab.fill_between(X, nanadd(Y, -sigma * 2), nanadd(Y, sigma * 2),
                               color='orange', alpha=0.5)
                pylab.fill_between(X, nanadd(Y, -sigma), nanadd(Y, sigma),
                               color='green', alpha=0.5)
                X = []
                Y = []
            else:
                # we are sliding inside a contiguous chunk
                X.append(i)
                Y.append(peak)

        pylab.legend()

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






