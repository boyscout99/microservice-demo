#!/bin/bash

deployment="productcatalogservice"
namespaces=("default" "testing" "rl-agent-e1-a2c" "rl-agent-e1-ppo" "rl-agent-e3-1" "rl-agent-e3-2" "rl-agent-e4-1")
auxiliary=("frontend" "recommendationservice" "checkoutservice" "currencyservice" "adservice" "cartservice")

for namespace in "${namespaces[@]}"; do
    echo "Scaling $deployment in $namespace to 1 replica."
    kubectl scale deployment -n $namespace $deployment --replicas 1
done

for namespace in "${namespaces[@]}"; do
    for service in "${auxiliary[@]}"; do
        echo "Scaling up bottleneck service $service to 6 replicas in namespace $namespace"
        kubectl scale deployment -n $namespace $service --replicas 6
    done
    echo "Deploying loadgenerator in namespace $namespace"
    kubectl apply -f /mnt/nfs-client/microservice-demo/kubernetes-manifests/$namespace/loadgenerator.yaml -n $namespace
done

