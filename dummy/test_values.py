# Consequences of the action on the environment
import json

def create_values():
    data = []

    for rep in range(0, 30):
        rep +=1
        if rep == 1:
            # decrease CPU utilisation
            # cpu = 150
            cpu = 500
            # decrease memory utilisation
            # mem = 0.6
            mem = 2.2
            # decrease service latency
            # t = 45 
            t = 180
            # decrease RPS
            # rps = 650
            rps = 2600
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

        # Store the values in a dictionary
        values = {
            "rps": rps,
            "cpu": cpu,
            "mem": mem,
            "t": t
        }
        
        # Append the dictionary to the data list
        data.append(values)

    return data

if __name__ == "__main__":
    # Save the data to a JSON file
    data = create_values()
    with open("data_3.json", "w") as file:
        json.dump(data, file, indent=4)

    print(f"data:\n{data}")
    print(data[29]["rps"])