import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import json

# Define the exponential function
def exponential_func(x, a, b):
    return a * np.exp(-b * x)

file = open("sample.json", "r")
data = json.load(file)
file.close()

x_values = []
y_values = []

print(data)

for i in range(len(data)):
    y_values.append(data[i]["rps"][0])
    x_values.append(i+1)

# Convert the vectors to numpy arrays
x_values = np.array(x_values)
y_values = np.array(y_values)

# Fit the exponential function to the data
popt, pcov = curve_fit(exponential_func, x_values, y_values)

# Extract the optimized parameters
a_opt, b_opt = popt

# Generate the fitted line
fitted_line = exponential_func(x_values, a_opt, b_opt)

print("a_opt: %.2f, b_opt: %.2f" % (a_opt, b_opt))

# Plot the original data points and the fitted line
plt.scatter(x_values, y_values, color='red', label='Original Data')
plt.plot(x_values, fitted_line, label='Fitted Line')
plt.title(f"Fitting function, y=%.2fexp(-%.2f, x)" % (a_opt, b_opt))
plt.xlabel('replicas')
plt.ylabel('CPU')
plt.legend()
plt.show()

