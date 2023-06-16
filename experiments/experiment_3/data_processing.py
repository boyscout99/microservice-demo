"""
Create a dictionary where for every number of replica there is a corresponding
value of (rps, p95, cpu, mem), so that there is a correspondence (replicas, metric).
In this way, if I give a pattern of RPS, with the number of replicas I will know
what are the p95, cpu, mem.
"""

import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import json
import math

# Read data from DataFrame
df = pd.read_csv('timeseries/data_sawTooth_1500users_1to15replicas_20230614.csv')

# Fill missing values with 0
df.fillna(0, inplace=True)

# Extract timestamps and signals from DataFrame
timestamps = pd.to_datetime(df['Time'])
# Filter columns that start with 'RPS'
rep_columns = [col for col in df.columns if col.startswith('replicas')]
rps_columns = [col for col in df.columns if col.startswith('RPS')]
p90_columns = [col for col in df.columns if col.startswith('p95')]
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
metrics_df_order = ["rep", "rps", "p95", "cpu", "mem"]
metrics_df_means = []

print("rps df\n", rps)

# Create a series of plots for each measurement
fig, axs = plt.subplots(len(metrics_df), 1)
metric_idx = 0
for df in metrics_df:
    axs[metric_idx].set_title(metrics_df_order[metric_idx])
    mean_signal = []
    # compute the mean of the group of signals and plot it
    # take the mean at each timestamp
    for timestamp in range(len(timestamps)):
        row_mean = np.mean(df.iloc[timestamp])
        # append the value to the array mean_signal
        mean_signal.append(row_mean)
    
    for col in df:
        # plot every signal of that metric
        axs[metric_idx].plot(timestamps, df[col].values, color='b', label=f"{col}")
    # plot the mean signal
    axs[metric_idx].plot(timestamps, mean_signal, color='r')
    # save the mean as the new signal
    df = pd.DataFrame({f'{metrics_df_order[metric_idx]}_mean':mean_signal})
    # print("df", df)
    metrics_df_means.append(df)
    metric_idx += 1

print(metrics_df_means)
# Create a dictionary for the measurements
measurements = []
"""
[
    {
        'rep':1.0,
        'rps':22,
        'cpu':10
    },
    {
        'rep':1.0,
        'rps':32,
        'cpu':20
    },
    {
        'rep':2.0,
        'rps':22,
        'cpu':5
    },
]
"""

# Create a rolling window with a size of 2.5 minutes and a step of 2.5 minutes
# Resample the DataFrame to 2.5 minute intervals
# the time length of the timeseries is len(df)*5s
size = len(timestamps)
total_time_sec = size*5
# 2.5 minutes correspond to 2*60+30s = 150s = 30 index
# total time of interval before changing replicas into number of indexes
tot_time_interval_index = 600/5

print(f"total_timestamps: {size}, total_time_sec: {total_time_sec}, tot_time_interval_index: {tot_time_interval_index}")


# Save file to json
json_object = json.dumps(measurements, indent=4, separators=(',', ':'))
with open("exp3_samples.json", "w") as outfile:
    outfile.write(json_object)
# check correct indexing
print("Data:", measurements[0]["p95"][0])

# Add legend
# plt.legend()
# Display the plot
plt.show()
