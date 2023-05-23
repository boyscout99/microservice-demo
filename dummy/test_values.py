# Consequences of the action on the environment
import json
import math

def create_values():
    data = []
    for rep in range(0, 30):
        rep +=1
        if rep == 1:
            # decrease CPU utilisation
            cpu = "{:.3f}".format(130)
            # decrease memory utilisation
            mem = "{:.3f}".format(0.5)
            # decrease service latency
            t = "{:.3f}".format(30)
            # decrease RPS
            rps = "{:.3f}".format(550)
        elif rep > 5:
            # decrease CPU utilisation
            cpu = "{:.3f}".format(160.21*math.exp(-0.22*rep))
            # decrease memory utilisation
            mem = "{:.3f}".format(0.5)
            # block service latency to minimum
            t = "{:.3f}".format(4)
            # decrease rps
            rps = "{:.3f}".format(860.28*math.exp(-0.49*rep))
        else:
            # decrease CPU utilisation
            cpu = "{:.3f}".format(160.21*math.exp(-0.22*rep))
            # decrease memory utilisation
            mem = "{:.3f}".format(0.5)
            # decrease service latency
            t = "{:.3f}".format(49.55*math.exp(-0.54*rep))
            # decrease rps
            rps = "{:.3f}".format(860.28*math.exp(-0.49*rep))
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