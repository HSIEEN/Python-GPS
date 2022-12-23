# Data : 12/22/2022 5:46 PM
# Author: Shawn Shi
# Right Reserved By COROS
import numpy as np


def shift_count(std, track):
    mstd = np.average(std, axis=0)
    mtrk = np.average(track, axis=0)
    shift = mstd - mtrk
    return shift
