import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import json
import math

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "sans-serif",
    "font.sans-serif": "Georgia",
    "font.size": 12,
    "figure.dpi": 250
})

# Read data from DataFrame
# df = pd.read_csv('timeseries/24hrs_new_predict.csv')
df = pd.read_csv('timeseries/24b_hrs_predict.csv')
# pick last 50 elements
# df = df.tail(220)
df = df[1:721]

# Fill missing values with 0
df.fillna(0, inplace=True)

# Extract timestamps and signals from DataFrame
# timestamps = pd.to_datetime([i/1000 for i in df['Time']], unit='s')
# timestamps = timestamps.strftime("%H:%M")
# timestamps = df['Time']
# Convert the string column to datetime format
df['Time'] = pd.to_datetime(df['Time'])

# Format the datetime column to display only the hour and minute
timestamps = df['Time'].dt.strftime('%H:%M')
print(f"Length timestamps: {len(timestamps)}")

# rnd sin load on S2
rnds2_sin_p95_agent = df['p95-rl-agent-e1-a2c']
rnds2_sin_rps_agent = df['RPS-rl-agent-e1-a2c']
# rnds2_sin_p95_hpa = df['p95-default']
rnds2_sin_rep_agent = df['replicas-rl-agent-e1-a2c']
# rnds2_sin_rep_hpa = df['replicas-default']
rnds2_sin_cpu_agent = df['CPU-rl-agent-e1-a2c']
# rnds2_sin_cpu_hpa = df['CPU-rl-agent-e1-ppo']
rnds2_sin_load_agent = df['dep_RPS-rl-agent-e1-a2c']
# rnds2_sin_load_hpa = df['dep_RPS-default']

# rnd sin load on S4
# rnds4_sin_p95_agent = df['p95-testing']
rnds4_sin_p95_agent = df['p95-testing']
rnds4_sin_p95_hpa = df['p95-default']
rnds4_sin_rep_agent = df['replicas-testing']
rnds4_sin_rep_hpa = df['replicas-default']
rnds4_sin_cpu_agent = df['CPU-testing']
rnds4_sin_cpu_hpa = df['CPU-default']
rnds4_sin_load_agent = df['dep_RPS-testing']
rnds4_sin_load_hpa = df['dep_RPS-default']
# rnds4_sin_load_hpa = df['dep_RPS-rl-agent-e3-1']
rnds4_sin_rps_hpa = df['RPS-default']

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
print("### New Random sin on S2 ###")
sla_viol_agent = (rnds2_sin_p95_agent>5).sum()/len(rnds2_sin_p95_agent)*100
# sla_viol_hpa = (sin_p95_hpa>5).sum()/len(sin_p95_hpa)*100
print(f"Violations: agent {sla_viol_agent}")
mean_rep_agent = rnds2_sin_rep_agent.mean()
print(f"Mean replicas: agent {mean_rep_agent}")
mean_cpu_agent = rnds2_sin_cpu_agent.mean()
print(f"Mean CPU: agent {mean_cpu_agent}")
mean_load_agent = rnds2_sin_load_agent.mean()
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
# load_1000 = [i/1000 for i in rnds2_sin_load_agent]
# plt.plot(timestamps, rnds2_sin_p95_agent, label="$L_{s,t}$ agent $S_{2}$")
# plt.plot(timestamps, rnds4_sin_p95_hpa, label="$L_{s,t}$ HPA")
# plt.plot(timestamps, rnds2_sin_rep_agent, '--', label='$N_{s,t}$ agent $S_{2}$')
# plt.plot(timestamps, sin_load_hpa, label='HPA e1-ppo')
# plt.plot(timestamps, rnds4_sin_load_agent, label='agent testing')
# plt.plot(timestamps, [i/1000 for i in rnds2_sin_load_agent], label="Load/1000 agent $S_{2}$")
# plt.plot(timestamps, [i/1000 for i in rnds4_sin_load_hpa], label="Load/1000 HPA")
# plt.plot(timestamps, rnds4_sin_rep_hpa, '--', label='$N_{s,t}$ HPA')
# plt.plot(timestamps, [i/100 for i in rnds4_sin_rps_hpa], '-.', label='rps HPA default')
# plt.plot(timestamps, [i/100 for i in rnds2_sin_rps_agent], '-.', label='rps agent e1-a2c')
# plt.plot(timestamps, rnd_sin_p95_agent, label='rnd s4 agent')
# plt.plot(timestamps, rnd_sin_p95_hpa, label='rnd s4 HPA')
fig, ax = plt.subplots()
plt.plot(timestamps, rnds2_sin_p95_agent)
# plt.plot(timestamps, cos_load_hpa, label='HPA e3-2')
# plt.legend()
ax.xaxis.set_major_locator(plt.MaxNLocator(20))
# Set the x-axis limits to include the last tick
# ax.set_xlim(timestamps[0], timestamps[-1])
# ax.locator_params(nbins=20)
plt.xlabel('Timesteps')
plt.xticks(rotation=45)
plt.ylabel('req/s')
# plt.ylim(0,8)
plt.title("Latency in GKE environment with load $H_{p}$")
plt.tight_layout()
plt.grid(linewidth='0.5')
# plt.show()
plt.savefig("sin_s4_gke_p95.png")


