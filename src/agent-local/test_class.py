from Query import PrometheusClient
from Scale import KubernetesEnvironment

url = 'http://prometheus.istio-system.svc.cluster.local:9090'
prom = PrometheusClient(url)

# QUERIES FOR FRONTEND DEPLOYMENT
# request duration [ms]
q_request_duration = 'max(rate(istio_request_duration_milliseconds_count{pod=~"frontend-.*", request_protocol="grpc", response_code="200", namespace="rl-agent"}[1m]))'
# cpu utilisation [%]
q_cpu_usage = 'rate(container_cpu_usage_seconds_total{pod=~"frontend-.*", namespace="rl-agent"}[1m])/0.1*100'
# memory usage [%]
q_memory_usage = 'rate(container_memory_usage_bytes{pod=~"frontend-.*", namespace="rl-agent"}[1m])/64000000'
# number of replicas per deployment
q_pod_replicas = 'count(kube_pod_info{pod=~"frontend-.*", namespace="rl-agent"})'

# list of queries
queries = [
    q_pod_replicas,
    q_request_duration,
    q_cpu_usage,
    q_memory_usage
]

prom.get_results(queries)

## Test scaling action
name = "frontend"
namespace = "rl-agent"

# scale = KubernetesEnvironment(name, namespace)
# scale.update_replicas(-1)
