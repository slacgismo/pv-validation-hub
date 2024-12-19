import pandas as pd

orig_df = pd.read_csv(
    "./file_data/1332_inv_total_ac_power__2654_15min_random_time_shifts.csv",
    index_col=0,
    parse_dates=True,
)


valid_df = pd.read_csv(
    "./validation_data/1332_inv_total_ac_power__2654_15min_random_time_shifts.csv",
    index_col=0,
    parse_dates=True,
)

valid_df.index = valid_df.index.tz_localize(orig_df.index.tz)

valid_df = valid_df.reindex(orig_df.index).ffill()

print("Number dates:")
print(len(pd.Series(orig_df.index.date).drop_duplicates()))
print(len(pd.Series(valid_df.index.date).drop_duplicates()))

print("Number timestamps:")
print(len(pd.Series(orig_df.index).drop_duplicates()))
print(len(pd.Series(valid_df.index).drop_duplicates()))
