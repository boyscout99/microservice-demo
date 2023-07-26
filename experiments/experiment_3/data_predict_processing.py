import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import json
import math

# Read data from DataFrame
df = pd.read_csv('timeseries/24b_hrs_predict.csv')

# Fill missing values with 0
df.fillna(0, inplace=True)

# Extract timestamps and signals from DataFrame
timestamps = pd.to_datetime(df['Time'])
print(f"Length timestamps: {len(timestamps)}")

# sin load on S4
sin_p95_agent = df['p95-rl-agent-e1-a2c']
sin_p95_hpa = df['p95-rl-agent-e1-ppo']
sin_rep_agent = df['replicas-rl-agent-e1-a2c']
sin_rep_hpa = df['replicas-rl-agent-e1-ppo']
sin_cpu_agent = df['CPU-rl-agent-e1-a2c']
sin_cpu_hpa = df['CPU-rl-agent-e1-ppo']
sin_load_agent = df['dep_RPS-rl-agent-e1-a2c']
sin_load_hpa = df['dep_RPS-rl-agent-e1-ppo']

# rnd sin load on S2
rnds2_sin_p95_agent = df['p95-testing']
rnds2_sin_p95_hpa = df['p95-default']
rnds2_sin_rep_agent = df['replicas-testing']
rnds2_sin_rep_hpa = df['replicas-default']
rnds2_sin_cpu_agent = df['CPU-testing']
rnds2_sin_cpu_hpa = df['CPU-default']
rnds2_sin_load_agent = df['dep_RPS-testing']
rnds2_sin_load_hpa = df['dep_RPS-default']

# rnd sin load on S4
rnd_sin_p95_agent = df['p95-rl-agent-e3-1']
rnd_sin_p95_hpa = df['p95-rl-agent-e3-2']
rnd_sin_rep_agent = df['replicas-rl-agent-e3-1']
rnd_sin_rep_hpa = df['replicas-rl-agent-e3-2']
rnd_sin_cpu_agent = df['CPU-rl-agent-e3-1']
rnd_sin_cpu_hpa = df['CPU-rl-agent-e3-2']
rnd_sin_load_agent = df['dep_RPS-rl-agent-e3-1']
rnd_sin_load_hpa = df['dep_RPS-rl-agent-e3-2']

# Sin on S4
print("### Sin on S4 ###")
sla_viol_agent = (sin_p95_agent>5).sum()/len(sin_p95_agent)*100
sla_viol_hpa = (sin_p95_hpa>5).sum()/len(sin_p95_hpa)*100
print(f"Violations: agent {sla_viol_agent}, HPA {sla_viol_hpa}")
mean_rep_agent = sin_rep_agent.mean()
mean_rep_hpa = sin_rep_hpa.mean()
print(f"Mean replicas: agent {mean_rep_agent}, HPA {mean_rep_hpa}")
mean_cpu_agent = sin_cpu_agent.mean()
mean_cpu_hpa = sin_cpu_hpa.mean()
print(f"Mean CPU: agent {mean_cpu_agent}, HPA {mean_cpu_hpa}")
mean_load_agent = sin_load_agent.mean()
mean_load_hpa = sin_load_hpa.mean()
print(f"Mean load: agent {mean_load_agent}, HPA {mean_load_hpa}")

# Random sin on S2
print("### Random sin on S2 ###")
rnds2_sla_viol_agent = (rnds2_sin_p95_agent>5).sum()/len(rnds2_sin_p95_agent)*100
rnds2_sla_viol_hpa = (rnds2_sin_p95_hpa>5).sum()/len(rnds2_sin_p95_hpa)*100
print(f"Violations: agent {rnds2_sla_viol_agent}, HPA {rnds2_sla_viol_hpa}")
rnds2_mean_rep_agent = rnds2_sin_rep_agent.mean()
rnds2_mean_rep_hpa = rnds2_sin_rep_hpa.mean()
print(f"Mean replicas: agent {rnds2_mean_rep_agent}, HPA {rnds2_mean_rep_hpa}")
rnds2_mean_cpu_agent = rnds2_sin_cpu_agent.mean()
rnds2_mean_cpu_hpa = rnds2_sin_cpu_hpa.mean()
print(f"Mean CPU: agent {rnds2_mean_cpu_agent}, HPA {rnds2_mean_cpu_hpa}")
# mean_rps_agent = sin_rps_agent.mean()
# mean_rps_hpa = sin_rps_hpa.mean()
# print(f"Mean RPS: agent {mean_rps_agent}, HPA {mean_rps_hpa}")
rnds2_mean_load_agent = rnds2_sin_load_agent.mean()
rnds2_mean_load_hpa = rnds2_sin_load_hpa.mean()
print(f"Mean load: agent {rnds2_mean_load_agent}, HPA {rnds2_mean_load_hpa}")

# Random sin on S4
print("### Random sin on S4 ###")
rnd_sla_viol_agent = (rnd_sin_p95_agent>5).sum()/len(rnd_sin_p95_agent)*100
rnd_sla_viol_hpa = (rnd_sin_p95_hpa>5).sum()/len(rnd_sin_p95_hpa)*100
print(f"Violations (rnd): agent {rnd_sla_viol_agent}, HPA {rnd_sla_viol_hpa}")
rnd_mean_rep_agent = rnd_sin_rep_agent.mean()
rnd_mean_rep_hpa = rnd_sin_rep_hpa.mean()
print(f"Mean replicas (rnd): agent {rnd_mean_rep_agent}, HPA {rnd_mean_rep_hpa}")
rnd_mean_cpu_agent = rnd_sin_cpu_agent.mean()
rnd_mean_cpu_hpa = rnd_sin_cpu_hpa.mean()
print(f"Mean CPU: agent {rnd_mean_cpu_agent}, HPA {rnd_mean_cpu_hpa}")
# mean_rps_agent = sin_rps_agent.mean()
# mean_rps_hpa = sin_rps_hpa.mean()
# print(f"Mean RPS: agent {mean_rps_agent}, HPA {mean_rps_hpa}")
rnd_mean_load_agent = rnd_sin_load_agent.mean()
rnd_mean_load_hpa = rnd_sin_load_hpa.mean()
print(f"Mean load: agent {rnd_mean_load_agent}, HPA {rnd_mean_load_hpa}")

# plt.plot(timestamps, sin_load_agent, label='sin agent')
# plt.plot(timestamps, sin_load_hpa, label='sin HPA')
# plt.plot(timestamps, rnd_sin_load_agent, label='rnd s4 agent')
# plt.plot(timestamps, rnd_sin_load_hpa, label='rnd s4 HPA')
plt.figure(dpi=300)
plt.plot(timestamps, rnd_sin_p95_agent, label='rnd s4 agent')
# plt.plot(timestamps, rnd_sin_p95_hpa, label='rnd s4 HPA')
# plt.plot(timestamps, rnds2_sin_load_agent, label='rnd s2 agent')
# plt.plot(timestamps, rnds2_sin_load_hpa, label='rnd s2 HPA')
# plt.legend()
plt.xlabel('Timesteps')
plt.ylabel('ms')
plt.ylim(0,20)
plt.title("$L_{s,t}$ inference emulation for $H_{r}$ on $S_{4}$")
plt.grid()
plt.show()


