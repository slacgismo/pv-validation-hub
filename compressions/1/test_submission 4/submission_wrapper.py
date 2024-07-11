import numpy as np
from solardatatools import DataHandler

def detect_time_shifts(time_series,
                       latitude=None, longitude=None,
                       data_sampling_frequency=None):
    dh = DataHandler(time_series.to_frame())
    dh.run_pipeline(fix_shifts=True, verbose=False, round_shifts_to_hour=False)
    return dh.time_shift_analysis.correction_estimate
