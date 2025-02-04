import numpy as np
import pandas as pd

# ----------------------------
# Metric Operations
# ----------------------------


def m_mean(df: pd.DataFrame, column: str):
    mean = df[column].mean()
    return mean


def m_median(df: pd.DataFrame, column: str):
    median = df[column].median()
    return median


metric_operations_map = {
    "mean": m_mean,
    "median": m_median,
}

# ----------------------------
# Performance Metrics
# ----------------------------


def p_absolute_error(output: pd.Series[float], ground_truth: pd.Series[float]):
    difference: pd.Series[float] = output - ground_truth
    absolute_difference = np.abs(difference)
    return absolute_difference


def p_mean_absolute_error(
    output: pd.Series[float], ground_truth: pd.Series[float]
):
    output.index = ground_truth.index
    difference: pd.Series[float] = output - ground_truth
    absolute_difference = np.abs(difference)
    mean_absolute_error = np.mean(absolute_difference)
    return mean_absolute_error


def p_error(output: pd.Series[float], ground_truth: pd.Series[float]):
    difference: pd.Series[float] = output - ground_truth
    return difference


performance_metrics_map = {
    "absolute_error": p_absolute_error,
    "mean_absolute_error": p_mean_absolute_error,
    "error": p_error,
}
