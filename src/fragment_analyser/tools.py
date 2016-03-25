#!/usr/bin/python
import numpy as np


def nonemedian(data):
    """simple utility to compute median in a list with None values"""
    # same as numpy but handles None instead of nan
    data = [x for x in data if x is not None]
    return np.median(data)


def get_mad(data):
    mad = nonemedian(abs(data - nonemedian(data)))
    return mad





