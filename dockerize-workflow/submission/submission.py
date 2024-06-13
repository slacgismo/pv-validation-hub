import numpy as np
from time import sleep
from time import perf_counter
import csv


def submission_function(index: str = "0", *args, **kwargs):
    start = perf_counter()

    random_number = np.random.rand()
    sleep_time = random_number * 15
    sleep(sleep_time)
    end = perf_counter()
    time_elapsed = end - start

    print(f"{index} : {time_elapsed}")

    # Write time elapsed to a csv file
    with open(f"results/{index}.csv", mode="w") as file:
        writer = csv.writer(file)
        writer.writerow([time_elapsed])

    print("Submission function completed successfully!")
    return time_elapsed
