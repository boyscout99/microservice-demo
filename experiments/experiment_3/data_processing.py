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
df = pd.read_csv('timeseries/new_data_sawTooth_1500users_20230620.csv')

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
load_column = [col for col in df.columns if col.startswith('dep')]
# add one more column for rps to deployment

# Create a new DataFrame with selected columns
rep = df[rep_columns]
rps = df[rps_columns]
p90 = df[p90_columns]
cpu = df[cpu_columns]
mem = df[mem_columns]
load = df[load_column]

# define the order of the metrics
metrics_df = [rep, load, rps, p90, cpu, mem]
metrics_df_order = ["rep", "load", "rps", "p95", "CPU_", "mem"]
metrics_df_means = pd.DataFrame()

print("load df\n", load)

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
    df = pd.DataFrame({f'{metrics_df_order[metric_idx]}_mean': mean_signal})
    # print("df", df)
    metrics_df_means[metrics_df_order[metric_idx]] = df
    metric_idx += 1

print(metrics_df_means)
# Create a dictionary for the JSON
"""
[
    {
        'rep':1.0,
        'metric_rows':[
            {'rps':200, 'cpu':50},
            {'rps':300, 'cpu':80}
        ]
    },
    {
        'rep':2.0,
        'metric_rows':[
            {'rps':200, 'cpu':25},
            {'rps':300, 'cpu':40}
        ]
    }
]
"""

json_list = []
json_dict = {}
for _, row in metrics_df_means.iterrows():
    # if list is empty
    if not json_list:
        d = {'rep': row['rep'], 'metric_rows':[row.drop('rep').to_dict()]}
        # print(d)
        # append that dictionary to the list
        json_list.append(d)
    else:
        # check if dicitonary for that replica is already present in the list
        if not any(d['rep'] == row['rep'] for d in json_list):
            # create a new dictionary for the number of replicas
            d = {'rep': row['rep'], 'metric_rows':[row.drop('rep').to_dict()]}
            # print(d)
            # append that dictionary to the list
            json_list.append(d)
        else:
            # add metrics for that replica
            for index in range(len(json_list)):
                if json_list[index]['rep'] == row['rep']:
                    json_list[index]['metric_rows'].append(row.drop('rep').to_dict())
                    # sort by rps
                    # TODO sort by RPS to deployment
                    json_list[index]['metric_rows'] = sorted(json_list[index]['metric_rows'], key=lambda metric: metric['load'])

# print(json_list)

# Save file to json
json_object = json.dumps(json_list, indent=4, separators=(',', ':'))
with open("exp3_new_sorted_samples.json", "w") as outfile:
    outfile.write(json_object)
# # check correct indexing
# # print("Data:", json_list[0]["p95"])

# Add legend
# plt.legend()
# Display the plot
# plt.show()
