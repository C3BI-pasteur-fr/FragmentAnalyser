"""

"""
from .line import Line
from .well import Well
from .plate import Plate, PlatePF1, PlatePFGE
from .peaktable import PeakTableReader



# TODO a get data file ?

def fa_data(filename, where=None):
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
    if where:
        filename = os.sep.join([share, where, filename])
    else:
        filename = os.sep.join([share, filename])
    if os.path.exists(filename) is False:
        raise Exception('unknown file %s' % filename)
    return filename
