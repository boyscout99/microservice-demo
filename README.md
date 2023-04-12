
---
# Developing environment
 One local cluster for testing the interaction between the agent and the frontend, Prometheus and Grafana.
 One GKE cluster to check the actual behaviour and compare the two autoscalers.
 Use `skaffold` to deploy Online Boutique
	 - on `default` namespace
	 - on `rl-agent` namespace

Use the repo `microservice-demo` to build everything.
	- Folder `/agent` to develop the algorithm.
		- `Dockerfile` to build the container in the cluster so that it will call Prometheus API
	- Folder `/local-dev` for developing locally. 
		- Same address for Prometheus API?
	- Folder `/gke-dev` to develop on GKE.

Branches of the repository:
	- `master` main branch
	- `dev-agent` only to develop in `/src/agent` 
	- `dev-load` to modify loadgenerator and update Docker image
		- modify `/src/loadgenerator`
		- modify `/kubernetes-manifests/loadgenerator.yaml` for the version of the image
	- `dev-cluster` to modify anything else outside the two folders above

Then I have created `istio-prom.yaml` to deploy Istio with the kube-state-metric server → instructions on how to download repo and deploy.

## Local cluster
Refer to [[Create a local testing environment on Docker]].
No secrets needed.
Just to see behaviour of the agent and test the algorithm on one pod.
Build image locally on Docker → both loadgenerator and agent
	Create table with versions and updates.
| version | update | published to gcr.io |
| :---: | :---: | :---: |
| 0.2 | test | ✅ |
| 0.4.1 | working Prom API calls | ✅ |

### Set up
For the default namespace, deploy from `/default`, while for cluster with agent deploy from `/rl-agent`.
Documents in `/src` are the same for both deployments.
`/istio-system` is deployed in the namespace `istio-system`

Should create the following tree
```
- kubernetes-manifests/
	- istio-system/
		- prometheus.yaml 👉 updated version with kube-state-metrics
		- grafana.yaml
		- kiali.yaml
	- default/
		- istio-manifests/ 
			- allow-egress
			- frontend-gateway
			- frontend
		- app/ 👉 pulling images from gcr.io/google-example/
			- all services YAML 
			- loadgenerator.yaml
	- rl-agent/
		- istio-manifests/ 👉 modify namespace ✅
			- allow-egress
			- frontend-gateway
			- frontend
		- app/
			- all services YAML
			- loadgenerator.yaml
		- local/ 👉 with imagePullPolicy: Never ✅
			- agent-local.yaml
			- loadgenerator-local.yaml
			- kube-manifests-local.yaml
- src/
	- all services/
- autoscaler/
	- frontend/
		- hpa-v2.yaml
- skaffold.yaml 👉 one for default and for rl-agent deploy from folder after default
```


#### Guide to develop locally
1. `cd src/agent`
2. `docker build -t agent:x.x .`
3. `cd src/loadgenerator`
4. `docker build -t loadgenerator .`
5. go to `kubernetes-manifests/rl-agent/local`
6. `kubectl apply -f kube-manifests-local.yaml`
7. `kubectl apply -f loadgenerator-local.yaml`
8. `kubectl apply -f agent-local.yaml`
9. ❗️mount a volume on agent's Dockerfile with the folder `/src/agent`
10. `kubectl delete deployment -n rl-agent agent`
11. `kubectl apply -f deployment agent`

Use Istio and monitoring
1. `cd kubernetes-manifests/rl-agent`
2. `kubectl apply -f ./istio-manifests`
3. `cd kubernetes-manifests/`
4. `kubectl -f apply ./istio-system`

#### Guide to develop on GKE
1. `kubectl create namespace rl-agent`
2. cd `microservice-demo/`
3. `cd src/agent`
4. `docker build -t agent:x.x .`
5. `docker tag agent:x.x gcr.io/master-thesis-hpa/agent:x.x`
6. `docker push gcr.io/master-thesis-hpa/agent:x.x`
7. `skaffold run --default-repo gcr.io/master-thesis-hpa`
8. `cd kubernetes-manifests/default`
9. `kubectl apply -f `
>[!note] To delete all resources in the cluster in a namespace `kubectl delete all --all`.

1. build images
	1. locally: go to every /src/ and build one by one
2. deploy images
	1. locally: deploy with a single `kubectl apply -f` all services except `loadgenerator-local.yaml` and `agent-local.yaml`. Deploy kube-state-metrics, Prometheus and Grafana managed by Istio in `istio-system`. 
	2. on GKE: use `skaffold run --default-repo gcr.io/master-thesis-hpa` to deploy `default` namespace, then deploy `rl-agent` namespace with `kubectl apply -f` after building and uploading `agent` and `loadgenerator`.

#### Service mesh with Istio
What is Istio and how to enable it. Following the official documentations.

##### Enabling Prometheus and Grafana
Copy the deployment files for Grafana, Prometheus, Kiali from Istio 1.17.1 in the repository, then ideally deploy an Istio folder with all required manifests inside.

#### Using the loadgenerator
Deployed with skaffold, but activate it by executing inside the pod.
Update images. Update version in `/kubernetes-manifests/loadgenerator.yaml` and re-deploy it.
>[!warning] Update image version both in `/kubernetes-manifests/default/app` and `kubernetes-manifests/rl-agent/app`

#### Using the HPA
In the folder `/autoscaler` developing different versions of the HPA as YAML files.
Always for the `default` namespace though.

#### Developing the RL agent
In the folder agent. Can be deployed with `skaffold`.
Update images. Update version in `/src/agent/agent.yaml`.

## GKE cluster
Refer to [[Deploy GKE cluster from scratch]].
Copy the local developments to the repository.
Publish image to `gcr.io/master-thesis-hpa`, update version of image on Deployment file (*how to take always latest version? Should I create a template?*).

#### Set up
Using skaffold to deploy in namespaces `default` and `rl-agent`.

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
