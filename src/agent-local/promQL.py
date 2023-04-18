from prometheus_api_client import PrometheusConnect
import requests.exceptions
import json

prom = PrometheusConnect(url='http://prometheus.istio-system.svc.cluster.local:9090')

# QUERIES FOR FRONTEND DEPLOYMENT
q_request_duration = 'max(rate(istio_request_duration_milliseconds_count{pod=~"frontend-.*", request_protocol="grpc", response_code="200", namespace="rl-agent"}[1m]))'
# cpu utilisation [%]
# query for gke:
# q_cpu_usage = 'rate(container_cpu_usage_seconds_total{pod=~"frontend-.*", namespace="rl-agent", container="server"}[1m])/0.1*100'
# query for minikube
q_cpu_usage = 'rate(container_cpu_usage_seconds_total{pod=~"frontend-.*", namespace="rl-agent"}[1m])/0.1*100'
# memory usage [%]
# query for gke:
# q_memory_usage = 'rate(container_memory_usage_bytes{pod=~"frontend-.*", container="server", namespace="rl-agent"}[1m])/64000000'
# query for minikube:
q_memory_usage = 'rate(container_memory_usage_bytes{pod=~"frontend-.*", namespace="rl-agent"}[1m])/64000000'
# number of replicas per deployment
q_pod_replicas = 'count(kube_pod_info{pod=~"frontend-.*", namespace="rl-agent"})'

# list of queries
queries = [
    q_request_duration,
    q_cpu_usage,
    q_memory_usage,
    q_pod_replicas
]
# list of query results
results = []

for query in queries:

    try:
        result = prom.custom_query(query=query)
        values = [float(q["value"][1]) for q in result]
        # cast to float type
        print("Query result: ", values)
        results.append(result)

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Prometheus: {e}")

    except Exception as e:
        print(f"Unexpected error occurred: {e}")

json_results = json.dumps(results, indent=2)
print("Results: \n", json_results)
