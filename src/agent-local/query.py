# This is a class to query Prometheus API
from prometheus_api_client import PrometheusConnect
from statistics import mean
import requests.exceptions
import json

class PrometheusClient:
    def __init__(self, url):
        self.url = url
        self.prom = PrometheusConnect(url = self.url)

    def query(self, query):
        try:
            result = self.prom.custom_query(query = query)
            value = mean([float(q["value"][1]) for q in result])
            # take the mean of the values (TODO temporary)
            # print("Query result: ", value)
            return value

        except requests.exceptions.RequestException as e:
            print(f"Error connecting to Prometheus: {e}")
            return None

        except Exception as e:
            print(f"Unexpected error occurred: {e}")
            return None

    def get_results(self, queries):
        results = []
        for query in queries:
            result = self.query(query = query)

            if result is not None:
                results.append(result)

        json_results = json.dumps(results, indent=2)
        print("Results: \n", json_results)
        return results
