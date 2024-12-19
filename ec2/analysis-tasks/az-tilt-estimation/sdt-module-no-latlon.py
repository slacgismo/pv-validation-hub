"""
PVWatts-based model submission.
"""

import pvlib
import pandas as pd
from solardatatools import DataHandler
from pvsystemprofiler.estimator import ConfigurationEstimator

# Suppress warnings here (just because we've already fixed script up)
import warnings

warnings.filterwarnings("ignore")


def estimate_az_tilt(time_series):
    df = time_series.to_frame(name="power")
    dh = DataHandler(df)
    dh.run_pipeline(verbose=False)
    ts = time_series.index[0]
    tz_offset = int(str(ts)[-6:-3])
    est = ConfigurationEstimator(dh, gmt_offset=int(tz_offset))
    est.estimate_orientation()
    return est.azimuth + 180, est.tilt
