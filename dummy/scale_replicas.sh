#!/bin/bash

deployment="productcatalogservice"
namespaces=("rl-agent-e1-a2c" "testing" "rl-agent-e3-1")

replicas=1
while [ $replicas -le 30 ]; do
    for namespace in "${namespaces[@]}"; do
        echo "Scaling deployment $deployment in namespace $namespace to $replicas replicas"
        kubectl scale deployment -n $namespace $deployment --replicas $replicas
    done
    replicas=$((replicas + 1))
    sleep 600  # Sleep for 10 minutes
done