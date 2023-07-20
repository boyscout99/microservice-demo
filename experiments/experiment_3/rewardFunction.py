import math

class reward_function:

    def rew_fun(resp_time, SLA_RESP_TIME, alpha, maxReplicas, current_replicas):
        delta_t = resp_time - SLA_RESP_TIME
        perc = delta_t / SLA_RESP_TIME
        if perc > 0:
            reward = -100 * perc
            # print(f"reward = -100 * {perc} = {reward}")
        else:
            reward = 10 * ((100 / alpha) * perc + 1) + (maxReplicas / current_replicas)
            # print(f"reward = 10 * ({100 / alpha} * {perc} + 1) + ({maxReplicas / current_replicas}) = {reward}")
        return reward