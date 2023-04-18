# This is a class to interact with Kubernetes API and scale a deployment
'''
This class is used to connect to the Kubernetes API and scale deployments.
'''
import os
from kubernetes import client, config
from kubernetes.client.rest import ApiException

class KubernetesEnvironment:

    def __init__(self, name, namespace, minReplicas, maxReplicas):
        self.name = name
        self.namespace = namespace
        self.minReplicas = minReplicas
        self.maxReplicas = maxReplicas
        self.api = None

        # Load the Kubernetes configuration
        if os.getenv('KUBERNETES_SERVICE_HOST'):
            config.load_incluster_config()
        else:
            config.load_kube_config()

        # Create an instance of the K8s API client
        self.api = client.AppsV1Api()

    def get_current_replicas(self):
        '''
        Get the current number of replicas for a deployment.
        '''
        try:
            # Get the current number of replicas of the Deployment
            deployment = self.api.read_namespaced_deployment_scale(
                name = self.name,
                namespace = self.namespace
            )
            if deployment.spec.replicas is not None:
                current_replicas = int(deployment.spec.replicas)
            else:
                current_replicas = self.minReplicas

            return current_replicas

        except ApiException as e:
            print("Exception when calling AppsV1Api->read_namespaced_deployment_scale: %s\n" % e)
            
            return None

    def update_replicas(self, action):
        '''
        Update the number of replicas by summing action to it.
        '''
        try:
            # Update the number of replicas
            current_replicas = self.get_current_replicas()

            if current_replicas is not None:

                deployment = self.api.read_namespaced_deployment_scale(
                    name = self.name,
                    namespace = self.namespace
                )

                if (current_replicas + action < self.minReplicas):
                    deployment.spec.replicas = self.minReplicas
                    print("Cannot have less than minReplicas. Setting to %d.", self.minReplicas)

                elif (current_replicas + action > self.maxReplicas):
                    deployment.spec.replicas = self.maxReplicas
                    print("Cannot have more than maxReplicas. Setting to %d.", self.maxReplicas)
                    
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
            deployment.spec.replicas = self.minReplicas

            self.api.replace_namespaced_deployment_scale(
                name = self.name,
                namespace = self.namespace,
                body = deployment
            )
            print("Reset to number of replicas: ", deployment.spec.replicas)

        except ApiException as e:
            print("Exception when calling AppsV1Api->replace_namespaced_deployment_scale: %s\n" % e)