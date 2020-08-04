variable "aws_region" {
  default = "eu-central-1"
}

variable "cidr_block" {
  default = "10.0.0.0/16"
}

variable "public_subnet" {
  default = "10.0.1.0/24"
}

variable "private_subnet" {
  default = "10.0.2.0/24"
}

variable "domain_name" {
  default = "przypieczony.com"
}

variable "public_key_path" {
  description = <<DESCRIPTION
Path to the SSH public key to be used for authentication.
Ensure this keypair is added to your local SSH agent so provisioners can
connect.
Example: ~/.ssh/aws-key-pair.pub
DESCRIPTION
  default = "~/.ssh/aws-key-pair.pub"
}

variable "cert_path" {
  description = "path to cert"
}

variable "key_cert_path" {
  description = "path to cert key"
}

variable "key_name" {
  description = "Desired name of AWS key pair"
}
