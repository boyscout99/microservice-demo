# Consequences of the action on the environment
if __name__ == "__main__":

    print(f"### Increasing replicas ###")
    for rep in range(0, 30):
        rep +=1
        if rep == 1:
            # decrease CPU utilisation
            cpu = 150
            # decrease memory utilisation
            mem = 0.6
            # decrease service latency
            t = 45 
            # decrease RPS
            rps = 650
        elif rep == 2:
            # decrease CPU utilisation
            cpu = cpu - cpu*0.16
            # decrease memory utilisation
            mem = mem - mem*0.16
            # decrease service latency
            t = t - t*0.35
            # decrease RPS
            rps = rps - rps*0.46
        else:
            # decrease CPU utilisation
            cpu = cpu - cpu*0.16*(1.05**rep)
            # decrease memory utilisation
            mem = mem - mem*0.16*(1.05**rep)
            # decrease service latency
            t = t - t*0.35*(0.85**rep)
            # decrease rps
            rps = rps - rps*0.46*(0.9**rep)
        print(f"rep: {rep}, rps: {rps}, cpu: {cpu}, mem: {mem}, t: {t}")

    print("### Decreasing replicas ###")
    for rep in range(30,1,-1):
        rep -= 1
        # Consequences of the action on the environment
        if rep == 1:
            # increase CPU utilisation
            cpu = 150
            # increase memory utilisation
            mem = 0.6
            # increase service latency
            t = 45 
            # increase RPS
            rps = 650
        elif rep == 2:
            # increase CPU utilisation
            cpu = cpu + cpu*0.3/(1-0.3)
            # increase memory utilisation
            mem = mem + mem*0.2/(1-0.2)
            # increase service latency
            t = t + t*0.14/(1-0.14)
            # increase RPS
            rps = rps + rps*0.28/(1-0.28)
        else:
            # increase CPU utilisation
            cpu = cpu + cpu*(0.16*(1.052**rep)/(1-0.16*1.052**rep))
            # increase memory utilisation
            mem = mem + mem*(0.16*(1.053**rep)/(1-0.16*1.053**rep))
            # increase service latency
            t = t + t*(0.35*(0.85**rep)/(1-0.35*0.85**rep))
            # increase rps
            rps = rps + rps*(0.46*(0.8915**rep)/(1-0.46*(0.8915**rep)))
        print(f"rep: {rep}, rps: {rps}, cpu: {cpu}, mem: {mem}, t: {t}")