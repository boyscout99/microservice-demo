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
metrics_df_means = pd.DataFrame()

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
        mean_signal.append(np.round(row_mean,2))
    
    for col in df:
        # plot every signal of that metric
        axs[metric_idx].plot(timestamps, df[col].values, color='b', label=f"{col}")
    # plot the mean signal
    axs[metric_idx].plot(timestamps, mean_signal, color='r')
    # save the mean as the new signal
    df = pd.DataFrame({f'{metrics_df_order[metric_idx]}_mean':mean_signal})
    # print("df", df)
    metrics_df_means[metrics_df_order[metric_idx]] = df
    metric_idx += 1

print(metrics_df_means)
# Create a dictionary for the JSON
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
json_list = []
for _, row in metrics_df_means.iterrows():
    json_dict = row.to_dict()
    json_list.append(json_dict)

# Save file to json
json_object = json.dumps(json_list, indent=4, separators=(',', ':'))
with open("exp3_samples.json", "w") as outfile:
    outfile.write(json_object)
# check correct indexing
print("Data:", json_list[0]["p95"])

# Search for RPS, given replicas, to set cpu, p95, mem
replicas = 1
RPS = 250
with open("exp3_samples.json", "r") as f_input:
    data = json.load(f_input)

for elem in range(len(data)):
    # search for the intended number of replicas
    if data[elem]["rep"] == replicas:
        # search for the given RPS
        print("Element: ", data[elem])
        # print(f"elem {data[elem]['rps']} type: {type(data[elem]['rps'])}, elem+1 {data[elem+1]['rps']}")
        if (data[elem]["rps"] <= RPS) & (data[elem+1]["rps"] >= RPS):
            print("Element: ", data[elem+1])
            # take the wighted mean between the two measures and apply the coefficient to the metrics
            print("Inside the loop.")
            coeff = np.abs((RPS-data[elem]["rps"])/(data[elem+1]["rps"]-data[elem]["rps"])) # relative distance wrt the first element
            print(f"coeff: {coeff}")
            adj_cpu = data[elem]["cpu"]*(1+coeff*(data[elem+1]["cpu"]-data[elem]["cpu"])) # the adjusted cpu
            adj_mem = data[elem]["mem"]*coeff # the adjusted mem
            adj_p95 = data[elem]["p95"]*coeff # the adjusted p95
            break

print(f"Replicas: {replicas}, RPS: {RPS}, CPU: {adj_cpu}, memory: {adj_mem}, p95: {adj_p95}")


# Add legend
# plt.legend()
# Display the plot
# plt.show()
