from prometheus_api_client import PrometheusConnect
import requests.exceptions

prom = PrometheusConnect(url='http://localhost:9090')

query = 'istio_request_duration_milliseconds_count{app="frontend", response_code="200",response_flags="-",request_protocol="http",source_app="loadgenerator"}'
try:
    result = prom.custom_query(query=query)
    print("Query result: ", result)
except requests.exceptions.RequestException as e:
    print(f"Error connecting to Prometheus: {e}")
except Exception as e:
    print(f"Unexpected error occurred: {e}")
