import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import json
import math

# Read data from DataFrame
df = pd.read_csv('timeseries/14hrs_predict.csv')

# Fill missing values with 0
df.fillna(0, inplace=True)

# Extract timestamps and signals from DataFrame
timestamps = pd.to_datetime(df['Time'])

# sin load
sin_p95_agent = df['p95-rl-agent-e1-a2c']
sin_p95_hpa = df['p95-rl-agent-e1-ppo']
sin_rep_agent = df['replicas-rl-agent-e1-a2c']
sin_rep_hpa = df['replicas-rl-agent-e1-ppo']

# rnd sin load
rnd_sin_p95_agent = df['p95-rl-agent-e3-1']
rnd_sin_p95_hpa = df['p95-rl-agent-e3-2']
rnd_sin_rep_agent = df['replicas-rl-agent-e3-1']
rnd_sin_rep_hpa = df['replicas-rl-agent-e3-2']

print(f"p95 agent: {sin_p95_agent[1]}")
print(f"Timesteps: {len(sin_p95_agent)}")
print(timestamps[1])
sla_viol_agent = (sin_p95_agent>5).sum()/len(sin_p95_agent)*100
sla_viol_hpa = (sin_p95_hpa>5).sum()/len(sin_p95_hpa)*100
mean_rep_agent = sin_rep_agent.mean()
mean_rep_hpa = sin_rep_hpa.mean()
print(f"Violations: agent {sla_viol_agent}, HPA {sla_viol_hpa}")
print(f"Mean replicas: agent {mean_rep_agent}, HPA {mean_rep_hpa}")

rnd_sla_viol_agent = (rnd_sin_p95_agent>5).sum()/len(rnd_sin_p95_agent)*100
rnd_sla_viol_hpa = (rnd_sin_p95_hpa>5).sum()/len(rnd_sin_p95_hpa)*100
rnd_mean_rep_agent = rnd_sin_rep_agent.mean()
rnd_mean_rep_hpa = rnd_sin_rep_hpa.mean()
print(f"Violations (rnd): agent {rnd_sla_viol_agent}, HPA {rnd_sla_viol_hpa}")
print(f"Mean replicas (rnd): agent {rnd_mean_rep_agent}, HPA {rnd_mean_rep_hpa}")

# plt.plot(timestamps, sin_p95_agent, label='agent')
# plt.plot(timestamps, sin_p95_hpa, label='HPA')
plt.plot(timestamps, rnd_sin_rep_agent, label='agent')
plt.plot(timestamps, rnd_sin_rep_hpa, label='HPA')
plt.show()
# Filter columns that start with 'RPS'
# rep_columns = [col for col in df.columns if col.startswith('replicas')]
# rps_columns = [col for col in df.columns if col.startswith('RPS')]
# p90_columns = [col for col in df.columns if col.startswith('p95')]
# cpu_columns = [col for col in df.columns if col.startswith('CPU')]
# mem_columns = [col for col in df.columns if col.startswith('mem')]
# load_column = [col for col in df.columns if col.startswith('dep')]
# add one more column for rps to deployment

# Create a new DataFrame with selected columns
# rep = df[rep_columns]
# rps = df[rps_columns]
# p90 = df[p90_columns]
# cpu = df[cpu_columns]
# mem = df[mem_columns]
# load = df[load_column]


