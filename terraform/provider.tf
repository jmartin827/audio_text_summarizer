terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
    }
  }
}

variable "DIGITALOCEAN_TOKEN" {}

provider "digitalocean" {
  token = var.DIGITALOCEAN_TOKEN
}