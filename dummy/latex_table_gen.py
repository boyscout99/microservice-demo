import json

# Read the JSON data from file
with open('sample.json') as f:
    data = json.load(f)

# Define column names and subcolumn names
columns = ['rep', 'rps', 'p90', 'cpu', 'mem']
subcolumns = ['mean', 'std', 'stderr']

# Generate the LaTeX table header
table_header = '\\begin{tabular}{|ccc|ccc|ccc|ccc|ccc|}\n'
table_header += '\\hline\n'
table_header += ' & \\multicolumn{3}{c|}{rep} & \\multicolumn{3}{c|}{rps} & \\multicolumn{3}{c|}{p90} & \\multicolumn{3}{c|}{cpu} & \\multicolumn{3}{c|}{mem} \\\\\n'
table_header += '\\hline\n'
table_header += ' & mean & std & stderr & mean & std & stderr & mean & std & stderr & mean & std & stderr & mean & std & stderr \\\\\n'
table_header += '\\hline\n'

# Generate the table rows
table_rows = ''
for item in data:
    row = ' & '.join([f'{item[column][index]}' for column in columns for index, subcolumn in enumerate(subcolumns)])
    table_rows += f'{row} \\\\\n'
    table_rows += '\\hline\n'

# Generate the LaTeX table footer
table_footer = '\\end{tabular}'

# Combine all the components to form the complete LaTeX table
latex_table = table_header + table_rows + table_footer

# Print the generated LaTeX table
print(latex_table)