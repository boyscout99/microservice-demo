import os
import json
from get_metrics import GetMetrics

d_file = open('exp3_sorted_samples.json', 'r')
data = json.load(d_file)
d_file.close()

# d = GetMetrics(data, ['CPU', 'p95', 'rps', 'mem']).get_metrics_approx(6,7000)
# print(d)

a = GetMetrics(data, ['p95']).plot_data()

# opt_rep = GetMetrics(data, ['CPU', 'p95', 'rps', 'mem']).optimal_rep_given_workload(5000)
# print(f"opt_rep: {opt_rep}")