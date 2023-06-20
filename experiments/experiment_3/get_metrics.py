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
    def __init__(self, data, metrics):
        # Reference data from a JSON
        self.data = data
        # List of metrics of the form ['rps', 'cpu', ...]
        self.metrics = metrics

    def get_metrics_approx(self, replicas, load):
        results = {'rep': replicas}
        for elem in range(len(self.data)):
            # search for the intended number of replicas
            if self.data[elem]["rep"] == replicas:
                # search for the given RPS (load)
                metric_list = self.data[elem]["metric_rows"]
                # print("Metric_list: ", metric_list)
                # print(f"elem {data[elem]['rps']} type: {type(data[elem]['rps'])}, elem+1 {data[elem+1]['rps']}")
                if (load<metric_list[0]["load"]): # case in which RPS is too low
                    print("Note - Load too low!")
                    coeff = np.abs((load-0)/(metric_list[0]["load"]-0)) # relative distance wrt the first element
                    # print(f"coeff: {coeff}")
                    for metric in self.metrics:
                        results.update( {metric: coeff*(metric_list[0][metric]-0)} ) # the adjusted value
                    break
                elif (load>metric_list[-1]["load"]):
                    # TODO estimate new coefficient
                    print("Note - Load too high!")
                    # do some linear regression to estimate the coefficent
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
                            for metric in self.metrics:
                                results.update( {metric: prev[metric]+coeff*(next[metric]-prev[metric])} ) # the adjusted value
                            break 

        return results