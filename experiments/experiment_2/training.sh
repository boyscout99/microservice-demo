#!/bin/bash

S2=("CPU" "p95" "mem" "rep")
S3=("CPU" "p95" "rep")
S4=("p95" "mem" "rep")
S5=("rps" "p95" "rep")
S6=("p95" "rep")

echo "${S2[@]}"
# states=(${S2[@]} ${S3[@]} ${S4[@]} ${S5[@]} ${S6[@]})
states=(S2 S3 S4 S5 S6)
echo "${states[$@]}"

# for state in "${states[@]}"; do
#     echo "Training for state $state"
#     eval values=\(\"\$\{$state\[@\]\}\"\)
#     echo "$values"
#     echo "python3 agent_learn.py \
#         --deployment productcatalogservice \
#         --namespace rl-agent-2 \
#         --cluster local \
#         --model A2C \
#         --rew_fun linear_1 \
#         --learn_rate 0.0007 \
#         --metrics \"${!state[@]}\""
#     # python3 agent_learn.py \
#     #     --deployment productcatalogservice \
#     #     --namespace rl-agent-2 \
#     #     --cluster local \
#     #     --model A2C \
#     #     --rew_fun linear_1 \
#     #     --learn_rate 0.0007 \
#     #     --metrics "${!state[*]}"
#     # Take best model at the end of the training
#     # Eliminate useless logs
# done