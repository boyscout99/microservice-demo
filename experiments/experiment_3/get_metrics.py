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
import matplotlib.pyplot as plt
from scipy.stats import linregress
from rewardFunction import reward_function as rf

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
                    # print("Note - Load too low!")
                    # coeff = np.abs((load-0)/(metric_list[0]["load"]-0)) # relative distance wrt the first element
                    # # print(f"coeff: {coeff}")
                    # for metric in self.metrics:
                    #     results.update( {metric: coeff*(metric_list[0][metric]-0)} ) # the adjusted value
                    # break
                    # perform linear regression for each metric on the last 10 values
                    # take first 20 elements to perform linear regression
                    d = metric_list[:20] # list of dictionaries
                    # create array of 10 elements for x
                    x = []
                    for i in range(len(d)):
                        x.append(d[i]['load'])
                    # print(f"metric: load, x: {x}")
                    x2 = [i for i in x] # add last element for plotting
                    x2.insert(0,load)
                    # loop each metric
                    for m in self.metrics:
                        # take first 20 values for one metric
                        y = []
                        for i in range(len(d)):
                            y.append(d[i][m])
                        # print(f"metric: {m}, y: {y}")
                        # compute linear regression
                        res = linregress(x,y)
                        # y = ax + b -> metric = res.slope*load + res.intercept
                        y_final = res.slope*load + res.intercept
                        results.update({m: y_final}) # the adjusted value
                        # print(f"results: {results}")
                        # # plot results
                        # y.append(y_final)
                        # plt.plot(x2, y, 'o', label='Original data')
                        # x_np = np.array(x)
                        # plt.plot(x_np, res.slope*x_np + res.intercept, label='Fitted line')
                        # plt.title(f"{m}")
                        # plt.xlabel('load')
                        # plt.ylabel(f"{m}")
                        # plt.legend()
                        # plt.show()
                elif (load>metric_list[-1]["load"]):
                    # print("Note - Load too high!")
                    # do some linear regression to estimate the coefficent
                    # perform linear regression for each metric on the last 10 values
                    # take last 20 elements to perform linear regression
                    d = metric_list[-20:] # list of dictionaries
                    # create array of 10 elements for x
                    x = []
                    for i in range(len(d)):
                        x.append(d[i]['load'])
                    # print(f"metric: load, x: {x}")
                    x2 = [i for i in x] # add last element for plotting
                    x2.append(load)
                    # loop each metric
                    for m in self.metrics:
                        # take last 10 values for one metric
                        y = []
                        for i in range(len(d)):
                            y.append(d[i][m])
                        # print(f"metric: {m}, y: {y}")
                        # compute linear regression
                        res = linregress(x,y)
                        # y = ax + b -> metric = res.slope*load + res.intercept
                        y_final = res.slope*load + res.intercept
                        results.update({m: y_final}) # the adjusted value
                        # print(f"results: {results}")
                        # plot results
                        # y.append(y_final)
                        # plt.plot(x2, y, 'o', label='Original data')
                        # x_np = np.array(x)
                        # plt.plot(x_np, res.slope*x_np + res.intercept, label='Fitted line')
                        # plt.title(f"{m}")
                        # plt.xlabel('load')
                        # plt.ylabel(f"{m}")
                        # plt.legend()
                        # plt.show()
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
    
    def plot_data(self):
        # For each number of replicas
        for elem in self.data:
            # get current replicas
            rep = elem['rep']
            # skip first 10 elements
            d = elem['metric_rows'][5:]
            # create x-axis, common to all metrics
            x = []
            # iterate over every sample in the list of dicts
            for sample in d:
                # create x axis with load
                x.append(sample['load'])
            # Create y-axis for each metric and plot
            for m in self.metrics:
                y = []
                if m == 'p95':
                    rewards = []
                    for sample in d:
                        # create y axis with metric value
                        y.append(sample[m])
                        # compute reward
                        rew = rf.rew_fun(sample[m], 5, 5, 15, rep)
                        rewards.append(rew)
                else:
                    for sample in d:
                        # create y axis with metric value
                        y.append(sample[m])
                # Plot each metric in the same graph
                # Do a linear regression to show the trend
                res = linregress(x,y)
                plt.plot(x, y, 'o', label=f'Original data {m}')
                x_np = np.array(x)
                plt.plot(x_np, res.slope*x_np + res.intercept, label=f'Fitted line {m}')

            # plt.plot(x, [i/100 for i in rewards], label='rewards/100')  
            plt.plot(x,rewards, label='rewards')  
            # Show all metrics for the same replica number
            plt.xlabel('load')
            # plt.ylabel(f"{m}")
            plt.legend()
            plt.title(f"Replicas: {rep}")
            plt.show()

    def optimal_rep_given_workload(self, load):
        """
        Based on the data, plot the optimal number of
        replicas for each load.
        Inputs: 
            - workload -> list
            - data -> sorted list of dict
        """
        # For each replica, workload, get metric approximation for p95
        all_rep = [] 
        for rep in range(1,16):
            all_rep.append(self.get_metrics_approx(rep, load))
        # print(f"all_rep: {all_rep}")
        for i in range(len(all_rep)):
            if all_rep[i]['p95']<5:
                return all_rep[i]['rep'], all_rep[i]['p95']
        print('Error - no optimal replica found')
        return
    
                