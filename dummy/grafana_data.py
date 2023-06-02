# import pandas as pd
# from datetime import datetime, timedelta
# import matplotlib.pyplot as plt
# import numpy as np

# # Read data from DataFrame
# df = pd.read_csv('All timeseries together-data-as-seriestocolumns-2023-06-01 17_39_37.csv')

# # Fill missing values with 0
# df.fillna(0, inplace=True)

# print(df)

# """
# "Time","RPS-testing","CPU-testing","p90-testing","replicas-testing","memory-testing","RPS-rl-agent-e1-a2c","CPU-rl-agent-e1-a2c","p90-rl-agent-e1-a2c","replicas-rl-agent-e1-a2c","memory-rl-agent-e1-a2c","RPS-rl-agent-e1-ppo","CPU-rl-agent-e1-ppo","p90-rl-agent-e1-ppo","replicas-rl-agent-e1-ppo"
# """

# # Extract timestamps and signals from DataFrame
# timestamps = pd.to_datetime(df['Time'])
# signal1 = df['RPS-testing']
# signal2 = df['RPS-rl-agent-e1-a2c']
# signal3 = df['RPS-rl-agent-e1-ppo']

# # Calculate mean of each signal over the past 5 minutes
# mean_window = timedelta(minutes=5)

# # Find the index of the last timestamp
# last_index = len(timestamps) - 1

# # Find the end time
# end_time = timestamps.iloc[last_index]

# # Calculate the start time for the 5-minute window
# start_time = end_time - mean_window

# print(f"mean_window: {mean_window}, last_index: {last_index}, end_time: {end_time}, start_time: {start_time}")

# # Find the nearest timestamps within the 5-minute window
# nearest_indices = (timestamps >= start_time) & (timestamps <= end_time)

# # Get the signal values within the time window for each signal
# window_signal1 = signal1[nearest_indices]
# window_signal2 = signal2[nearest_indices]
# window_signal3 = signal3[nearest_indices]

# # Calculate the mean of the values within the time window for each signal
# mean_signal1 = np.mean(window_signal1)
# mean_signal2 = np.mean(window_signal2)
# mean_signal3 = np.mean(window_signal3)

# # Create plot
# plt.plot(timestamps, signal1, color='r', label='Signal 1')
# plt.plot(timestamps, signal2, color='g', label='Signal 2')
# plt.plot(timestamps, signal3, color='b', label='Signal 3')

# # Add mean lines
# plt.axhline(y=mean_signal1, color='r', linestyle='--', label=f"Mean (Signal 1) {mean_signal1}")
# plt.axhline(y=mean_signal2, color='g', linestyle='--', label=f"Mean (Signal 2) {mean_signal2}")
# plt.axhline(y=mean_signal3, color='b', linestyle='--', label=f"Mean (Signal 3) {mean_signal3}")

# # Set labels and title
# plt.xlabel('Time')
# plt.ylabel('Signal Value')
# plt.title('Signal Data')

# # Add legend
# plt.legend()

# # Display the plot
# plt.show()

import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

# Read data from DataFrame
df = pd.read_csv('All timeseries together-data-as-seriestocolumns-2023-06-01 21_43_07.csv')

# Fill missing values with 0
df.fillna(0, inplace=True)

# Extract timestamps and signals from DataFrame
timestamps = pd.to_datetime(df['Time'])
signal1 = df['RPS-testing']
signal2 = df['RPS-rl-agent-e1-a2c']
signal3 = df['RPS-rl-agent-e1-ppo']

# compute the mean of the signals at regular time intervals
mean_signal1 = []
mean_signal2 = []
mean_signal3 = []

# the time length of the timeseries is len(df)*5s
total_time_sec = len(timestamps)*5
print(f"total_timestamps: {len(timestamps)}, total_time_sec: {total_time_sec}")
# 2.5 minutes correspond to 2*60+30s = 150s = 30 indexes

# Create a rolling window with a size of 2.5 minutes and a step of 2.5 minutes
# Resample the DataFrame to 2.5 minute intervals
i = 60
j = 30
means_signal1 = []
plt.plot(timestamps, signal1, color='r', label='Signal 1')
print(f"len(singal1): {len(signal1)}")
for index in range(0, len(signal1), i):
    if index+j>=len(signal1): break
    if (index+2*j>len(signal1)):
        right = len(signal1)
    else:
        right = (index+2*j)
    print(f"index+j: {index+j}, index+2*j: {right}")
    selected_window = signal1.iloc[index+j:right]
    print(f"selected_window:\n{selected_window}")
    plt.plot(timestamps.iloc[index+j:right], selected_window, color='b', label='Selected')
    mean_signal1 = np.mean(selected_window)
    print(f"mean: {mean_signal1}")
    x_min = (index+j)
    x_max = right
    # plt.hlines(y=mean_signal1, xmin=x_min, xmax=x_max, color='g', linestyle='--', label=f"Mean (Signal 1) {mean_signal1}")
    plt.hlines(y=mean_signal1, color='g', linestyle='--', label=f"Mean (Signal 1) {mean_signal1}")
    means_signal1.append(mean_signal1)
    # print(means_signal1)
# Apply a function or aggregation on the rolling window
# For example, to calculate the mean of each window:


# a = np.array([mean_signal1, mean_signal2, mean_signal3])
# std = np.std(a)
# #calculate standard error of the mean 
# stde = np.std(a, ddof=1) / np.sqrt(np.size(a))

# print(f"a: {a}, std: {std}, stde: {stde}")

# # Create plot

# plt.plot(timestamps, signal2, color='g', label='Signal 2')
# plt.plot(timestamps, signal3, color='b', label='Signal 3')

# # Add mean lines
# plt.axhline(y=mean_signal1, color='r', linestyle='--', label=f"Mean (Signal 1) {mean_signal1}")
# plt.axhline(y=mean_signal2, color='g', linestyle='--', label=f"Mean (Signal 2) {mean_signal2}")
# plt.axhline(y=mean_signal3, color='b', linestyle='--', label=f"Mean (Signal 3) {mean_signal3}")

# # Set labels and title
# plt.xlabel('Time')
# plt.ylabel('Signal Value')
# plt.title('Signal Data')

# # Add legend
plt.legend()

# # Display the plot
plt.show()
