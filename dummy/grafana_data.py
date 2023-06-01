import csv
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

# Read data from CSV
timestamps = []
signal1 = []
signal2 = []
signal3 = []

with open('CPU utilisation [%]-data-as-seriestocolumns-2023-06-01 09_47_45.csv', 'r') as file:
    reader = csv.reader(file)
    headers = next(reader)  # Skip the first row (headers)
    for row in reader:
        if row:
            timestamps.append(datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S'))
            signal1.append(float(row[1]))
            signal2.append(float(row[2]))
            signal3.append(float(row[3]))

# Calculate mean of each signal over the past 5 minutes
mean_window = timedelta(minutes=5)

# Find the index of the last timestamp
last_index = len(timestamps) - 1

# Find the end time
end_time = timestamps[last_index]

# Calculate the start time for the 5-minute window
start_time = end_time - mean_window

print(f"mean_window: {mean_window}, last_index: {last_index}, end_time: {end_time}, start_time: {start_time}")

# Find the nearest timestamps within the 5-minute window
nearest_indices = [i for i, ts in enumerate(timestamps) if start_time <= ts <= end_time]

# Get the signal values within the time window for each signal
window_signal1 = [signal1[i] for i in nearest_indices]
window_signal2 = [signal2[i] for i in nearest_indices]
window_signal3 = [signal3[i] for i in nearest_indices]

# Calculate the mean of the values within the time window for each signal
mean_signal1 = np.mean(window_signal1)
mean_signal2 = np.mean(window_signal2)
mean_signal3 = np.mean(window_signal3)

# Create plot
plt.plot(timestamps, signal1, color='r', label=headers[1])
plt.plot(timestamps, signal2, color='g', label=headers[2])
plt.plot(timestamps, signal3, color='b', label=headers[3])

# Add mean lines
plt.axhline(y=mean_signal1, color='r', linestyle='--', label=f"Mean (Signal 1) {mean_signal1}")
plt.axhline(y=mean_signal2, color='g', linestyle='--', label=f"Mean (Signal 2) {mean_signal2}")
plt.axhline(y=mean_signal3, color='b', linestyle='--', label=f"Mean (Signal 3) {mean_signal3}")

# Set labels and title
plt.xlabel('Time')
plt.ylabel('Signal Value')
plt.title('Signal Data')

# Add legend
plt.legend()

# Display the plot
plt.show()
