"""

"""
from .line import Line
from .well import Well
from .plate import Plate
from .peaktable import PeakTableReader

import pkg_resources
import easydev

# Avoid display issue on the IP cluster
import matplotlib
matplotlib.use('Agg')


try:
    version = pkg_resources.require("fragment_analyser")[0].version
    __version__ = version
except:
    # update this manually is possible when the version in the
    # setup changes
    version = "?"


def fa_data(filename=None, where=None):
    """retrieve data set path from fragment_analyser/data dir"""
    import os
    import easydev
    import glob
    fa_path = easydev.get_package_location('fragment_analyser')
    sharedir = os.sep.join([fa_path , "fragment_analyser", 'data'])
    filename = sharedir + os.sep + filename
    if os.path.exists(filename) is False:
        raise Exception('unknown file %s' % filename)
    return filename
