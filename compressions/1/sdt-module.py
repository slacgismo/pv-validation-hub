"""
Solar-data-tools based module. This module will be uploaded by the user
and tested using the data sets accordingly. 
"""

import numpy as np
from solardatatools import DataHandler

def detect_time_shifts(time_series):
    """
    

    Returns
    -------
    None.

    """
    dh = DataHandler(time_series)
    dh.run_pipeline(fix_shifts=True) 
    estimated = np.copy(dh.time_shift_analysis.s1)
    estimated -= estimated[0]
    estimated -= dh.tz_correction
    estimated *= -60
    return estimated