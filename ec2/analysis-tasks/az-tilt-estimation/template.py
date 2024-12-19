"""
Az-tilt Marimo prototype.
"""

import marimo

__generated_with = "0.1.18"
app = marimo.App()


@app.cell
def __(mo):
    mo.md("# Private Report: Azimuth-Tilt Results")
    return


@app.cell
def __(create_df_from_cli_args, generatePlots):
    results_df = create_df_from_cli_args()
    plotting = generatePlots(results_df)
    return plotting, results_df


@app.cell
def __(plotting, mo):
    if plotting is not None:
        median_run_time = round(plotting.results_df.run_time.median(), 2)
        mean_run_time = round(plotting.results_df.run_time.mean(), 2)
        max_run_time = round(plotting.results_df.run_time.max(), 2)
        min_run_time = round(plotting.results_df.run_time.min(), 2)
        _fig = mo.md(
            f"""
                     First, we visualize the distribution of run times. 
                     
                     Median run time: """
            + str(median_run_time)
            + """ seconds
                     
                     Mean run time: """
            + str(mean_run_time)
            + """ seconds
                     
                     Max run time: """
            + str(max_run_time)
            + """ seconds
                     
                     Min run time: """
            + str(min_run_time)
            + """ seconds
                     """
        )
    else:
        _fig = None
    _fig
    return


@app.cell
def __(plotting):
    if plotting is not None:
        _fig = plotting.plot_run_times()
    else:
        _fig = None
    _fig
    return


@app.cell
def __(plotting, mo):
    if plotting is not None:
        az_mae = round(plotting.results_df["absolute_error_azimuth"].mean(), 2)
        tilt_mae = round(plotting.results_df["absolute_error_tilt"].mean(), 2)
        _fig = mo.md(
            f"""
                     Next, we visualize the mean absolute error distribution.
                     
                     Azimuth MAE: """
            + str(az_mae)
            + """ degrees
                     
                     Tilt MAE: """
            + str(tilt_mae)
            + """ degrees
                     """
        )
    else:
        _fig = None
    _fig
    return


@app.cell
def __(plotting, mo):
    if plotting is not None:
        _fig = mo.md(
            f"""
                     We visualize the absolute error distribution for azimuth.
                     """
        )
    else:
        _fig = None
    _fig
    return


@app.cell
def __(plotting, mo):
    if plotting is not None:
        _fig = plotting.plot_azimuth_error()
    else:
        _fig = None
    _fig
    return


@app.cell
def __(plotting, mo):
    if plotting is not None:
        _fig = mo.md(
            f"""
                     We then visualize the absolute error distribution for tilt.
                     """
        )
    else:
        _fig = None
    _fig
    return


@app.cell
def __(plotting):
    if plotting is not None:
        _fig = plotting.plot_tilt_error()
    else:
        _fig = None
    _fig
    return


@app.cell
def __(plotting, mo):
    if plotting is not None:
        _fig = mo.md(
            f"""
                     We then visualize algorithm run time (in seconds) vs. the number of days in the associated AC power data set.
                     """
        )
    else:
        _fig = None
    _fig
    return


@app.cell
def __(plotting):
    if plotting is not None:
        _fig = plotting.plot_number_days_runtime()
    else:
        _fig = None
    _fig
    return


@app.cell
def __(
    mo,
    np,
    sns,
    pd,
    plt,
):

    class generatePlots:

        def __init__(self, results_df):
            """Create plotting class."""
            self.results_df = results_df
            self.results_df = self.results_df.rename(
                columns={
                    "issue": "Data Issue Type",
                    "absolute_error_azimuth": "Azimuth Absolute Error",
                    "absolute_error_tilt": "Tilt Absolute Error",
                    "run_time": "Run Time",
                    "number_days": "Number Days",
                }
            )

        def plot_run_times(self):
            fig = sns.histplot(self.results_df, x="run_time", bins=40)
            fig.set(xlabel="Run Time (seconds)", ylabel="Number Instances")
            return fig

        def plot_azimuth_error(self):
            fig = sns.histplot(
                self.results_df,
                x="Azimuth Absolute Error",
                hue="Data Issue Type",
                bins=30,
            )
            fig.set(
                xlabel="Azimuth Absolute Error (deg)",
                ylabel="Number Instances",
            )
            return fig

        def plot_tilt_error(self):
            fig = sns.histplot(
                self.results_df,
                x="Tilt Absolute Error",
                hue="Data Issue Type",
                bins=30,
            )
            fig.set(
                xlabel="Tilt Absolute Error (deg)", ylabel="Number Instances"
            )
            return fig

        def plot_number_days_runtime(self):
            fig = sns.scatterplot(
                data=self.results_df, x="Run Time", y="Number Days"
            )
            fig.set(xlabel="Run Time (s)", ylabel="Number Days in Dataset")
            return fig

    return (generatePlots,)


@app.cell
def __():
    import marimo as mo
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    import json

    return (
        json,
        mo,
        np,
        sns,
        pd,
        plt,
    )


@app.cell
def __(json, mo, pd):

    def create_df_from_cli_args():
        args = mo.cli_args().to_dict()
        data = args.get("results_df")
        rows = []
        for row in data:
            rows.append(json.loads(row))

        df = pd.DataFrame.from_records(rows)
        return df

    return (create_df_from_cli_args,)


if __name__ == "__main__":
    app.run()
