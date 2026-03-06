data "aws_caller_identity" "current" {}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      project     = var.project
      environment = local.env
    }
  }
}
