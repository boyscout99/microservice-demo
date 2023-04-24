
---
# Deploying an intelligent autoscaler into a Kubernetes cluster

The purpose of this repository is to train an agent with reinforcement learning so that it can outperform a standard [Horizontal Pod Autoscaler (HPA)](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/) by allocating resources in a smarter way.

The microservice architecture that it is used is built upon [GoogleCloudPlatform/microservices-demo](https://github.com/GoogleCloudPlatform/microservices-demo) v0.5.2. Based on that repository, an RL agent has been developed to take scaling decisions and actually scale-out or -in the services of the Online Boutique when run in Kubernetes.

*Picture of the microservice architecture.*

In the following, there is a guide to deploy the agent locally using [minikube](https://minikube.sigs.k8s.io/docs/start/) and a guide to deploy it in a [Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine) cluster.
The local development environment is used mainly for testing the interaction between the agent, the [Prometheus API](https://prometheus.io/docs/prometheus/latest/querying/api/) and the [Kubernetes API](https://kubernetes.io/docs/concepts/overview/kubernetes-api/).
While the GKE cluster is used to check the actual behaviour of the algorithm in a more realistic environment, and to compare the standard HPA with the intelligent autoscaler.
These steps are required to run the very basic agent inside the cluster.

So take your cup of coffee or tea and let's begin! ☕️

## Developing locally on minikube 💻 (☕️ sip #1)

##### Starting minikube and building images
1. `minikube start`
2. `minikube mount ${HOME}/Documents/microservice-demo:/app/microservice-demo` to mount the volume that will be used by the agent pod to run the code developed locally
3. Open a new terminal
4. `minikube docker-env` and `eval $(minikube -p minikube docker-env)`
5. `cd src/agent-local`
6. `docker build -t agent:<version> .` Remember to change the version of the image in the deployment file to deploy that image in the cluster.
7. `cd src/loadgenerator`
8. `docker build -t loadgenerator:<version> .`

##### Use Istio for monitoring
1. Install Istio following the [official documentation](https://istio.io/latest/docs/setup/getting-started/#download).
2. `istioctl install --set profile=demo -y` this will allow you to use Prometheus and Grafana
3. `kubectl label namespace rl-agent istio-injection=enabled`
4. Verify the labelling with `kubectl get namespaces --show-labels`
5. `cd kubernetes-manifests/`
6. `kubectl -f apply ./istio-system` to deploy Istio components

##### Deploy the Online Boutique application
1. Go to `kubernetes-manifests/rl-agent/local`
4. `kubectl apply -f kube-manifests-local.yaml`
6. `kubectl apply -f loadgenerator-local.yaml`
7. `kubectl apply -f agent-role.yaml`
8. `kubectl apply -f agent-roleBind.yaml`
9. `kubectl apply -f agent-local.yaml`
10. On a new terminal, to run the load generator execute the file `workload_gen.py` from within the pod. `kubectl exec -it -n rl-agent loadgenerator-<id> -- /bin/sh`
11. On a new terminal, to run the agent code execute `kubectl exec -it -n rl-agent agent-<id> -- /bin/sh`

>[!danger] REMEMBER that when creating a volume, everything you modify in the pod (including deleted files) will be reflected on the host volume!

>[!note] To delete all resources in the cluster in a namespace `kubectl delete all --all`.

---

## Developing on a cloud platform ☁️
Here the agent is deployed in a cloud environment that is similar to what will happen in the real world. Mainly considering the fact that it is scalable, compared to the local development case in which everything runs in a single node in a laptop.

>[!warning] Cloud computing comes with a cost 💸🏭
>Using GKE, you will be charged for the resources you use.
>The main costs will occur for the following resources:
> - [Compute Engine](https://cloud.google.com/compute/all-pricing), VM instance
> - [Filestore](https://cloud.google.com/filestore/pricing), NFS server instance
> - [Kubernetes Engine](https://cloud.google.com/kubernetes-engine/pricing), for the nodes
> - [Container Registry](https://cloud.google.com/container-registry/pricing), to store container images

*Picture of the infrastructure*.

### Setting up all components
First things first, you have to create a project with you Google account on Google Cloud Platform as indicated [in the official documentation](https://cloud.google.com/resource-manager/docs/creating-managing-projects).
The following components are needed to have everything working on GKE.
Specifically, we will connect to the Kubernetes cluster with a virtual machine and manage it from there.

#### Virtual Machine (VM) as main workstation to connect to the Kubernetes cluster
This VM will be used to use commands like `kubectl` and `git pull` the latest changes from the repository when developing.

1. [Create a VM instance](https://cloud.google.com/compute/docs/instances/create-start-instance) with at least 2 vCPUs, 4GB of memory, 20GB of disk and Ubuntu as OS.
2. SSH to the machine from your local computer or from the browser. You can use `gcloud compute ssh --zone "<your_zone>" "<vm_instance_name>" --project "<your_proect-name>"` or directly from the user interface in GCP.

##### What to install in the Ubuntu VM
- **gcloud SDK**: [follow these instructions to install the SDK](https://cloud.google.com/sdk/docs/install#deb) and then
	1. Install the package to authenticate with GKE `sudo apt-get install google-cloud-cli-gke-gcloud-auth-plugin` 
	2. Install the Kubernetes command line if not already present with`sudo apt-get install kubectl`
- **GitHub CLI**: [follow these instructions to install gh](https://github.com/cli/cli/blob/trunk/docs/install_linux.md), which will be necessary to authenticate to GitHub, push and pull changes to the repository. The complete command is reported below.
```
type -p curl >/dev/null || (sudo apt update && sudo apt install curl -y)
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
&& sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
&& sudo apt update \
&& sudo apt install gh -y
```
- **Docker**: [follow these instructions to install Docker](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository) and `sudo chmod 666 /var/run/docker.sock` after the installation to provide the right permissions to access Docker socket.

#### Network Files System (NFS) server as shared persistent disk
A persistent disk that can be shared across all components is necessary because virtual machines and containers are by definition ephemeral and there is no guarantee that data will be available across sessions. A NFS server will be used to share storage between the VM and pods.

You can [follow these guidelines](https://cloud.google.com/filestore/docs/create-instance-console) to set up a NFS server with [Google Filestore](https://cloud.google.com/filestore/docs).
On the VM:
1. Change directory and go into the mounted volume `cd /mnt/<dir_name>` 
2. Create folder `keys/` to store the secret keys.
3. Clone this repository with `git clone`.

>[!warning] If the VM is restarted you need to remount the volume (the address of the NFS server may have changed)
>`sudo mount <nfs_server_ip_address>:/vol1 /mnt/nfs-client`
>`sudo chmod go+rw /mnt/nfs-client`

This volume will be claimed by certain pods using a [Persistent Volume Claim](https://kubernetes.io/docs/concepts/storage/persistent-volumes/).

### Create a GKE cluster 
You can follow the [official documentation] to set up your standard cluster. Machine type `e2-standard-4` are sufficient with capacity to run the application and scale it.

### Time to authenticate to the cluster (☕️ sip #3)
From within the VM run the following commands.

1. Authenticate to the platform with your Google account with `gcloud auth login`
2. Enter the project you created with  `gcloud config set project PROJECT_ID`
3. Log into the cluster with `gcloud container clusters get-credentials <cluster-name> --zone <zone_of_your_cluster>`
4. You can try to create a namespace with `kubectl create namespace rl-agent`

To push Docker images in the Container Registry at `gcr.io/<your_project_name>` you will need to authenticate Docker to the Registry. 
You can follow the [official documentation](https://cloud.google.com/artifact-registry/docs/docker/authentication) to show how to authenticate or simply run `gcloud auth configure-docker`. 

To enable Kubernetes pull the container images from your private Container Registry you have to create a [Kubernetes secret](https://kubernetes.io/docs/concepts/configuration/secret/)

Point to the key file from a service account with Viewer permissions and name it `gcr-json-key`
To create a secret for Kubernetes
```
kubectl create secret docker-registry gcr-json-key \
--docker-server=gcr.io \
--docker-username=_json_key \
--docker-password="$(cat ~/keys/img_pull_key.json)" \
--docker-email=gke-pull-image@master-thesis-hpa.iam.gserviceaccount.com \
--namespace rl-agent
```

👉 Do the same also for the default namespace for loadgenerator.

Check that it has been created with `kubectl get secrets`

Create a secret for agent to authenticate to the GKE cluster from a pod.

create a new key file to authenticate to GKE and use Kubernetes API → use default service account
Like this:
create a key to connect to GKE API for that service account from IAM UI or with `gcloud iam service-accounts keys create KEY_FILE --iam-account=SA_NAME@PROJECT_ID.iam.gserviceaccount.com`

>[!warning] Security: This secret will be copied directly into the image. It could be a security concern.

### Monitoring installations
Follow [this](https://chrisedrego.medium.com/kubernetes-monitoring-kube-state-metrics-df6546aea324) tutorial to install the kube-state-metrics server. 
1. download repository `git clone https://github.com/kubernetes/kube-state-metrics`
2. apply manifest `kubectl apply -f kube-state-metrics/examples/standard/`
You should see a pod named like `kube-state-metrics-65bf754b96-cvp75`.
Install `kube-state-metrics` server from [https://github.com/kubernetes/kube-state-metrics](https://github.com/kubernetes/kube-state-metrics).

#### Service mesh with Istio (by this time the coffee would be cold, finish it!)
What is Istio and how to enable it. Following the [official documentation]().

`istioctl install --set profile=demo -y`

`kubectl label namespace rl-agent istio-injection=enabled`

##### Enabling Prometheus and Grafana
Copy the deployment files for Grafana, Prometheus, Kiali from Istio 1.17.1 in the repository, then ideally deploy an Istio folder with all required manifests inside.

Enable istio injection in both namespaces.
`kubectl label namespace rl-agent istio-injection=enabled`
`kubectl label namespace default istio-injection=enabled`

`kubectl apply -f kubernetes-manifests/istio-system`

2. cd `microservice-demo/`
3. `cd src/agent`
4. `docker build -t agent:x.x .`
5. `docker tag agent:x.x gcr.io/master-thesis-hpa/agent:x.x`
6. `docker push gcr.io/master-thesis-hpa/agent:x.x`
7. `skaffold run --default-repo gcr.io/master-thesis-hpa`
8. `cd kubernetes-manifests/rl-agent`
9. apply the role `agent-role.yaml` and `agent-roleBind.yaml`
10. `kubectl apply -f ./app`
11. start the HPA for frontend in default namespace
12. start the load in both namespaces and the agent

#### Using the loadgenerator
Update images. Update version in `/kubernetes-manifests/loadgenerator.yaml` and re-deploy it.
>[!warning] Update image version both in `/kubernetes-manifests/default/app` and `kubernetes-manifests/rl-agent/app`

#### Using the HPA
In the folder `/autoscaler` developing different versions of the HPA as YAML files.
Always for the `default` namespace though.

#### Developing the RL agent
Update images. Update version in `/src/agent/agent.yaml`.

---
# Resources
Tutorials I used and other references.
[How to a pull Docker Image from GCR in any non-GCP Kubernetes cluster](https://medium.easyread.co/today-i-learned-pull-docker-image-from-gcr-google-container-registry-in-any-non-gcp-kubernetes-5f8298f28969).
[Google Kubernetes Engine(GKE) — Persistent Volume with Persistent Disks (NFS) on Multiple Nodes (ReadWriteMany)](https://medium.com/@athulravindran/google-kubernetes-engine-gke-persistence-volume-nfs-on-multiple-nodes-readwritemany-4b6e8d565b08).



---
<p align="center">
<img src="src/frontend/static/icons/Hipster_HeroLogoMaroon.svg" width="300" alt="Online Boutique" />
</p>


![Continuous Integration](https://github.com/GoogleCloudPlatform/microservices-demo/workflows/Continuous%20Integration%20-%20Main/Release/badge.svg)

**Online Boutique** is a cloud-first microservices demo application.
Online Boutique consists of an 11-tier microservices application. The application is a
web-based e-commerce app where users can browse items,
add them to the cart, and purchase them.

**Google uses this application to demonstrate use of technologies like
Kubernetes/GKE, Istio, Stackdriver, and gRPC**. This application
works on any Kubernetes cluster, as well as Google
Kubernetes Engine. It’s **easy to deploy with little to no configuration**.

If you’re using this demo, please **★Star** this repository to show your interest!

> 👓**Note to Googlers (Google employees):** Please fill out the form at
> [go/microservices-demo](http://go/microservices-demo) if you are using this
> application.

## Screenshots

| Home Page                                                                                                         | Checkout Screen                                                                                                    |
| ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| [![Screenshot of store homepage](./docs/img/online-boutique-frontend-1.png)](./docs/img/online-boutique-frontend-1.png) | [![Screenshot of checkout screen](./docs/img/online-boutique-frontend-2.png)](./docs/img/online-boutique-frontend-2.png) |

## Quickstart (GKE)

[![Open in Cloud Shell](https://gstatic.com/cloudssh/images/open-btn.svg)](https://ssh.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https%3A%2F%2Fgithub.com%2FGoogleCloudPlatform%2Fmicroservices-demo&shellonly=true&cloudshell_image=gcr.io/ds-artifacts-cloudshell/deploystack_custom_image)

1. **[Create a Google Cloud Platform project](https://cloud.google.com/resource-manager/docs/creating-managing-projects#creating_a_project)** or use an existing project. Set the `PROJECT_ID` environment variable and ensure the Google Kubernetes Engine and Cloud Operations APIs are enabled.

```
PROJECT_ID="<your-project-id>"
gcloud services enable container.googleapis.com --project ${PROJECT_ID}
```

2. **Clone this repository.**

```
git clone https://github.com/GoogleCloudPlatform/microservices-demo.git
cd microservices-demo
```

3. **Create a GKE cluster.**

- GKE autopilot mode (see [Autopilot
overview](https://cloud.google.com/kubernetes-engine/docs/concepts/autopilot-overview)
to learn more):

```
REGION=us-central1
gcloud container clusters create-auto onlineboutique \
    --project=${PROJECT_ID} --region=${REGION}
```

- GKE Standard mode:

```
ZONE=us-central1-b
gcloud container clusters create onlineboutique \
    --project=${PROJECT_ID} --zone=${ZONE} \
    --machine-type=e2-standard-2 --num-nodes=4
```

4. **Deploy the sample app to the cluster.**

```
kubectl apply -f ./release/kubernetes-manifests.yaml
```

5. **Wait for the Pods to be ready.**

```
kubectl get pods
```

After a few minutes, you should see:

```
NAME                                     READY   STATUS    RESTARTS   AGE
adservice-76bdd69666-ckc5j               1/1     Running   0          2m58s
cartservice-66d497c6b7-dp5jr             1/1     Running   0          2m59s
checkoutservice-666c784bd6-4jd22         1/1     Running   0          3m1s
currencyservice-5d5d496984-4jmd7         1/1     Running   0          2m59s
emailservice-667457d9d6-75jcq            1/1     Running   0          3m2s
frontend-6b8d69b9fb-wjqdg                1/1     Running   0          3m1s
loadgenerator-665b5cd444-gwqdq           1/1     Running   0          3m
paymentservice-68596d6dd6-bf6bv          1/1     Running   0          3m
productcatalogservice-557d474574-888kr   1/1     Running   0          3m
recommendationservice-69c56b74d4-7z8r5   1/1     Running   0          3m1s
redis-cart-5f59546cdd-5jnqf              1/1     Running   0          2m58s
shippingservice-6ccc89f8fd-v686r         1/1     Running   0          2m58s
```

7. **Access the web frontend in a browser** using the frontend's `EXTERNAL_IP`.

```
kubectl get service frontend-external | awk '{print $4}'
```

*Example output - do not copy*

```
EXTERNAL-IP
<your-ip>
```

**Note**- you may see `<pending>` while GCP provisions the load balancer. If this happens, wait a few minutes and re-run the command.

8. [Optional] **Clean up**:

```
gcloud container clusters delete onlineboutique \
    --project=${PROJECT_ID} --zone=${ZONE}
```

## Use Terraform to provision a GKE cluster and deploy Online Boutique

The [`/terraform` folder](terraform) contains instructions for using [Terraform](https://www.terraform.io/intro) to replicate the steps from [**Quickstart (GKE)**](#quickstart-gke) above.

## Other deployment variations

- **Istio**: [See these instructions.](docs/service-mesh.md)
- **Anthos Service Mesh**: [See these instructions](/docs/service-mesh.md)
- **non-GKE clusters (Minikube, Kind)**: see the [Development Guide](/docs/development-guide.md)

## Deploy Online Boutique variations with Kustomize

The [`/kustomize` folder](kustomize) contains instructions for customizing the deployment of Online Boutique with different variations such as:
* integrating with [Google Cloud Operations](kustomize/components/google-cloud-operations/)
* replacing the in-cluster Redis cache with [Google Cloud Memorystore (Redis)](kustomize/components/memorystore) or [Google Cloud Spanner](kustomize/components/spanner)
* etc.

## Architecture

**Online Boutique** is composed of 11 microservices written in different
languages that talk to each other over gRPC.

[![Architecture of
microservices](./docs/img/architecture-diagram.png)](./docs/img/architecture-diagram.png)

Find **Protocol Buffers Descriptions** at the [`./pb` directory](./pb).

| Service                                              | Language      | Description                                                                                                                       |
| ---------------------------------------------------- | ------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| [frontend](./src/frontend)                           | Go            | Exposes an HTTP server to serve the website. Does not require signup/login and generates session IDs for all users automatically. |
| [cartservice](./src/cartservice)                     | C#            | Stores the items in the user's shopping cart in Redis and retrieves it.                                                           |
| [productcatalogservice](./src/productcatalogservice) | Go            | Provides the list of products from a JSON file and ability to search products and get individual products.                        |
| [currencyservice](./src/currencyservice)             | Node.js       | Converts one money amount to another currency. Uses real values fetched from European Central Bank. It's the highest QPS service. |
| [paymentservice](./src/paymentservice)               | Node.js       | Charges the given credit card info (mock) with the given amount and returns a transaction ID.                                     |
| [shippingservice](./src/shippingservice)             | Go            | Gives shipping cost estimates based on the shopping cart. Ships items to the given address (mock)                                 |
| [emailservice](./src/emailservice)                   | Python        | Sends users an order confirmation email (mock).                                                                                   |
| [checkoutservice](./src/checkoutservice)             | Go            | Retrieves user cart, prepares order and orchestrates the payment, shipping and the email notification.                            |
| [recommendationservice](./src/recommendationservice) | Python        | Recommends other products based on what's given in the cart.                                                                      |
| [adservice](./src/adservice)                         | Java          | Provides text ads based on given context words.                                                                                   |
| [loadgenerator](./src/loadgenerator)                 | Python/Locust | Continuously sends requests imitating realistic user shopping flows to the frontend.                                              |

## Features

- **[Kubernetes](https://kubernetes.io)/[GKE](https://cloud.google.com/kubernetes-engine/):**
  The app is designed to run on Kubernetes (both locally on "Docker for
  Desktop", as well as on the cloud with GKE).
- **[gRPC](https://grpc.io):** Microservices use a high volume of gRPC calls to
  communicate to each other.
- **[Istio](https://istio.io):** Application works on Istio service mesh.
- **[Cloud Operations (Stackdriver)](https://cloud.google.com/products/operations):** Many services
  are instrumented with **Profiling** and **Tracing**. In
  addition to these, using Istio enables features like Request/Response
  **Metrics** and **Context Graph** out of the box. When it is running out of
  Google Cloud, this code path remains inactive.
- **[Skaffold](https://skaffold.dev):** Application
  is deployed to Kubernetes with a single command using Skaffold.
- **Synthetic Load Generation:** The application demo comes with a background
  job that creates realistic usage patterns on the website using
  [Locust](https://locust.io/) load generator.

## Local Development

If you would like to contribute features or fixes to this app, see the [Development Guide](/docs/development-guide.md) on how to build this demo locally.

## Demos featuring Online Boutique

- [Use Helm to simplify the deployment of Online Boutique, with a Service Mesh, GitOps, and more!](https://medium.com/p/246119e46d53)
- [How to reduce microservices complexity with Apigee and Anthos Service Mesh](https://cloud.google.com/blog/products/application-modernization/api-management-and-service-mesh-go-together)
- [gRPC health probes with Kubernetes 1.24+](https://medium.com/p/b5bd26253a4c)
- [Use Google Cloud Spanner with the Online Boutique sample](https://medium.com/p/f7248e077339)
- [Seamlessly encrypt traffic from any apps in your Mesh to Memorystore (redis)](https://medium.com/google-cloud/64b71969318d)
- [Strengthen your app's security with Anthos Service Mesh and Anthos Config Management](https://cloud.google.com/service-mesh/docs/strengthen-app-security)
- [From edge to mesh: Exposing service mesh applications through GKE Ingress](https://cloud.google.com/architecture/exposing-service-mesh-apps-through-gke-ingress)
- [Take the first step toward SRE with Cloud Operations Sandbox](https://cloud.google.com/blog/products/operations/on-the-road-to-sre-with-cloud-operations-sandbox)
- [Deploying the Online Boutique sample application on Anthos Service Mesh](https://cloud.google.com/service-mesh/docs/onlineboutique-install-kpt)
- [Anthos Service Mesh Workshop: Lab Guide](https://codelabs.developers.google.com/codelabs/anthos-service-mesh-workshop)
- [KubeCon EU 2019 - Reinventing Networking: A Deep Dive into Istio's Multicluster Gateways - Steve Dake, Independent](https://youtu.be/-t2BfT59zJA?t=982)
- Google Cloud Next'18 SF
  - [Day 1 Keynote](https://youtu.be/vJ9OaAqfxo4?t=2416) showing GKE On-Prem
  - [Day 3 Keynote](https://youtu.be/JQPOPV_VH5w?t=815) showing Stackdriver
    APM (Tracing, Code Search, Profiler, Google Cloud Build)
  - [Introduction to Service Management with Istio](https://www.youtube.com/watch?v=wCJrdKdD6UM&feature=youtu.be&t=586)
- [Google Cloud Next'18 London – Keynote](https://youtu.be/nIq2pkNcfEI?t=3071)
  showing Stackdriver Incident Response Management

---

This is not an official Google project.
