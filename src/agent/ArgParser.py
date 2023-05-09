import argparse

class StringProcessor:
    def __init__(self):
        self.deployment = None
        self.namespace = None
        self.cluster = None
        self.model = None
        self.rew_fun = None
    
    def parse_args(self):
        # Parse arguments
        parser = argparse.ArgumentParser()
        parser.add_argument("--deployment", type=str, required=True,
                            help="The deployment: e.g. frontend or paymentservice")
        parser.add_argument("--namespace", type=str, required=True,
                            help="The namespace: e.g. rl-agent-e1 or rl-agent-e2")
        parser.add_argument("--cluster", type=str, required=True,
        help="The cluster: e.g. GKE or minikube")
        parser.add_argument("--model", type=str, required=True,
                            help="The SB3 model: e.g. A2C or PPO")
        parser.add_argument("--rew_fun", type=str, required=True,
                            help="The reward function: e.g. indicator or quadratic")
        try:
            args = parser.parse_args()
            self.deployment = args.deployment
            self.namespace = args.namespace
            self.cluster = args.cluster
            self.model = args.model
            self.rew_fun = args.rew_fun
        except Exception as e:
            print(f"Unexpected error occurred: {e}\nCheck arguments.")

        return self.deployment, self.namespace, self.cluster, self.model, self.rew_fun