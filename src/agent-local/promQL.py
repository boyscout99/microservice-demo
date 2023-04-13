from prometheus_api_client import PrometheusConnect
import requests.exceptions

prom = PrometheusConnect(url='http://prometheus.istio-system.svc.cluster.local:9090')

# query = 'istio_request_duration_milliseconds_count{app="frontend", response_code="200",response_flags="-",request_protocol="http",source_app="loadgenerator"}'
q_response_time = 'rate(istio_request_duration_milliseconds_count{app="frontend", response_code="200",response_flags="-",request_protocol="http",source_app="loadgenerator"}[1m])'
try:
    result = prom.custom_query(query=q_response_time)
    print("Query result: ", result)
except requests.exceptions.RequestException as e:
    print(f"Error connecting to Prometheus: {e}")
except Exception as e:
    print(f"Unexpected error occurred: {e}")
