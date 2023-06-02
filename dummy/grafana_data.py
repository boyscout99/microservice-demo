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
rps1 = df['RPS-testing']
rps2 = df['RPS-rl-agent-e1-a2c']
rps3 = df['RPS-rl-agent-e1-ppo']

rps = pd.DataFrame({'rps1': rps1, 'rps2': rps2, 'rps3': rps3})

# the time length of the timeseries is len(df)*5s
total_time_sec = len(timestamps)*5
print(f"total_timestamps: {len(timestamps)}, total_time_sec: {total_time_sec}")
# 2.5 minutes correspond to 2*60+30s = 150s = 30 index
rgb = 0
for col in rps:
    rgb += 0.1
    plt.plot(timestamps, rps[col].values, color=(0.5+rgb, 0.5+rgb, 0.5+rgb), label=f"{col}")


# Create a rolling window with a size of 2.5 minutes and a step of 2.5 minutes
# Resample the DataFrame to 2.5 minute intervals
i = 60
j = 25
means = []
size = len(rps)

for index in range(0, size, i):
    left = index+j
    right = index+2*j
    if left>=size: break
    elif right>size:
        right=size
    else:
        right = right
    print(f"left margin: {left}, right margin: {right}")
    rgb = 0
    for col in rps:
        rgb += 0.01
        window = rps[col].iloc[left:right].values
        plt.plot(timestamps.iloc[left:right], window, color=(rgb, rgb, rgb))
        mean = np.mean(window)

    # window_1 = signal1.iloc[index+j:right]
    # window_2 = signal2.iloc[index+j:right]
    # window_3 = signal3.iloc[index+j:right]
    # print(f"selected_window:\n{window_1}")
    # print(f"selected_window:\n{window_2}")
    # print(f"selected_window:\n{window_3}")
    # plt.plot(timestamps.iloc[index+j:right], window_1, color='m')
    # plt.plot(timestamps.iloc[index+j:right], window_2, color='m')
    # plt.plot(timestamps.iloc[index+j:right], window_3, color='m')

    # mean_signal1 = np.mean(window_1)
    # mean_signal2 = np.mean(window_2)
    # mean_signal3 = np.mean(window_3)
    # # print(f"mean: {mean_signal1}")
    # x_min = timestamps.iloc[index + j]
    # x_max = timestamps.iloc[right - 1]
    # plt.hlines(y=mean_signal1, xmin=x_min, xmax=x_max, color='c', linestyle='--', label=f"Mean (Signal 1) {mean_signal1}")
    # plt.hlines(y=mean_signal2, xmin=x_min, xmax=x_max, color='c', linestyle='--', label=f"Mean (Signal 2) {mean_signal2}")
    # plt.hlines(y=mean_signal3, xmin=x_min, xmax=x_max, color='c', linestyle='--', label=f"Mean (Signal 3) {mean_signal3}")
    # means_signal1.append(mean_signal1)
    # means_signal2.append(mean_signal2)
    # means_signal3.append(mean_signal3)
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
