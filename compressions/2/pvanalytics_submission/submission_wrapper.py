"""
PVAnalytics-CPD based module. This module will be uploaded by the user
and tested using the data sets accordingly. 
"""

import pandas as pd
from pvanalytics.quality.time import shifts_ruptures
from pvanalytics.features import daytime
from pvanalytics.quality.outliers import zscore
from pvanalytics.quality import gaps
import pvlib
import matplotlib.pyplot as plt
import pvanalytics
import ruptures
    
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
    # REMOVE STALE DATA (that isn't during nighttime periods)
    # Day/night mask
    daytime_mask = daytime.power_or_irradiance(time_series)
    # Stale data mask
    stale_data_mask = gaps.stale_values_round(time_series,
                                              window=3,
                                              decimals=2)
    stale_data_mask = stale_data_mask & daytime_mask
    
    # REMOVE NEGATIVE DATA
    negative_mask = (time_series < 0)
    
    # FIND ABNORMAL PERIODS
    daily_min = time_series.resample('D').min()
    series_min = 0.1 * time_series.mean()
    erroneous_mask = (daily_min >= series_min)
    erroneous_mask = erroneous_mask.reindex(index=time_series.index,
                                            method='ffill',
                                            fill_value=False)
    # FIND OUTLIERS (Z-SCORE FILTER)
    zscore_outlier_mask = zscore(time_series, zmax=3.5,
                                 nan_policy='omit')
    
    # Filter the time series, taking out all of the issues
    issue_mask = ((~stale_data_mask) & (~negative_mask) &
                  (~erroneous_mask) & (~zscore_outlier_mask))
    
    time_series = time_series[issue_mask]
    time_series = time_series.asfreq(str(data_sampling_frequency) + 'T')
    # Data completeness
    # Trim the series based on daily completeness score
    trim_series_mask = pvanalytics.quality.gaps.trim_incomplete(time_series,
                                                                minimum_completeness=.25,
                                                                freq=str(data_sampling_frequency) + 'T')

    time_series = time_series[trim_series_mask]
    if len(time_series) > 0:
        # Calculate a nighttime offset 
        # Mask daytime periods for the time series
        daytime_mask = daytime.power_or_irradiance(time_series,
                                                   freq=str(data_sampling_frequency) + 'T',
                                                   low_value_threshold=.005)
        # Get the modeled sunrise and sunset time series based on the system's
        # latitude-longitude coordinates
        modeled_sunrise_sunset_df = pvlib.solarposition.sun_rise_set_transit_spa(
            time_series.index, latitude, longitude)
        
        # Calculate the midday point between sunrise and sunset for each day
        # in the modeled irradiance series
        modeled_midday_series = modeled_sunrise_sunset_df['sunrise'] + \
            (modeled_sunrise_sunset_df['sunset'] -
             modeled_sunrise_sunset_df['sunrise']) / 2

        #Generate the sunrise, sunset, and halfway pts for the data stream
        sunrise_series = daytime.get_sunrise(daytime_mask)
        sunset_series = daytime.get_sunset(daytime_mask)
        midday_series = sunrise_series + ((sunset_series - sunrise_series)/2)
        # Convert the midday and modeled midday series to daily values
        midday_series_daily, modeled_midday_series_daily = (
            midday_series.resample('D').mean(),
            modeled_midday_series.resample('D').mean())
        
        # Set midday value series as minutes since midnight, from midday datetime
        # values
        midday_series_daily = (midday_series_daily.dt.hour * 60 +
                               midday_series_daily.dt.minute +
                               midday_series_daily.dt.second / 60)
        modeled_midday_series_daily = \
            (modeled_midday_series_daily.dt.hour * 60 +
             modeled_midday_series_daily.dt.minute +
             modeled_midday_series_daily.dt.second / 60)
        
        # Estimate the time shifts by comparing the modelled midday point to the
        # measured midday point.
        is_shifted, time_shift_series = shifts_ruptures(midday_series_daily,
                                                        modeled_midday_series_daily,
                                                        period_min=15,
                                                        shift_min=15,
                                                        zscore_cutoff=.75)
        time_shift_series = -1 * time_shift_series
        
        # Create a midday difference series between modeled and measured midday, to
        # visualize time shifts. First, resample each time series to daily frequency,
        # and compare the data stream's daily halfway point to the modeled halfway
        # point
        midday_diff_series = (modeled_midday_series.resample('D').mean() -
                              midday_series.resample('D').mean()
                              ).dt.total_seconds() / 60
        
        midday_diff_series.plot()
        time_shift_series.plot()
        plt.show()
        plt.close()
        time_shift_series.index = time_shift_series.index.date
        return time_shift_series
    else:
        return pd.Series(0, index=date_index)