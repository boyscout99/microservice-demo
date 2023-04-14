from query import PrometheusClient
from scale import KubernetesEnvironment

url = 'http://prometheus.istio-system.svc.cluster.local:9090'
prom = PrometheusClient(url)

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
    q_pod_replicas,
    q_request_duration,
    q_cpu_usage,
    q_memory_usage
]

prom.get_results(queries)

## Test scaling action
deployment = "frontend"
namespace = "rl-agent"

scale = KubernetesEnvironment(deployment, namespace)
scale.update_replicas(-1)
