'''
This class is used to call the Prometheus API and query for the state
of the system.
'''

from prometheus_api_client import PrometheusConnect
from statistics import mean
import requests.exceptions
import json
import time

class PrometheusClient:

    def __init__(self, url):
        '''
        Connect to Prometheus API
        '''
        self.url = url
        self.prom = PrometheusConnect(url = self.url)

    def query(self, query):
        '''
        Query the Prometheus API with the given query in promQL.
        Returns the mean of the values in the query.
        '''
        try:
            result = self.prom.custom_query(query = query)
            # take the mean of the values (TODO temporary)
            value = mean([float(q["value"][1]) for q in result])
            # print("Query result: ", value)
            return value

        except requests.exceptions.RequestException as e:
            print(f"Error connecting to Prometheus: {e}")
            time.sleep(1)
            return None

        except Exception as e:
            print(f"Unexpected error occurred: {e}")
            return None

    def get_results(self, queries):
        '''
        Given a list of promQL, append the results given by the function
        query() in a list called results[].
        Returns the list of results.
        '''
        results = []
        for query in queries:
            result = self.query(query = query)
            found = 0
            tentatives = 0

            if result is not None:
                results.append(result)
            else:
                # retake the query
                while(tentatives < 3 or found):
                    result = self.query(query = query)
                    if result is not None:
                        results.append(result)
                        found = 1
                    else:
                        tentatives += 1
                        print(f"Missing value, repeating query. Tentative {tentatives}.")
                        time.sleep(tentatives**2*30) # exponential backoff strategy up to 9 minutes
                # if tentatives == 3:
                #     # call for interpolation
                #     interpolation()

        json_results = json.dumps(results, indent=2)
        print("Results: \n", json_results)
        return results
