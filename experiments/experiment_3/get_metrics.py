"""
This script returns CPU, memory and p95 based on RPS and replicas.
Takes input data of this format.
[
    {
        "rep":1.0,
        "metric_rows":[
            {
                "load":150.43,
                "rps":150.43,
                "p95":4.85,
                "cpu":14.44,
                "mem":0.4
            },
            {
                "load":205.14,
                "rps":205.14,
                "p95":4.58,
                "cpu":20.8,
                "mem":0.37
            },
            {
                "load":257.43,
                "rps":257.43,
                "p95":4.54,
                "cpu":28.2,
                "mem":0.46
            }
    }
]
"""
# Generalisation of the algorithm for (replicas, metric) correspondence
import numpy as np

class GetMetrics:
    def __init__(self, data):
        # Reference data from a JSON
        self.data = data

    def get_metrics_approx(self, replicas, load):
        # TODO add metric about RPS to deployment and approx RPS to pod
        for elem in range(len(self.data)):
            # search for the intended number of replicas
            if self.data[elem]["rep"] == replicas:
                # search for the given RPS
                metric_list = self.data[elem]["metric_rows"]
                # print("Metric_list: ", metric_list)
                # print(f"elem {data[elem]['rps']} type: {type(data[elem]['rps'])}, elem+1 {data[elem+1]['rps']}")
                if (load<metric_list[0]["load"]): # case in which RPS is too low
                    # TODO Estimate new coefficient
                    print("Note - Load too low!")
                    coeff = np.abs((load-0)/(metric_list[0]["load"]-0)) # relative distance wrt the first element
                    # print(f"coeff: {coeff}")
                    adj_rps = coeff*(metric_list[0]["rps"]-0) # the adjusted rps
                    adj_cpu = coeff*(metric_list[0]["cpu"]-0) # the adjusted cpu
                    adj_mem = coeff*(metric_list[0]["mem"]-0) # the adjusted mem
                    adj_p95 = coeff*(metric_list[0]["p95"]-0) # the adjusted p95
                    break
                elif (load>metric_list[-1]["load"]):
                    # TODO estimate new coefficient
                    print("Note - Load too high!")
                    # do some linear regression to estimate the coefficent
                    # coeff = np.abs((rps-metric_list[-1]["rps"])/(rps-metric_list[-1]["rps"])) # relative distance wrt the first element
                    # # print(f"coeff: {coeff}")
                    # adj_cpu = coeff*(metric_list[0]["cpu"]-metric_list[-1]["cpu"]) # the adjusted cpu
                    # adj_mem = coeff*(metric_list[0]["mem"]-metric_list[-1]["mem"]) # the adjusted mem
                    # adj_p95 = coeff*(metric_list[0]["p95"]-metric_list[-1]["p95"]) # the adjusted p95
                    break
                else:
                    for index in range(len(metric_list)-1):
                        prev = metric_list[index]
                        next = metric_list[index+1]
                        # print("Element: ", prev)
                        if (prev["load"] <= load) and (next["load"] >= load):
                            # print("Element: ", next)
                            # take the wighted mean between the two measures and apply the coefficient to the metrics
                            # print("Inside the loop.")
                            coeff = np.abs((load-prev['load'])/(next['load']-prev['load'])) # relative distance wrt the first element
                            # print(f"coeff: {coeff}")
                            adj_rps = prev["rps"]+coeff*(next["rps"]-prev["rps"]) # the adjusted rps
                            adj_cpu = prev["cpu"]+coeff*(next["cpu"]-prev["cpu"]) # the adjusted cpu
                            adj_mem = prev["mem"]+coeff*(next["mem"]-prev["mem"]) # the adjusted mem
                            adj_p95 = prev["p95"]+coeff*(next["p95"]-prev["p95"]) # the adjusted p95
                            # print(f"Replicas: {replicas}, RPS: {rps}, CPU: {adj_cpu}, memory: {adj_mem}, p95: {adj_p95}")
                            break 

        return adj_rps, adj_cpu, adj_mem, adj_p95