# Deploy to K8 Cluster with Ingress and Domain

## Terraform Deployment of K8 Cluster:
Digital Ocean(DO) API Token for Terraform:
```bash
export TF_VAR_do_token='your-token'
```
```bash
terraform init
```
```bash
terraform plan
```
```bash
terraform apply
```

Login into Digital Ocean account and add cluster credentials to kubectl--refer to DO documentation.


## Basic Ingress Configuration
Ingress configuration reference: https://www.digitalocean.com/community/tutorials/how-to-set-up-an-nginx-ingress-with-cert-manager-on-digitalocean-kubernetes
Run through slowly and may need to be reran to get it working.
Run file to apply all the K8 manifest files:

Apply ingress controller specifically for Digital Ocean. (Modify for other providers)
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.1.1/deploy/static/provider/do/deploy.yaml
```
Confirm Ingress is running:
```bash
kubectl get pods -n ingress-nginx \
  -l app.kubernetes.io/name=ingress-nginx --watch
```
Confirm LB is running:
```bash
kubectl get svc --namespace=ingress-nginx
```

Ensure file is modified for your domain before applying:
```bash
kubectl apply -f ingress.yaml
kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.7.1/cert-manager.yaml
```

Apply remaining 
```bash
# Optional
#kubectl create -f staging_issuer.yaml
kubectl create -f prod_issuer.yaml
```
```bash
kubectl apply -f ingress_nginx_svc.yaml
```
Wait until certificate has been created:
```bash
kubectl describe ingress
```
```bash
kubectl apply -f ingress.yaml
```
