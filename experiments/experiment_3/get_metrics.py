"""
This script returns CPU, memory and p95 based on RPS and replicas.
"""
# Generalisation of the algorithm for (replicas, metric) correspondence
import numpy as np

class GetMetrics:
    def __init__(self, data):
        # Reference data from a JSON
        self.data = data

    def get_metrics_approx(self, replicas, rps):
        for elem in range(len(self.data)):
            # search for the intended number of replicas
            if self.data[elem]["rep"] == replicas:
                # search for the given RPS
                metric_list = self.data[elem]["metric_rows"]
                # print("Metric_list: ", metric_list)
                # print(f"elem {data[elem]['rps']} type: {type(data[elem]['rps'])}, elem+1 {data[elem+1]['rps']}")
                if (rps<metric_list[0]["rps"]): # case in which RPS is too low
                    # TODO Estimate new coefficient
                    print("ERROR - RPS too low!")
                    break
                elif (rps>metric_list[-1]["rps"]):
                    # TODO estimate new coefficient
                    print("ERROR - RPS too high!")
                    break
                else:
                    for index in range(len(metric_list)-1):
                        prev = metric_list[index]
                        next = metric_list[index+1]
                        # print("Element: ", prev)
                        if (prev["rps"] <= rps) and (next["rps"] >= rps):
                            # print("Element: ", next)
                            # take the wighted mean between the two measures and apply the coefficient to the metrics
                            # print("Inside the loop.")
                            coeff = np.abs((rps-prev['rps'])/(next['rps']-prev['rps'])) # relative distance wrt the first element
                            # print(f"coeff: {coeff}")
                            adj_cpu = prev["cpu"]+coeff*(next["cpu"]-prev["cpu"]) # the adjusted cpu
                            adj_mem = prev["mem"]+coeff*(next["mem"]-prev["mem"]) # the adjusted mem
                            adj_p95 = prev["p95"]+coeff*(next["p95"]-prev["p95"]) # the adjusted p95
                            # print(f"Replicas: {replicas}, RPS: {rps}, CPU: {adj_cpu}, memory: {adj_mem}, p95: {adj_p95}")
                            break 

        return [adj_cpu, adj_mem, adj_p95]