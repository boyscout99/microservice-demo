import os
import json
from get_metrics import GetMetrics
import math
import matplotlib.pyplot as plt

d_file = open('exp3_sorted_samples.json', 'r')
data = json.load(d_file)
d_file.close()

d = GetMetrics(data, ['CPU', 'p95', 'rps', 'mem']).get_metrics_approx(2,150)
print(d)

a = GetMetrics(data, ['p95']).plot_data()

opt_rep = GetMetrics(data, ['CPU', 'p95', 'rps', 'mem']).optimal_rep_given_workload(150)
print(f"opt_rep: {opt_rep}")


# import scipy.stats as stats

# # Given data
# sample_mean = -3782956
# sample_std = 1223759
# sample_size = 10

# # Hypothesized population mean (Null Hypothesis)
# population_mean = -4552630

# # Calculate the t-statistic
# t_statistic = (sample_mean - population_mean) / (sample_std / (sample_size ** 0.5))

# # Calculate the degrees of freedom
# degrees_of_freedom = sample_size - 1

# # Set the significance level (alpha)
# alpha = 0.10

# # Find the critical value from the t-distribution table (two-tailed test)
# critical_value = stats.t.ppf(1 - alpha / 2, df=degrees_of_freedom)

# # Calculate the p-value (two-tailed test)
# p_value = 2 * (1 - stats.t.cdf(abs(t_statistic), df=degrees_of_freedom))

# # Print the results
# print("T-statistic:", t_statistic)
# print("P-value:", p_value)

# # Compare p-value and alpha for statistical significance
# if p_value <= alpha:
#     print("The results are statistically significant.")
# else:
#     print("The results are not statistically significant.")
# import math
# import numpy as np

# with open('signals.json') as f_in:
#     data = json.load(f_in)

# sin_sig = data[2]['rps_signal']
# # take two days of timesteps
# steps = 2*2880
# sin_sig = sin_sig[:steps]
# # convert RPS to Locust users
# # alpha = 50/70 # conversion factor, 50 users : 70 RPS
# # users_sig = [math.ceil(rps*50/70) for rps in sin_sig]
# users_sig = np.arange(10,1000,5)
# time = np.arange(0, len(users_sig))*30/60

# # for t in range(1400):
# #     current_step = math.floor(t / 30) + 1
# #     users = users_sig[current_step]
# #     print(users)

# plt.plot(time, users_sig, label='users')
# # plt.plot(time, sin_sig, label='load')
# plt.show()