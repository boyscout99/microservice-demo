from prometheus_api_client import PrometheusConnect
import requests.exceptions

prom = PrometheusConnect(url='http://prometheus.istio-system.svc.cluster.local:9090')

# QUERIES FOR FRONTEND DEPLOYMENT
# request duration [ms]
q_request_duration = 'rate(istio_request_duration_milliseconds_count{app="frontend", response_code="200",response_flags="-",request_protocol="http",source_app="loadgenerator"}[1m])'
# cpu utilisation [%]
q_cpu_usage = 'rate(container_cpu_usage_seconds_total{pod=~"frontend-.*"}[1m])/0.2'
# memory usage [Mb]
# !TODO change the image name
q_memory_usage = 'rate(container_memory_usage_bytes{pod=~"frontend-.*"}[1m])/1000000'
# number of replicas per deployment
q_pod_replicas = 'count(kube_pod_info{pod=~"frontend-.*"})'

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
        print("Query result: ", result[0]['value'])
        results.append(result)

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Prometheus: {e}")

    except Exception as e:
        print(f"Unexpected error occurred: {e}")

print("Results: \n", results)
