import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import json
import math

# Read data from DataFrame
df = pd.read_csv('timeseries/All timeseries together-data-as-seriestocolumns-2023-06-07 11_01_02.csv')

# Fill missing values with 0
df.fillna(0, inplace=True)

# Extract timestamps and signals from DataFrame
timestamps = pd.to_datetime(df['Time'])
# Filter columns that start with 'RPS'
rep_columns = [col for col in df.columns if col.startswith('replicas')]
rps_columns = [col for col in df.columns if col.startswith('RPS')]
p90_columns = [col for col in df.columns if col.startswith('p90')]
cpu_columns = [col for col in df.columns if col.startswith('CPU')]
mem_columns = [col for col in df.columns if col.startswith('mem')]

# Create a new DataFrame with selected columns
rep = df[rep_columns]
rps = df[rps_columns]
p90 = df[p90_columns]
cpu = df[cpu_columns]
mem = df[mem_columns]

# define the order of the metrics
metrics_df = [rep, rps, p90, cpu, mem]
metrics_df_order = ["rep", "rps", "p90", "cpu", "mem"]

# Create a series of plots for each measurement
fig, axs = plt.subplots(len(metrics_df), 1)
metric_idx = 0
for df in metrics_df:
    axs[metric_idx].set_title(metrics_df_order[metric_idx])
    for col in df:
        axs[metric_idx].plot(timestamps, df[col].values, color='b', label=f"{col}")
    metric_idx += 1

# Create a dictionary for the measurements
measurements = []

# Create a rolling window with a size of 2.5 minutes and a step of 2.5 minutes
# Resample the DataFrame to 2.5 minute intervals
# the time length of the timeseries is len(df)*5s
size = len(timestamps)
total_time_sec = size*5
# 2.5 minutes correspond to 2*60+30s = 150s = 30 index
# total time of interval before changing replicas into number of indexes
tot_time_interval_index = 300/5
i = math.ceil(tot_time_interval_index)
j = math.ceil(i/2)-11
# i = 70
# j = 35
print(f"total_timestamps: {size}, total_time_sec: {total_time_sec}, tot_time_interval_index: {tot_time_interval_index}, (i,j): ({i},{j})")

for index in range(0, size, i):
    left = index+j
    right = index+2*j
    # if window exceeds dimension fix limits
    if left>=size: break
    elif right>size:
        right=size
    else:
        right = right
    print(f"left margin: {left}, right margin: {right}")
    # for every measurement compute the mean of the window
    metric_idx = 0
    measure = {} # dictionary of metrics for a single window
    # compute mean on the window for every metric
    for df in metrics_df:
        means = [] # list the mean value in the window of each measurement
        # for every measurement of the same metric
        for col in df:
            # compute the window
            window = df[col].iloc[left:right].values
            # highlight the winow on top of the signal
            axs[metric_idx].plot(timestamps.iloc[left:right], window, color='r')
            # compute the mean of the values in the window
            mean = np.mean(window)
            # plot the mean as horizontal line
            x_min = timestamps.iloc[index + j]
            x_max = timestamps.iloc[right - 1]
            axs[metric_idx].hlines(y=mean, xmin=x_min, xmax=x_max, color='c', linestyle='--')
            # append to a list of means
            means.append(mean)
        # compute standard deviation and standard error for the interval on same metric
        std = np.std(means)
        stde = np.std(means, ddof=1) / np.sqrt(np.size(means))
        # save an entry in the dictionary as
        # {"metric name":[mean of measurements, std, sterr]}
        measure[metrics_df_order[metric_idx]] = [round(np.mean(means),2), round(std,2), round(stde,2)]
        # go to the next metric
        metric_idx += 1
    # add the results of the interval to the dictionary of all intervals
    measurements.append(measure)
    print(f"measurements:\n{measurements}")

# Save file to json
json_object = json.dumps(measurements, indent=4, separators=(',', ':'))
with open("exp2_samples.json", "w") as outfile:
    outfile.write(json_object)
# check correct indexing
print("Data:", measurements[0]["p90"][0])

# Add legend
# plt.legend()
# Display the plot
plt.show()
