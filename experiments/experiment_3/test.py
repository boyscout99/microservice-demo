import os
import json
from get_metrics import GetMetrics

# d_file = open('exp3_sorted_samples.json', 'r')
# data = json.load(d_file)
# d_file.close()

# d = GetMetrics(data, ['CPU', 'p95', 'rps', 'mem']).get_metrics_approx(6,7000)
# print(d)

# a = GetMetrics(data, ['p95']).plot_data()

# opt_rep = GetMetrics(data, ['CPU', 'p95', 'rps', 'mem']).optimal_rep_given_workload(5000)
# print(f"opt_rep: {opt_rep}")
import scipy.stats as stats

# Given data
sample_mean = -3782956
sample_std = 1223759
sample_size = 10

# Hypothesized population mean (Null Hypothesis)
population_mean = -4552630

# Calculate the t-statistic
t_statistic = (sample_mean - population_mean) / (sample_std / (sample_size ** 0.5))

# Calculate the degrees of freedom
degrees_of_freedom = sample_size - 1

# Set the significance level (alpha)
alpha = 0.10

# Find the critical value from the t-distribution table (two-tailed test)
critical_value = stats.t.ppf(1 - alpha / 2, df=degrees_of_freedom)

# Calculate the p-value (two-tailed test)
p_value = 2 * (1 - stats.t.cdf(abs(t_statistic), df=degrees_of_freedom))

# Print the results
print("T-statistic:", t_statistic)
print("P-value:", p_value)

# Compare p-value and alpha for statistical significance
if p_value <= alpha:
    print("The results are statistically significant.")
else:
    print("The results are not statistically significant.")