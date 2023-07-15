"""
For a load of 1500 RPS to the deployment, 
generate a table that reports for each
replica, the metrics calculated for that load.
"""
import os
import json
import numpy as np
from get_metrics import GetMetrics

# Get the absolute path of the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Copy samples for synthetic traffic
data_json_path = os.path.join(script_dir, "exp3_sorted_samples.json")
d_file = open(data_json_path, "r")
data = json.load(d_file)
# print(f"Data samples:\n{data}")
d_file.close()

content = []
for i in range(1,16):
    content.append(
        GetMetrics(data, ['rps', 'CPU', 'p95', 'mem']).get_metrics_approx(i, 1500)
        )
print(content)

SLA_RESP_TIME = 5
alpha = 15
# Compute expected reward
for item in content:
    delta_t = item['p95']-SLA_RESP_TIME
    perc = delta_t/SLA_RESP_TIME
    if perc>0:
        reward = -100*perc
    else:
        reward = 10*((100/alpha) * perc + 1) + (15/item['rep'])
    item.update({'rew': reward})

# Define column names
columns = ['rep', 'rps', 'p95', 'CPU', 'mem', 'rew']

# Generate the LaTeX table header
table_header = '\\begin{tabular}{|c|c|c|c|c|c|}\n'
table_header += '\\hline\n'
table_header += f"Replicas & RPS [req/s] & p95 & CPU & memory & reward \\\\\n"
table_header += '\\hline\n'

# Generate the table rows
table_rows = ''
for item in content:
    row = ' & '.join([f'${round(item[column],2)}$' for column in columns])
    table_rows += f'{row} \\\\\n'
    table_rows += '\\hline\n'

# Generate the LaTeX table footer
table_footer = '\\end{tabular}'

# Combine all the components to form the complete LaTeX table
latex_table = table_header + table_rows + table_footer

# Print the generated LaTeX table
print(latex_table)