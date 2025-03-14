# Clean up any duplicated data sets

from statistics import mode
import pandas as pd
import glob
import os

file_metadata = pd.read_csv(
    "C:/Users/kperry/Documents/source/repos/time-shift-validation-hub/data/file_metadata.csv"
)

# file_metadata_filter = file_metadata.drop_duplicates(subset=['file_name', 'system_id', 'file_name', 'timezone',
#        'data_sampling_frequency', 'issue', 'subissue'], keep="last")

# file_metadata_filter['file_id'] = file_metadata_filter.reset_index(drop=True).index

# file_metadata_filter.to_csv("C:/Users/kperry/Documents/source/repos/time-shift-validation-hub/data/file_metadata.csv",
#                             index=False)

file_test_link = pd.read_csv(
    "C:/Users/kperry/Documents/source/repos/time-shift-validation-hub/data/file_test_link.csv"
)


system_metadata = pd.read_csv(
    "C:/Users/kperry/Documents/source/repos/time-shift-validation-hub/data/system_metadata.csv"
)


files = glob.glob(
    "C:/Users/kperry/Documents/source/repos/time-shift-validation-hub/data/file_data/*"
)

error_freq_list = list()

# for file in files:
#     df = pd.read_csv(file, index_col=0, parse_dates=True)
#     # Double verify our sampling frequency is right
#     freq_minutes = mode(df.index.to_series().diff().dt.seconds / 60)
#     # Look up the file metadata to double verify
#     data_info = dict(file_metadata[file_metadata['file_name'] == os.path.basename(file)].iloc[0])
#     if data_info['data_sampling_frequency'] != freq_minutes:
#         print("Data frequency discrepancy for file: " + file)
#         print("Frequency should be: " + str(freq_minutes))
#         error_freq_list.append({"file_name": os.path.basename(file),
#                                 "data_frequency": freq_minutes})


# error_list = pd.DataFrame(error_freq_list)

file_test_link_new = pd.DataFrame()

file_test_link_new["file_id"] = file_metadata["file_id"]
file_test_link_new["test_id"] = file_metadata["file_id"]
file_test_link_new["category_id"] = 0

file_test_link_new = file_test_link_new[["test_id", "category_id", "file_id"]]

file_test_link_new.to_csv(
    "C:/Users/kperry/Documents/source/repos/time-shift-validation-hub/data/file_test_link.csv",
    index=False,
)


val_files = glob.glob(
    "C:/Users/kperry/Documents/source/repos/time-shift-validation-hub/data/validation_data/*"
)

val_files_base = [os.path.basename(val) for val in val_files]
files_base = [os.path.basename(file) for file in files]

main_list = [item for item in val_files_base if item not in files_base]
