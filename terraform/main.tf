terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.37"
    }
  }

  backend "s3" {
    bucket = "oaks-terraform-state"
    key    = "maisignal/terraform.tfstate"
    region = "eu-central-1"
  }
}
