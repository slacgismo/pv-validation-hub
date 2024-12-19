"""
PVWatts-based model submission.
"""

import pvlib
import pandas as pd
from pvanalytics import system
from pvanalytics.quality import gaps
from pvanalytics.quality import data_shifts as ds
from pvanalytics.quality.outliers import hampel, zscore
import numpy as np
import rdtools


def estimate_az_tilt(time_series, latitude, longitude):
    """
    Estimate the azimuth and tilt of a system based on its time series data,
    using the PVAnalytics PVWatts-based method.

    Parameters
    ----------
    time_series : Pandas series
        Time series of an AC power stream associated with the system.
    latitude: Float.
        Latitude coordinate of the site.

    longitude: Float.
        Longitude coordinate of the site.

    Returns
    -------
    azimuth: Float.
        Predicted azimuth value.
    tilt: Float.
        Predicted tilt value.

    """
    psm3s = []
    years = list(time_series.index.year.drop_duplicates())
    years = [x for x in years if x < 2021]
    for year in years:
        psm3 = None
        try:
            # connect
            psm3, _ = pvlib.iotools.get_psm3(
                latitude,
                longitude,
                "4z5fRAXbGB3qldVVd3c6WH5CuhtY5mhgC2DyD952",
                "kirsten.perry@nrel.gov",
                year,
                attributes=[
                    "air_temperature",
                    "ghi",
                    "clearsky_ghi",
                    "clearsky_dni",
                    "clearsky_dhi",
                ],
                map_variables=True,
                interval=30,
                leap_day=True,
            )
        except Exception as e:
            print(e)
        psm3s.append(psm3)
    psm3 = pd.concat(psm3s)
    psm3 = psm3.reindex(
        pd.date_range(psm3.index[0], psm3.index[-1], freq="15T")
    ).interpolate()
    psm3 = psm3.reindex(time_series.index)
    # psm3[(psm3.index.year == year) | (psm3.index.year == year+1)]
    psm3_sub = psm3
    is_clear = psm3_sub.ghi_clear == psm3_sub.ghi
    is_daytime = psm3_sub.ghi > 0
    # Run the associated data-cleaning routines on the time series:
    # 1) Data shift detection + removal
    # 2) Removal of frozen/stuck data
    # 3) Removal of data periods with low data 'completeness'
    # 4) Removal of negative data
    # 5) Removal of outliers via Hampel + outlier filter
    # 6) Removal of clipped values via clipping filter
    # 7) Filter to clearsky data only, as determined by PSM3
    # try:
    # Detect any data shifts and remove them
    time_series_daily = time_series.resample("D").sum()
    start_date, end_date = ds.get_longest_shift_segment_dates(
        time_series_daily
    )
    time_series = time_series[start_date:end_date]
    # Trim based on frozen data values
    stale_data_mask = gaps.stale_values_diff(time_series)
    time_series = time_series.asfreq("15T")
    time_series = time_series[~stale_data_mask]
    time_series = time_series.asfreq("15T")
    # Remove negative data
    time_series = time_series[(time_series >= 0) | (time_series.isna())]
    time_series = time_series.asfreq("15T")
    # Remove any outliers via Hampel and z-score filters
    hampel_outlier_mask = hampel(time_series, window=5)
    zscore_outlier_mask = zscore(time_series, zmax=2, nan_policy="omit")
    time_series = time_series[(~hampel_outlier_mask) & (~zscore_outlier_mask)]
    time_series = time_series.asfreq("15T")
    # Apply clipping filter from Rdtools.
    clip_mask = rdtools.logic_clip_filter(time_series)
    time_series = time_series[clip_mask]
    # Reindex the time series after all of the filtering so it
    # has the same index as PSM3
    time_series = time_series.reindex(is_clear.index)
    # Trim based on clearsky values
    time_series_clearsky = time_series[(is_clear) & (is_daytime)]
    # Remove any incomplete days (less than 25% data)
    time_series_clearsky = time_series_clearsky.asfreq("15T")
    completeness = gaps.complete(
        time_series_clearsky, minimum_completeness=0.25
    )
    time_series_clearsky = time_series_clearsky[completeness]
    # Get the peak value for each day, and if it's less than 25% of the
    # monthly average peak value, then throw it out
    daily_max = time_series_clearsky.groupby(
        time_series_clearsky.index.date
    ).transform("max")
    average_max_day_month = daily_max.groupby(
        time_series_clearsky.index.month
    ).transform("median")
    time_series_clearsky = time_series_clearsky[
        daily_max > 0.25 * average_max_day_month
    ]
    time_series_clearsky = time_series_clearsky.dropna()
    # Get the clearsky data
    psm3_clearsky = psm3.loc[time_series_clearsky.index]
    solpos_clearsky = pvlib.solarposition.get_solarposition(
        time_series_clearsky.index, latitude, longitude
    )
    # Run PVWatts estimator
    best_tilt, best_azimuth, r2 = system.infer_orientation_fit_pvwatts(
        time_series_clearsky,
        psm3_clearsky.ghi_clear,
        psm3_clearsky.dhi_clear,
        psm3_clearsky.dni_clear,
        solpos_clearsky.zenith,
        solpos_clearsky.azimuth,
        temperature=psm3_clearsky.temp_air,
        azimuth_min=85,
        azimuth_max=275,
    )
    return best_azimuth, best_tilt


if __name__ == "__main__":
    # Test the function
    print("Reading data")
    file_name = "1332_inv_total_ac_power__2654.csv"

    time_series = pd.read_csv(file_name, index_col=0, parse_dates=True)
    print(time_series.head())

    time_series = time_series.asfreq("15min").squeeze()

    print(time_series.head())
    print("Estimating azimuth and tilt...")
    results = estimate_az_tilt(
        time_series, latitude=40.0150, longitude=-105.2705
    )
    print(results)
