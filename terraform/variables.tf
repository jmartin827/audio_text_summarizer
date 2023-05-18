variable "region" {
  default = "nyc1"
}

variable "instance_size" {
  default = "s-2vcpu-4gb"
}

variable "k8s_cluster_name" {
  default = "testcluster"
}

variable "k8s_version" {
  default = "1.26.3-do.0"
}

variable "k8s_pool_name" {
  default = "worker-pool"
}

variable "k8s_count" {
  default = "1"
}
