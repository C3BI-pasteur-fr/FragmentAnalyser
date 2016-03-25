"""

"""
from .line import Line
from .well import Well
from .plate import Plate
from .peaktable import PeakTableReader

import pkg_resources
import easydev

try:
    version = pkg_resources.require("fragment_analyser")[0].version
    __version__ = version
except:
    # update this manually is possible when the version in the
    # setup changes
    version = "?"


# TODO a get data file ?

def fa_data(filename):
    """Retrieve data set pathname from fragment_analyser/share directory

    ::

        >>> fa_data("standard_mix_cases/peak_table.csv")
        /home/user/path_to_fa/share/data/standard_mix_cases/peak_table.csv'

    """
    import os
    import easydev
    share = easydev.get_shared_directory_path('fragment_analyser')
    share = os.sep.join([share, 'data'])
    # in the code one may use / or \
    filename = os.sep.join([share, filename])
    if os.path.exists(filename) is False:
        raise Exception('unknown file %s' % filename)
    return filename
