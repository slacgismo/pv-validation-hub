# -*- coding: utf-8 -*-
"""
Post-processing results (for paper statistics + graphics)
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import rdtools


def generateDSTHeatMapPlot(time_series):
    """
    This function creates a heat map of a time series, which shows if there are
    shifts due to daylight savings time or sensor drift.
    """
    plt.figure(figsize=(7, 6))
    time_series = (time_series - time_series.min()) / (
        time_series.max() - time_series.min()
    )
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
    plt.ylabel("Time of day [0-24 hours]")
    plt.xlabel("Date")
    plt.xticks(rotation=60)
    plt.colorbar()
    plt.tight_layout()
    plt.savefig("./results/heavily-shaded-system-heatmap.png")
    plt.close()
    plt.clf()
    return


# Read in the SDT lat-lon known data
sdt_lat_lon = pd.read_csv(
    "./results/sdt-module-latlon_full_results.csv", index_col=0
)
pvwatts = pd.read_csv(
    "./results/pvwatts-5-module_full_results.csv", index_col=0
)
sdt_no_lat_lon = pd.read_csv(
    "./results/sdt-module-no-latlon_full_results.csv", index_col=0
)

pv_peak = pd.read_csv(
    "./results/pv-peak-module-matt-redo_full_results.csv", index_col=0
)

# File metadata
file_df = pd.read_csv("./data/file_metadata.csv")

sdt_lat_lon = pd.merge(
    file_df[["file_name", "number_days"]], sdt_lat_lon, on="file_name"
)

pvwatts = pd.merge(
    file_df[["file_name", "number_days"]], pvwatts, on="file_name"
)

sdt_no_lat_lon = pd.merge(
    file_df[["file_name", "number_days"]], sdt_no_lat_lon, on="file_name"
)

pv_peak = pd.merge(
    file_df[["file_name", "number_days"]], pv_peak, on="file_name"
)


# median run time statistics

print("SDT- lat-long median run time:")
print(sdt_lat_lon["run_time"].median())

print("SDT- no lat-long median run time:")
print(sdt_no_lat_lon["run_time"].median())

print("PVWatts median run time:")
print(pvwatts["run_time"].median())

print("PV Peak median run time:")
print(pv_peak["run_time"].median())


# median MAE for azimuth

print("SDT- lat-long median az MAE:")
print(sdt_lat_lon["mean_absolute_error_azimuth"].median())

print("SDT- no lat-long median az MAE:")
print(sdt_no_lat_lon["mean_absolute_error_azimuth"].median())

print("PVWatts median az MAE:")
print(pvwatts["mean_absolute_error_azimuth"].median())

print("PV Peak median az MAE:")
print(pv_peak["mean_absolute_error_azimuth"].median())

# median MAE for tilt

print("SDT- lat-long median tilt MAE:")
print(sdt_lat_lon["mean_absolute_error_tilt"].median())

print("SDT- no lat-long median tilt MAE:")
print(sdt_no_lat_lon["mean_absolute_error_tilt"].median())

print("PVWatts median tilt MAE:")
print(pvwatts["mean_absolute_error_tilt"].median())

print("PV-Peak median tilt MAE:")
print(pv_peak["mean_absolute_error_tilt"].median())

# Build out some graphics for each case
sdt_lat_lon["algorithm"] = "SDT-lat-lon known"
sdt_no_lat_lon["algorithm"] = "SDT-lat-lon unknown"
pvwatts["algorithm"] = "PVWatts-5"
pv_peak["algorithm"] = "PV-Peak"

df_master = pd.concat([sdt_lat_lon, sdt_no_lat_lon, pvwatts, pv_peak])


# Convert to subplots
plt.rcParams.update({"font.size": 18})
fig, axes = plt.subplots(3, 1)
fig.set_figheight(15)
fig.set_figwidth(8)

# Azimuth error distribution
ax0 = sns.boxplot(
    x=df_master["algorithm"],
    y=df_master["mean_absolute_error_azimuth"],
    ax=axes[0],
).set(
    title="Azimuth Absolute Error",
    ylabel="Error (degrees)",
    xlabel=None,
    xticklabels=[],
)
# Tilt error distribution
ax1 = sns.boxplot(
    y=df_master["mean_absolute_error_tilt"],
    x=df_master["algorithm"],
    ax=axes[1],
).set(
    title="Tilt Absolute Error",
    ylabel="Error (degrees)",
    xlabel=None,
    xticklabels=[],
)
# Run time distribution
sns.boxplot(y=df_master["run_time"], x=df_master["algorithm"], ax=axes[2]).set(
    title="Run Time", ylabel="Run Time (s)", xlabel=None
)
for ax in fig.axes:
    plt.sca(ax)
    plt.xticks(rotation=20)
plt.tight_layout()
# Save to a folder
plt.savefig("./results/combined-error-runtime-distribution.pdf")
plt.close()
plt.clf()


# Compare time series length to run time
plt.rcParams.update({"font.size": 18})
fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
fig.set_figheight(12)
fig.set_figwidth(8)
# SDT-lat-lon
ax1.set_title("SDT-Lat-Long Known")
sns.scatterplot(
    x=sdt_lat_lon["run_time"], y=sdt_lat_lon["number_days"], ax=ax1
)
sns.regplot(
    x=sdt_lat_lon["run_time"],
    y=sdt_lat_lon["number_days"],
    scatter=False,
    ax=ax1,
)
ax1.set_ylabel("Number days")
ax1.set_xlabel(None)
# PVWatts
ax2.set_title("PVWatts")
sns.scatterplot(x=pvwatts["run_time"], y=pvwatts["number_days"], ax=ax2).set(
    xlabel="Run Time (s)", ylabel="Number Days"
)
sns.regplot(
    x=pvwatts["run_time"], y=pvwatts["number_days"], scatter=False, ax=ax2
)
ax2.set_ylabel("Number days")
ax2.set_xlabel(None)
# PV-Peak
ax3.set_title("PV-Peak")
sns.scatterplot(x=pv_peak["run_time"], y=pv_peak["number_days"], ax=ax3).set(
    xlabel="Run Time (s)", ylabel="Number Days"
)
sns.regplot(
    x=pv_peak["run_time"], y=pv_peak["number_days"], scatter=False, ax=ax3
)
ax3.set_ylabel("Number days")
ax3.set_xlabel("Run Time (s)")
plt.tight_layout()
# Save to a folder
plt.savefig("./results/run-time-number-days-comparison.pdf")
plt.close()
plt.clf()


# Look at MAE vs data set size
# PVWatts
sns.scatterplot(
    x=pvwatts["number_days"], y=pvwatts["mean_absolute_error_tilt"]
)

plt.title("PVWatts: Absolute Error Tilt vs Number Days")
plt.ylabel("Absolute Error Tilt")
plt.xlabel("Number Days")
plt.tight_layout()
# Save to a folder
plt.savefig("./results/mae-tilt-number-days-pvwatts.pdf")
plt.close()
plt.clf()

#
sns.scatterplot(
    x=pvwatts["number_days"], y=pvwatts["mean_absolute_error_azimuth"]
)
plt.ylabel("Absolute Error Tilt")
plt.xlabel("Number Days")
plt.tight_layout()
# Save to a folder
plt.savefig("./results/mae-azimuth-number-days-pvwatts.pdf")
plt.close()
plt.clf()

# Data set issue analysis

# Soiling-azimuth
df_master.loc[df_master["issue"].isna(), "issue"] = ""
df_master["has_soiling"] = False
df_master.loc[df_master["issue"].str.contains("soiling"), "has_soiling"] = True
sns.boxplot(
    data=df_master,
    x="algorithm",
    y="mean_absolute_error_azimuth",
    hue="has_soiling",
)
plt.ylabel("Absolute Error Azimuth")
plt.xlabel("Algorithm")
plt.tight_layout()
# Save to a folder
plt.savefig("./results/mae-azimuth-soiling-detected.pdf")
plt.close()
plt.clf()

# Soiling-tilt
sns.boxplot(
    data=df_master,
    x="algorithm",
    y="mean_absolute_error_tilt",
    hue="has_soiling",
)
plt.title("Tilt Absolute Error Color-Coded by Presence of Soiling")
plt.ylabel("Absolute Error Tilt")
plt.xlabel("Algorithm")
plt.tight_layout()
# Save to a folder
plt.savefig("./results/mae-tilt-soiling-detected.pdf")
plt.close()
plt.clf()

# Clipping-azimuth
df_master.loc[df_master["issue"].isna(), "issue"] = ""
df_master["has_clipping"] = False
df_master.loc[df_master["issue"].str.contains("clipping"), "has_clipping"] = (
    True
)
sns.boxplot(
    data=df_master,
    x="algorithm",
    y="mean_absolute_error_azimuth",
    hue="has_clipping",
)
plt.ylabel("Absolute Error Azimuth")
plt.xlabel("Algorithm")
plt.tight_layout()
# Save to a folder
plt.savefig("./results/mae-azimuth-clipping-detected.pdf")
plt.close()
plt.clf()

# Clipping-tilt
sns.boxplot(
    data=df_master,
    x="algorithm",
    y="mean_absolute_error_tilt",
    hue="has_clipping",
)
plt.ylabel("Absolute Error Tilt")
plt.xlabel("Algorithm")
plt.tight_layout()
# Save to a folder
plt.savefig("./results/mae-tilt-clipping-detected.pdf")
plt.close()
plt.clf()

# Shading-azimuth
df_master.loc[df_master["issue"].isna(), "issue"] = ""
df_master["has_shading"] = False
df_master.loc[df_master["issue"].str.contains("shading"), "has_shading"] = True
sns.boxplot(
    data=df_master,
    x="algorithm",
    y="mean_absolute_error_azimuth",
    hue="has_shading",
)
plt.ylabel("Absolute Error Azimuth")
plt.xlabel("Algorithm")
plt.tight_layout()
# Save to a folder
plt.savefig("./results/mae-azimuth-shading-detected.pdf")
plt.close()
plt.clf()

# Shading-tilt
sns.boxplot(
    data=df_master,
    x="algorithm",
    y="mean_absolute_error_tilt",
    hue="has_shading",
)
plt.ylabel("Absolute Error Tilt")
plt.xlabel("Algorithm")
plt.tight_layout()
# Save to a folder
plt.savefig("./results/mae-tilt-shading-detected.pdf")
plt.close()
plt.clf()


# Isolate specific test cases for certain issues

systems_no_issues = df_master[df_master["issue"] == ""]
systems_no_issues["median_error_az"] = systems_no_issues.groupby("algorithm")[
    "mean_absolute_error_azimuth"
].transform("median")
systems_no_issues["median_error_tilt"] = systems_no_issues.groupby(
    "algorithm"
)["mean_absolute_error_tilt"].transform("median")


# Clipped system
clip_file_names = [
    "5184_ac_power_inv_3051.csv"
]  # ["5016_ac_power_inv_2100.csv","5159_ac_power_inv_2718.csv",
# "5184_ac_power_inv_3051.csv", "5226_ac_power_inv_3356.csv"]
clip_df = df_master[df_master["file_name"].isin(clip_file_names)]


# Shaded system
clip_file_names = [
    "5184_ac_power_inv_3051.csv"
]  # ["5016_ac_power_inv_2100.csv","5159_ac_power_inv_2718.csv",
# "5184_ac_power_inv_3051.csv", "5226_ac_power_inv_3356.csv"]
clip_df = df_master[df_master["file_name"].isin(clip_file_names)]


shade_file_names = ["1332_inv3_ac_power__2650.csv"]
shade_df = df_master[df_master["file_name"].isin(shade_file_names)]

# Generate a time heatmap for the system

shaded_sys = pd.read_csv(
    "./data/file_data/1332_inv3_ac_power__2650.csv",
    index_col=0,
    parse_dates=True,
)
generateDSTHeatMapPlot(shaded_sys)


# Plot a clipped system
clipped_sys = pd.read_csv(
    "./data/file_data/5184_ac_power_inv_3051.csv",
    index_col=0,
    parse_dates=True,
)

clipped_sys = (clipped_sys - clipped_sys.min()) / (
    clipped_sys.max() - clipped_sys.min()
)

time_series = clipped_sys.iloc[:, 0]
time_series = time_series.asfreq("15T")
clip_mask = rdtools.logic_clip_filter(time_series)

sns.lineplot(
    x=time_series[
        "2015-01-01 00:00:00-05:00":"2016-01-01 00:00:00-05:00"
    ].index,
    y=time_series["2015-01-01 00:00:00-05:00":"2016-01-01 00:00:00-05:00"],
)
plt.xticks(rotation=30)
plt.xlabel("Date")
plt.ylabel("Normalized Power")
plt.tight_layout()
plt.savefig("./results/clipped-system.pdf")
plt.close()
plt.clf()
