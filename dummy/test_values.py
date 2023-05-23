# Consequences of the action on the environment
import json
import math

def create_values():
    data = []
    for rep in range(0, 30):
        rep +=1
        if rep == 1:
            # decrease CPU utilisation
            cpu = round(130, 3)
            # decrease memory utilisation
            mem = round(0.5, 3)
            # decrease service latency
            t = round(30, 3)
            # decrease RPS
            rps = round(550, 3)
        elif rep > 5:
            # decrease CPU utilisation
            cpu = round(160.21*math.exp(-0.22*rep), 3)
            # decrease memory utilisation
            mem = round(0.5, 3)
            # block service latency to minimum
            t = round(4, 3)
            # decrease rps
            rps = round(860.28*math.exp(-0.49*rep), 3)
        else:
            # decrease CPU utilisation
            cpu = round(160.21*math.exp(-0.22*rep), 3)
            # decrease memory utilisation
            mem = round(0.5, 3)
            # decrease service latency
            t = round(49.55*math.exp(-0.54*rep), 3)
            # decrease rps
            rps = round(860.28*math.exp(-0.49*rep), 3)
        print(f"rep: {rep}, t: {t}, rps: {rps}, cpu: {cpu}, mem: {mem}")

        # Store the values in a dictionary
        values = {
            "t": t,
            "rps": rps,
            "cpu": cpu,
            "mem": mem
        }
        
        # Append the dictionary to the data list
        data.append(values)

    return data

if __name__ == "__main__":
    # Save the data to a JSON file
    data = create_values()
    with open("data.json", "w") as file:
        json.dump(data, file, indent=4)

    print(f"data:\n{data}")
    print(data[2]["rps"])