provider "aws" {
  profile = "default"
  region  = "eu-central-1"
}

data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_launch_template" "cr_launch_template" {
  name_prefix   = "cr_launch_template"
  image_id      = "ami-0a02ee601d742e89f"
  instance_type = "t2.micro"
}

resource "aws_autoscaling_group" "cr_autoscaling_group" {
  availability_zones = [data.aws_availability_zones.available.names[0], data.aws_availability_zones.available.names[1]]
  desired_capacity   = 1
  max_size           = 1
  min_size           = 1

  launch_template {
    id      = aws_launch_template.cr_launch_template.id
    version = "$Latest"
  }
}