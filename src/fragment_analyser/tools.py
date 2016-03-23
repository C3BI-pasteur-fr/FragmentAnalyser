#!/usr/bin/python
import numpy as np


def nonemedian(data):
    # same as numpy but handles None instead of nan
    data = [x for x in data if x is not None]
    return np.median(data)








