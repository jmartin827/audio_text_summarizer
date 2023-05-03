terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
    }
  }
}


variable "do_token" {}

provider "digitalocean" {
  token = var.do_token
}