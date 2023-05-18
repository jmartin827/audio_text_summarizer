resource "digitalocean_kubernetes_cluster" "kubernetes_cluster" {
  name    = var.k8s_cluster_name
  region  = var.region
  version = var.k8s_version

  # This default node pool is mandatory
  node_pool {
    name       = var.k8s_pool_name
    size       = var.instance_size
    auto_scale = false
    node_count = var.k8s_count
    tags       = ["node-pool-tag"]
  }

}

output "cluster-id" {
  value = digitalocean_kubernetes_cluster.kubernetes_cluster.id
}

data "digitalocean_kubernetes_cluster" "example_cluster" {
  name = digitalocean_kubernetes_cluster.kubernetes_cluster.name
}

# TODO extract the kubeconfig from here and pass to fluxcd?