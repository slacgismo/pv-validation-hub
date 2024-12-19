"""
Solar-data-tools based module. This module will be uploaded by the user
and tested using the data sets accordingly. 
"""

import numpy as np
from solardatatools import DataHandler


def detect_time_shifts(
    time_series, latitude=None, longitude=None, data_sampling_frequency=None
):
    dh = DataHandler(time_series.to_frame())
    dh.run_pipeline(fix_shifts=True, verbose=False)
    estimated = np.copy(dh.time_shift_analysis.s1)
    estimated -= dh.time_shift_analysis.baseline
    estimated -= dh.tz_correction
    estimated *= -60
    return estimated
