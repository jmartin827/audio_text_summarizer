# Basic Digital Ocean Ingress Quick Start

Adapted from this article and tested with Digital Ocean.
https://www.digitalocean.com/community/tutorials/how-to-set-up-an-nginx-ingress-on-digitalocean-kubernetes-using-helm

1. Deploy services (base deployment) using main README.MD in root folder and verify everything is ready:
    ```bash
    kubectl get svc
    kubectl get pods
    ```
2. Deploy Nginx controller using helm
   (Note may be advisable to wait a few minutes after the cluster is provisioned)
   ```bash
   helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
   helm repo update
   helm install nginx-ingress ingress-nginx/ingress-nginx --set controller.publishService.enabled=true
   ```

3. Wait until load balancer has an external ip address:
   ```bash
   kubectl --namespace default get services -o wide -w nginx-ingress-ingress-nginx-controller
     ```

   Add in DNS records pointing to Load Balancer.
   If using cloudflare--ensure SSL/TLS is set to "Full" once the SSL cert is created or a redirect loop may occur.

4. Setup cert-manager and also apply the prod_issuer.yaml:

   (Update email in prod_issuer.yaml)
   ```bash
   kubectl create namespace cert-manager
   helm repo add jetstack https://charts.jetstack.io
   helm repo update
   helm install cert-manager jetstack/cert-manager --namespace cert-manager --version v1.10.1 --set installCRDs=true
   kubectl create -f prod_issuer.yaml
   ```

5. Apply the ingress files and confirm it's working with cURL.
   (Ensure the hosts are updated within the files)


   front_end_ingress.yaml: ReactJS front end for the domain root example.com
   
   back_end_ingress.yaml: Back end FastAPI Rest API for api.example.com
   
   back_end_ingress_root.yaml: Identical to above but for example.com and is a CORS workaround
   ```bash
   kubectl apply -f front_end_ingress.yaml
   ```
   ```bash
   kubectl apply -f back_end_ingress_api.yaml
   ```
   ```bash
   kubectl apply -f back_end_ingress_root.yaml
   ```

Validate there is a created certificate:
```bash
kubectl describe ingress
```

Validate:
```bash
wget --save-headers -O- echo1.example.com
```

Verify:
```bash
kubectl get certificate
```
