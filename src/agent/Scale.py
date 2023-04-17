# This is a class to interact with Kubernetes API and scale a deployment
import os
from kubernetes import client, config
from kubernetes.client.rest import ApiException

class KubernetesEnvironment:

    def __init__(self, name, namespace):
        self.name = name
        self.namespace = namespace
        self.api = None

        # Load the Kubernetes configuration
        if os.getenv('KUBERNETES_SERVICE_HOST'):
            config.load_incluster_config()
        else:
            config.load_kube_config()

        # Create an instance of the K8s API client
        self.api = client.AppsV1Api()

    def get_current_replicas(self):
        try:
            # Get the current number of replicas of the Deployment
            deployment = self.api.read_namespaced_deployment_scale(
                name = self.name,
                namespace = self.namespace
            )
            if deployment.spec.replicas is not None:
                current_replicas = int(deployment.spec.replicas)
            else:
                current_replicas = 1

            return current_replicas

        except ApiException as e:
            print("Exception when calling AppsV1Api->read_namespaced_deployment_scale: %s\n" % e)
            
            return None

    def update_replicas(self, action):
        try:
            # Update the number of replicas
            current_replicas = self.get_current_replicas()

            if current_replicas is not None:

                deployment = self.api.read_namespaced_deployment_scale(
                    name = self.name,
                    namespace = self.namespace
                )

                if (current_replicas + action <= 0):
                    deployment.spec.replicas = 1
                    print("Cannot have 0 replicas. Setting to 1.")
                else:
                    deployment.spec.replicas = current_replicas + action
                    print("New number of replicas: ", deployment.spec.replicas)

                self.api.replace_namespaced_deployment_scale(
                    name = self.name,
                    namespace = self.namespace,
                    body = deployment
                )

        except ApiException as e:
            print("Exception when calling AppsV1Api->replace_namespaced_deployment_scale: %s\n" % e)

    def reset_replicas(self):
        # Reset the number of replicas to 1
        try:
            deployment = self.api.read_namespaced_deployment_scale(
                name = self.name,
                namespace = self.namespace
            )
            deployment.spec.replicas = 1

            self.api.replace_namespaced_deployment_scale(
                name = self.name,
                namespace = self.namespace,
                body = deployment
            )
            print("Reset to number of replicas: ", deployment.spec.replicas)

        except ApiException as e:
            print("Exception when calling AppsV1Api->replace_namespaced_deployment_scale: %s\n" % e)