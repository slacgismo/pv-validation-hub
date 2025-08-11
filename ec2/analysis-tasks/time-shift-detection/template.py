import marimo

__generated_with = "0.1.18"
app = marimo.App()


@app.cell
def __(mo):
    mo.md("# Private Report: Time Shift Data Results")
    return


@app.cell
def __(pd, generatePlots):
    results_df = pd.read_csv("time_shifts_full_results.csv")
    plotting = generatePlots(results_df)
    return results_df, plotting


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
    return


@app.cell
def __(plotting):
    if plotting is not None:
        _fig = plotting.plot_mae_by_issue()
    else:
        _fig = None
    _fig
    return


@app.cell
def __(plotting, mo):
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
def __(plotting, mo):
    if plotting is not None:
        _fig = plotting.dataframe_mae_by_issue_type()
    else:
        _fig = None
    _fig
    return


@app.cell
def __(plotting, mo):
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
def __(plotting, mo):
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
def __(plotting, mo, pd):
    if plotting is not None:
        _fig = plotting.dataframe_mae_by_sampling()
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
                    "mean_absolute_error_time_series": "Time Series-Level MAE",
                    "data_sampling_frequency": "Data Sampling Frequency (minutes)",
                }
            )

        def plot_run_times(self):
            fig = sns.histplot(self.results_df, x="run_time", bins=40)
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
    import matplotlib.pyplot as plt
    import seaborn as sns

    return (
        mo,
        np,
        sns,
        pd,
        plt,
    )


if __name__ == "__main__":
    app.run()
