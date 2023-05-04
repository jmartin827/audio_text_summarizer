## Basic Digital Ocean Ingress Quick Start

Summarized from this guide:
https://www.digitalocean.com/community/tutorials/how-to-set-up-an-nginx-ingress-with-cert-manager-on-digitalocean-kubernetes

# Deploy services:
```bash
kubectl apply -f ../kustomization.yaml
```

Verify everything is ready:
```bash
kubectl get svc
kubectl get pods
```

Kubernetes Nginx Ingress Controller
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.1.1/deploy/static/provider/do/deploy.yaml
```

Verify two pods completed and one is running:
```bash
kubectl get pods -n ingress-nginx \
  -l app.kubernetes.io/name=ingress-nginx --watch
  ```

Verify that the ingress-nginx-controller has an external IP address:
```bash
kubectl get svc --namespace=ingress-nginx
```

Add in DNS records pointing to Load Balancer and confirm with CURL:
Failed curl for .dev... might be domain type specific as it's ssl only

Apply the cert manager:
```bash
kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.7.1/cert-manager.yaml
```

Roll out staging:
```bash
kubectl create -f staging_issuer.yaml
```
(Note that certificates will only be created after annotating and 
updating the Ingress resource provisioned in the previous step.)

Roll out prod: (This is likely pointless and should be removed)
```bash
kubectl create -f prod_issuer.yaml
```


Only required as a Digital Ocean Workaround:
```bash
kubectl apply -f ingress_nginx_svc.yaml
```


Use with staging issuer:
```bash
kubectl apply -f ingress.yaml
```

Validate there is a created certificate:
```bash
kubectl describe ingress
```

Validate:
```bash
wget --save-headers -O- echo1.example.com
```


Use with production issuer:
```bash
kubectl apply -f ingress.yaml
```

Verify:
```bash
kubectl describe certificate echo-tls
```
