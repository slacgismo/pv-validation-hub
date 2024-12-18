"""
Generated unfiltered plots so we can identify issues: clipping, capacity shifts, etc.
"""

import glob
import pandas as pd
import pvlib
from pvanalytics import system
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
from pvanalytics.quality import gaps
from pvanalytics.quality import data_shifts as ds
import matplotlib.pyplot as plt
from pvanalytics.quality.outliers import hampel, zscore, tukey
import rdtools
import plotly.express as px


def generateDSTHeatMapPlot(
    time_series, time_series_name, system_id, heatmap_file_path
):
    """
    This function creates a heat map of a time series, which shows if there are
    shifts due to daylight savings time or sensor drift.
    """
    plt.figure()
    # Get time of day from the associated datetime column
    time_of_day = pd.Series(
        time_series.index.hour + time_series.index.minute / 60,
        index=time_series.index,
    )
    # Pivot the dataframe
    dataframe = pd.DataFrame(pd.concat([time_series, time_of_day], axis=1))
    dataframe.columns = ["values", "time_of_day"]
    dataframe = dataframe.dropna()
    dataframe_pivoted = dataframe.pivot_table(
        index="time_of_day", columns=dataframe.index, values="values"
    )
    plt.pcolormesh(
        dataframe_pivoted.columns,
        dataframe_pivoted.index,
        dataframe_pivoted,
        shading="auto",
    )
    plt.ylabel("Time of day [0-24]")
    plt.xlabel("Date")
    plt.xticks(rotation=60)
    plt.title("Datetime signal - " + str(system_id) + " - " + time_series_name)
    plt.colorbar()
    plt.tight_layout()
    plt.savefig(heatmap_file_path)
    plt.clf()
    plt.close("all")
    return


stream_files = glob.glob(
    "C:/Users/kperry/Documents/source/repos/az-tilt-estimation-validation/data/file_data/*.csv"
)
sys_meta = pd.read_csv(
    "C:/Users/kperry/Documents/source/repos/az-tilt-estimation-validation/data/system_metadata.csv"
)
master_pred_df = pd.DataFrame(
    columns=[
        "system_id",
        "year",
        "data_stream",
        "predicted_azimuth",
        "predicted_tilt",
        "actual_azimuth",
        "actual_tilt",
    ]
)
# pd.read_csv("./results_new/pvwatts_model_resultsv2.csv",index_col=0)

file_linker_list = list()
master_predictions = list()
for file in stream_files:
    if file.split("\\")[-1].split(".csv")[0] not in list(
        master_pred_df["data_stream"]
    ):
        df = pd.read_csv(file, index_col=0, parse_dates=True)
        # Get the associated system details
        sys = int(file.split("\\")[-1].split("_")[0])
        stream = file.split("\\")[-1].split(".csv")[0]
        time_series = df.iloc[:, 0]
        # Detect any data shifts and remove them
        time_series_daily = time_series.resample("D").sum()
        shift_mask = ds.detect_data_shifts(time_series_daily)
        shift_list = list(time_series_daily[shift_mask].index)
        # Apply clipping filter from Rdtools.
        time_series = time_series.asfreq("15T")
        clip_mask = rdtools.logic_clip_filter(time_series)
        # # Heatmap
        # heatmap_file_path = "C:/Users/kperry/Documents/source/repos/az-tilt-estimation-validation/plots_unfiltered/" + stream + ".png"
        # generateDSTHeatMapPlot(time_series,
        #                        time_series.name,
        #                        sys,
        #                        heatmap_file_path)
        # Plot it
        fig = px.scatter(x=time_series.index, y=time_series, color=clip_mask)
        for shift in shift_list:
            fig.add_hline(y=shift)
        fig.write_html(
            "C:/Users/kperry/Documents/source/repos/az-tilt-estimation-validation/plots_unfiltered/"
            + stream
            + ".html"
        )
