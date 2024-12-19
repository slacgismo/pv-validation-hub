import marimo

__generated_with = "0.6.16"
app = marimo.App()


@app.cell
def __(mo):
    mo.md("# Private Report: Time Shift Data Results")
    return


@app.cell
def __(create_df_from_cli_args, generatePlots):
    results_df = create_df_from_cli_args()
    plotting = generatePlots(results_df)
    return plotting, results_df


@app.cell
def __(mo, plotting):
    if plotting is not None:
        median_runtime = round(plotting.results_df.runtime.median(), 2)
        mean_runtime = round(plotting.results_df.runtime.mean(), 2)
        max_runtime = round(plotting.results_df.runtime.max(), 2)
        min_runtime = round(plotting.results_df.runtime.min(), 2)
        _fig = mo.md(
            f"""
                     First, we visualize the distribution of run times. 

                     Median run time: """
            + str(median_runtime)
            + """ seconds

                     Mean run time: """
            + str(mean_runtime)
            + """ seconds

                     Max run time: """
            + str(max_runtime)
            + """ seconds

                     Min run time: """
            + str(min_runtime)
            + """ seconds
                     """
        )
    else:
        _fig = None
    _fig
    return max_runtime, mean_runtime, median_runtime, min_runtime


@app.cell
def __(plotting):
    if plotting is not None:
        _fig = plotting.plot_runtimes()
    else:
        _fig = None
    _fig
    return


@app.cell
def __(mo, plotting):
    if plotting is not None:
        median_mae = round(
            plotting.results_df["Time Series-Level MAE"].median(), 2
        )
        mean_mae = round(
            plotting.results_df["Time Series-Level MAE"].mean(), 2
        )
        _fig = mo.md(
            f"""
                     Next, we visualize the mean absolute error distribution, color-coded by issues present in the time series.

                     Median time series MAE: """
            + str(median_mae)
            + """ minutes

                     Mean time series MAE: """
            + str(mean_mae)
            + """ minutes
                     """
        )
    else:
        _fig = None
    _fig
    return mean_mae, median_mae


@app.cell
def __(plotting):
    if plotting is not None:
        _fig = plotting.plot_mae_by_issue()
    else:
        _fig = None
    _fig
    return


@app.cell
def __(mo, plotting):
    if plotting is not None:
        _fig = mo.md(
            f"""
                     Mean of Time Series-Level MAE, by Issue Type
                     """
        )
    else:
        _fig = None
    _fig
    return


@app.cell
def __(plotting):
    if plotting is not None:
        _fig = plotting.dataframe_mae_by_issue_type()
    else:
        _fig = None
    _fig
    return


@app.cell
def __(mo, plotting):
    if plotting is not None:
        _fig = mo.md(
            f"""
                     We then visualize the mean absolute error distribution, color-coded by data sampling frequency.
                     """
        )
    else:
        _fig = None
    _fig
    return


@app.cell
def __(plotting):
    if plotting is not None:
        _fig = plotting.plot_mae_by_sampling_frequency()
    else:
        _fig = None
    _fig
    return


@app.cell
def __(mo, plotting):
    if plotting is not None:
        _fig = mo.md(
            f"""
                     Mean of Time Series-Level MAE, by Data Sampling Frequency
                     """
        )
    else:
        _fig = None
    _fig
    return


@app.cell
def __(plotting):
    if plotting is not None:
        _fig = plotting.dataframe_mae_by_sampling()
    else:
        _fig = None
    _fig
    return


@app.cell
def __(pd, sns):
    class generatePlots:

        def __init__(self, results_df):
            """Create plotting class."""
            self.results_df = results_df
            self.results_df = self.results_df.rename(
                columns={
                    "issue": "Data Issue Type",
                    "mean_absolute_error_time_series": "Time Series-Level MAE",
                    "data_sampling_frequency": "Data Sampling Frequency (minutes)",
                }
            )

        def plot_runtimes(self):
            fig = sns.histplot(self.results_df, x="runtime", bins=40)
            fig.set(xlabel="Run Time (seconds)", ylabel="Number Instances")
            return fig

        def plot_mae_by_issue(self):
            fig = sns.histplot(
                self.results_df,
                x="Time Series-Level MAE",
                hue="Data Issue Type",
                bins=30,
            )
            fig.set(
                xlabel="Time Series-Level MAE (minutes)",
                ylabel="Number Instances",
            )
            return fig

        def plot_mae_by_sampling_frequency(self):
            fig = sns.histplot(
                self.results_df,
                x="Time Series-Level MAE",
                hue="Data Sampling Frequency (minutes)",
                bins=30,
            )
            fig.set(
                xlabel="Time Series-Level MAE (minutes)",
                ylabel="Number Instances",
            )
            return fig

        def dataframe_mae_by_issue_type(self):
            df = self.results_df.groupby("Data Issue Type")[
                "Time Series-Level MAE"
            ].mean()
            df = pd.DataFrame(df.reset_index())
            return df

        def dataframe_mae_by_sampling(self):
            df = self.results_df.groupby("Data Sampling Frequency (minutes)")[
                "Time Series-Level MAE"
            ].mean()
            df = pd.DataFrame(df.reset_index())
            return df

    return (generatePlots,)


@app.cell
def __():
    import marimo as mo
    import numpy as np
    import pandas as pd
    import json
    import matplotlib.pyplot as plt
    import seaborn as sns

    return json, mo, np, pd, plt, sns


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
