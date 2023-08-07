import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import json
import math

# Read data from DataFrame
# df = pd.read_csv('timeseries/24hrs_new_predict.csv')
df = pd.read_csv('timeseries/last_24hrs_new_inference.csv')

# Fill missing values with 0
df.fillna(0, inplace=True)

# Extract timestamps and signals from DataFrame
timestamps = pd.to_datetime(df['Time'])
print(f"Length timestamps: {len(timestamps)}")

# rnd sin load on S2
sin_p95_agent = df['p95-rl-agent-e1-a2c']
# sin_p95_hpa = df['p95-rl-agent-e1-ppo']
sin_rep_agent = df['replicas-rl-agent-e1-a2c']
# sin_rep_hpa = df['replicas-rl-agent-e1-ppo']
sin_cpu_agent = df['CPU-rl-agent-e1-a2c']
# sin_cpu_hpa = df['CPU-rl-agent-e1-ppo']
sin_load_agent = df['dep_RPS-rl-agent-e1-a2c']
# sin_load_hpa = df['dep_RPS-rl-agent-e1-ppo']

# rnd sin load on S4
rnds4_sin_p95_agent = df['p95-testing']
rnds4_sin_p95_hpa = df['p95-default']
rnds4_sin_rep_agent = df['replicas-testing']
rnds4_sin_rep_hpa = df['replicas-default']
rnds4_sin_cpu_agent = df['CPU-testing']
rnds4_sin_cpu_hpa = df['CPU-default']
rnds4_sin_load_agent = df['dep_RPS-testing']
rnds4_sin_load_hpa = df['dep_RPS-default']

# cos load on S4
cos_p95_agent = df['p95-rl-agent-e3-1']
cos_p95_hpa = df['p95-rl-agent-e3-2']
cos_rep_agent = df['replicas-rl-agent-e3-1']
cos_rep_hpa = df['replicas-rl-agent-e3-2']
cos_cpu_agent = df['CPU-rl-agent-e3-1']
cos_cpu_hpa = df['CPU-rl-agent-e3-2']
cos_load_agent = df['dep_RPS-rl-agent-e3-1']
cos_load_hpa = df['dep_RPS-rl-agent-e3-2']

# New rnd sin on S4
print("### New rnd sin on S2 ###")
sla_viol_agent = (sin_p95_agent>5).sum()/len(sin_p95_agent)*100
# sla_viol_hpa = (sin_p95_hpa>5).sum()/len(sin_p95_hpa)*100
print(f"Violations: agent {sla_viol_agent}")
mean_rep_agent = sin_rep_agent.mean()
print(f"Mean replicas: agent {mean_rep_agent}")
mean_cpu_agent = sin_cpu_agent.mean()
print(f"Mean CPU: agent {mean_cpu_agent}")
mean_load_agent = sin_load_agent.mean()
print(f"Mean load: agent {mean_load_agent}")

# Random sin on S4
print("### New Random sin on S4 ###")
rnds4_sla_viol_agent = (rnds4_sin_p95_agent>5).sum()/len(rnds4_sin_p95_agent)*100
rnds4_sla_viol_hpa = (rnds4_sin_p95_hpa>5).sum()/len(rnds4_sin_p95_hpa)*100
print(f"Violations: agent {rnds4_sla_viol_agent}, HPA {rnds4_sla_viol_hpa}")
rnds4_mean_rep_agent = rnds4_sin_rep_agent.mean()
rnds4_mean_rep_hpa = rnds4_sin_rep_hpa.mean()
print(f"Mean replicas: agent {rnds4_mean_rep_agent}, HPA {rnds4_mean_rep_hpa}")
rnds4_mean_cpu_agent = rnds4_sin_cpu_agent.mean()
rnds4_mean_cpu_hpa = rnds4_sin_cpu_hpa.mean()
print(f"Mean CPU: agent {rnds4_mean_cpu_agent}, HPA {rnds4_mean_cpu_hpa}")
# mean_rps_agent = sin_rps_agent.mean()
# mean_rps_hpa = sin_rps_hpa.mean()
# print(f"Mean RPS: agent {mean_rps_agent}, HPA {mean_rps_hpa}")
rnds4_mean_load_agent = rnds4_sin_load_agent.mean()
rnds4_mean_load_hpa = rnds4_sin_load_hpa.mean()
print(f"Mean load: agent {rnds4_mean_load_agent}, HPA {rnds4_mean_load_hpa}")

# Cos on S4
print("### Cosine on S4 ###")
cos_sla_viol_agent = (cos_p95_agent>5).sum()/len(cos_p95_agent)*100
cos_sla_viol_hpa = (cos_p95_hpa>5).sum()/len(cos_p95_hpa)*100
print(f"Violations: agent {cos_sla_viol_agent}, HPA {cos_sla_viol_hpa}")
cos_mean_rep_agent = cos_rep_agent.mean()
cos_mean_rep_hpa = cos_rep_hpa.mean()
print(f"Mean replicas: agent {cos_mean_rep_agent}, HPA {cos_mean_rep_hpa}")
cos_mean_cpu_agent = cos_cpu_agent.mean()
cos_mean_cpu_hpa = cos_cpu_hpa.mean()
print(f"Mean CPU: agent {cos_mean_cpu_agent}, HPA {cos_mean_cpu_hpa}")
# mean_rps_agent = sin_rps_agent.mean()
# mean_rps_hpa = sin_rps_hpa.mean()
# print(f"Mean RPS: agent {mean_rps_agent}, HPA {mean_rps_hpa}")
cos_mean_load_agent = cos_load_agent.mean()
cos_mean_load_hpa = cos_load_hpa.mean()
print(f"Mean load: agent {cos_mean_load_agent}, HPA {cos_mean_load_hpa}")

# plt.figure(dpi=300)
plt.plot(timestamps, sin_load_agent, label='agent e1-a2c')
# plt.plot(timestamps, sin_load_hpa, label='HPA e1-ppo')
plt.plot(timestamps, rnds4_sin_load_agent, label='agent testing')
plt.plot(timestamps, rnds4_sin_load_hpa, label='HPA default')
# plt.plot(timestamps, rnd_sin_p95_agent, label='rnd s4 agent')
# plt.plot(timestamps, rnd_sin_p95_hpa, label='rnd s4 HPA')
# plt.plot(timestamps, cos_load_agent, label='agent e3-1')
# plt.plot(timestamps, cos_load_hpa, label='HPA e3-2')
plt.legend()
plt.xlabel('Timesteps')
# plt.ylabel('ms')
# plt.ylim(0,20)
# plt.title("$L_{s,t}$ inference emulation for $H_{r}$ on $S_{4}$")
plt.grid()
plt.show()


