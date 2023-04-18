"""
PVAnalytics-CPD based module. This module will be uploaded by the user
and tested using the data sets accordingly. 
"""

import pandas as pd
from pvanalytics.features import daytime
from pvanalytics.quality.outliers import zscore
from pvanalytics.quality import gaps
import pvlib
import ruptures as rpt
import numpy as np

def get_sunrise_sunset_timestamps(time_series, daytime_mask):
    """
    Get the timestamp for sunrise/sunset for the time series.
    
    Parameters 
    ----------
    time_series: Pandas datetime series of measured data (can be irradiance,
                                                          power, or energy)
    daytime_mask: Pandas series of boolean masks for day/night periods.
        Same datetime index as time_series object.
    
    Returns
    ---------
    sunrise_series: Pandas series of the sunrise 
        datetimes for each day in the time series.
    sunset_series: Pandas series of the sunset
        datetimes for each day in the time series.
    midday_series: Pandas series of the midway 
        point datetimes (halfway between sunrise and sunset) for each day in 
        the time series.
    """
    day_night_changes = daytime_mask.groupby(
        daytime_mask.index.date).apply(lambda x: x.ne(x.shift().ffill()))
    #Get the first 'day' mask for each day in the series; proxy for sunrise
    sunrise_series = pd.Series(daytime_mask[(daytime_mask) &
                                            (day_night_changes)].index)
    sunrise_series = pd.Series(sunrise_series.groupby(sunrise_series.dt.date).min(),
                              index= sunrise_series.dt.date).drop_duplicates()
    # Get the sunset value for each day; this is the first nighttime period
    # after sunrise  
    sunset_series = pd.Series(daytime_mask[~(daytime_mask) & (day_night_changes)].index)
    sunset_series = pd.Series(sunset_series.groupby(sunset_series.dt.date).max(),
                              index= sunset_series.dt.date).drop_duplicates()
    # Generate a 'midday' series, which is the midpoint between sunrise
    # and sunset for every day in the data set
    midday_series = sunrise_series + ((sunset_series - sunrise_series)/2)
    #Return the pandas series associated with the sunrise, sunset, and midday points
    return sunrise_series, sunset_series, midday_series 

def time_shift_estimation(midday_diff_series,
                          cpd_penalty=20,
                          min_window_size=15,
                          bottom_quantile_threshold=.5,
                          top_quantile_threshold=1,
                          minute_rounding=15):
    """
    Run denoising-CPD combo algorithm on the midday time series.
    """
    midday_diff_series = midday_diff_series.dropna()
    prediction_series=midday_diff_series
    model = "rbf"
    algo = rpt.Binseg(model=model, min_size=min_window_size).fit(
        np.array(prediction_series))
    bkps = algo.predict(pen=cpd_penalty)
    if len(midday_diff_series) in bkps:
        bkps.remove(len(midday_diff_series))
    # Return a list of dates where changepoints are detected
    mask = pd.Series(False, index=pd.Series(np.array(prediction_series)).index)
    mask.iloc[bkps] = True
    mask.index = prediction_series.index
    # Calculate the mean for each segment
    mask_bkps = list(mask[mask == True].index)
    # Append the first and last index to list
    mask_bkps = [mask.index.min()] + mask_bkps + [mask.index.max()]
    prediction_series_mean = prediction_series.copy()
    for index in range(len(mask_bkps) - 1):
        idx_start = mask_bkps[index]
        idx_end = mask_bkps[index + 1]
        segment = prediction_series[idx_start: idx_end]
        zscore_outlier_mask = zscore(segment, zmax=2,
                                      nan_policy='omit')
        segment = segment[~zscore_outlier_mask]
        quantile_cutoff = segment.quantile([bottom_quantile_threshold,
                                            top_quantile_threshold])
        segment = segment[(segment>=quantile_cutoff.iloc[0]) &
                         (segment<=quantile_cutoff.iloc[1])]
        # Now take the mean of the segment
        mean_value = segment.mean()
        prediction_series_mean.loc[idx_start: idx_end] = minute_rounding * round(
            float(mean_value)/minute_rounding)            
    return prediction_series_mean
    
def detect_time_shifts(time_series,
                       latitude, longitude,
                       data_sampling_frequency):
    """
    Master function for testing for time shifts in a series and returning
    time-shifted periods
    
    """
    # Save the dates of the time series index for reindexing at the end
    date_index = pd.Series(time_series.index.date).drop_duplicates()
    # Data pre-processing:
    # 1) Removal of frozen/stuck data
    # 2) Removal of data periods with low data 'completeness'
    # 3) Removal of negative data
    # 4) Removal of outliers via Hampel + outlier filter
    # Trim based on frozen data values
    stale_data_mask = gaps.stale_values_diff(time_series)
    time_series = time_series[~stale_data_mask]
    time_series = time_series.asfreq(str(data_sampling_frequency) + 'T')
    # Remove negative data
    time_series = time_series[(time_series >= 0) | (time_series.isna())]
    time_series = time_series.asfreq(str(data_sampling_frequency) + 'T')
    # Remove any outliers via z-score filter
    zscore_outlier_mask = zscore(time_series, zmax=2,
                                 nan_policy='omit')
    time_series = time_series[(~zscore_outlier_mask)]
    time_series = time_series.asfreq(str(data_sampling_frequency) + 'T')
    # Remove any incomplete days (less than 33% data)
    completeness = gaps.complete(time_series,
                                minimum_completeness=0.33)
    time_series = time_series[completeness]
    time_series = time_series.asfreq(str(data_sampling_frequency) + 'T')
    if len(time_series) > 0:
        # Calculate a nighttime offset 
        # Mask daytime periods for the time series
        daytime_mask = daytime.power_or_irradiance(time_series,
                                                   freq=str(data_sampling_frequency) + 'T',
                                                   low_value_threshold=.005)
        # Get the modeled sunrise and sunset time series based on the system's
        # latitude-longitude coordinates
        modeled_sunrise_sunset_df = pvlib.solarposition.sun_rise_set_transit_spa(
            time_series.index,
            latitude, longitude)
        modeled_sunrise_sunset_df.index = modeled_sunrise_sunset_df.index.date
        modeled_sunrise_sunset_df = modeled_sunrise_sunset_df.drop_duplicates()
        # Calculate the midday point between sunrise and sunset for each day
        # in the modeled irradiance series
        modeled_midday_series = modeled_sunrise_sunset_df['sunrise'] + \
                                (modeled_sunrise_sunset_df['sunset'] - \
                                 modeled_sunrise_sunset_df['sunrise']) / 2
        #Generate the sunrise, sunset, and halfway pts for the data stream
        sunrise_series, sunset_series, midday_series = get_sunrise_sunset_timestamps(time_series,
                                                                                     daytime_mask)
        #Compare the data stream's daily halfway point to the modeled halfway point
        midday_diff_series = (modeled_midday_series - 
                              midday_series).dt.total_seconds() / 60
        # Run a secondary z-score outlier filter to clean up the midday series
        zscore_outlier_mask = zscore(midday_diff_series, zmax=3,
                                     nan_policy='omit')
        midday_diff_series = midday_diff_series[~zscore_outlier_mask]
        midday_diff_series = midday_diff_series.dropna().dropna()
        time_shift_series = time_shift_estimation(midday_diff_series)
        time_shift_series = time_shift_series.reindex(date_index)\
            .ffill().bfill()
        return time_shift_series
    else:
        return pd.Series(0, index=date_index)