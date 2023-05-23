import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# Define the exponential function
def exponential_func(x, a, b):
    return a * np.exp(-b * x)

# Convert the vectors to numpy arrays
x_values = np.array([1 ,2, 3, 4, 5])
y_values = np.array([30, 14, 9, 7, 6])

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

