import json
import numpy as np

# Read the JSON data from file
with open('exp1_samples.json') as f:
    data = json.load(f)
# for every element of the array
_std = []
_stderr = []
std_means = {}
stderr_means = {}
    
for metric in data[0]:
    # take every metric std and sterr and make the mean
    for i in range(len(data)):
        _std.append(data[i][metric][1])
        _stderr.append(data[i][metric][2])

    std_means[metric] = round(np.mean(_std), 2)
    stderr_means[metric] = round(np.mean(_stderr),2)
    _std = []
    _stderr = []

print(f"std_means: {std_means}\nstderr_means: {stderr_means}")
print(std_means['rps'])


# Define column names and subcolumn names
columns = ['rps', 'p95', 'cpu', 'mem']

# Generate the LaTeX table header
table_header = '\\begin{tabular}{|c|c|c|c|c|}\n'
table_header += '\\hline\n'
table_header += f"users & rps (std {std_means['rps']}, stderr {stderr_means['rps']}) & p95 (std {std_means['p95']}, stderr {stderr_means['p95']}) & cpu (std {std_means['cpu']}, stderr {stderr_means['cpu']}) & mem (std {std_means['mem']}, stderr {stderr_means['mem']}) \\\\\n"
table_header += '\\hline\n'

# Generate the table rows
table_rows = ''
for item in data:
    row = ' & '.join([f'{item[column][0]}' for column in columns])
    table_rows += f'{row} \\\\\n'
    table_rows += '\\hline\n'

# Generate the LaTeX table footer
table_footer = '\\end{tabular}'

# Combine all the components to form the complete LaTeX table
latex_table = table_header + table_rows + table_footer

# Print the generated LaTeX table
print(latex_table)