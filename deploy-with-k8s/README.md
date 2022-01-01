## Background

_**In Progress!**_

As mentioned in the main [README](../README.md), this is an experimental project mainly used for learning and practice. This time around, I am adapting it to deploy to and run using Kubernetes.

## requirements

* Docker - I have containerised the application with Docker to deploy to the cluster
  * If you are making changes, rebuild the Docker image, push it somewhere like dockerhub (I have used dockerhub)
    * Update the [Deployment file](whos-out.deployment.yaml)
* A Kubernetes cluster - I have kept it simple and used minikube to run things locally for now
* Kubectl for interacting with the cluster
  * Make sure you add the secrets to Kubernetes cluster for the BambooHR API key and domain.
    * Replace the 'replace-me-base64-encoded' holding text in the secret.yaml file and apply it with _**something like**_ `kubectl apply -f whos-out.secret.yaml`
  
## Deploying

_Notes for future reference..._

* `kubectl apply -f whos-out.secret.yaml`
* `kubectl apply -f whos-out.deployment.yaml`
* `kubectl apply -f whos-out.service.yaml`
* `kubectl port-forward service/whos-out 30518:5000`
  