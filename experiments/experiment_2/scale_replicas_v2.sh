#!/bin/bash

deployment="productcatalogservice"
namespaces=("default" "testing" "rl-agent-e1-a2c" "rl-agent-e1-ppo" "rl-agent-e3-1" "rl-agent-e3-2" "rl-agent-e4-1")

replicas=1
while [ $replicas -le 15 ]; do
    for namespace in "${namespaces[@]}"; do
        echo "Scaling deployment $deployment in namespace $namespace to $replicas replicas"
        kubectl scale deployment -n $namespace $deployment --replicas $replicas
    done
    replicas=$((replicas + 1))
    echo "Waiting 660 seconds ..."
    sleep 660  # Wait for loadgen experiment to finish
    for namespace in "${namespaces[@]}"; do
        echo "Restarting loadgene"
        kubectl scale deployment -n $namespace $deployment --replicas $replicas
    done
done
