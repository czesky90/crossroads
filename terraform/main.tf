# Specify the provider and access details
provider "aws" {
  region = var.aws_region
}

# Create a VPC to launch our instances into
resource "aws_vpc" "cr_vpc" {
  cidr_block = var.cidr_block
}

# Create an internet gateway to give our subnet access to the outside world
resource "aws_internet_gateway" "cr_internet_gateway" {
  vpc_id = aws_vpc.cr_vpc.id
}

# Grant the VPC internet access on its main route table
resource "aws_route" "internet_access" {
  route_table_id         = aws_vpc.cr_vpc.main_route_table_id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.cr_internet_gateway.id
}

# Create a subnet to elb our instances into
resource "aws_subnet" "elb_subnet" {
  vpc_id                  = aws_vpc.cr_vpc.id
  cidr_block              = var.public_subnet
  map_public_ip_on_launch = true
}

# Create a subnet to launch our instances into
resource "aws_subnet" "cr_subnet" {
  vpc_id                  = aws_vpc.cr_vpc.id
  cidr_block              = var.private_subnet
  map_public_ip_on_launch = true
}

# A security group for the ELB so it is accessible via the web
resource "aws_security_group" "elb" {
  name        = "cr_elb_sg"
  description = "Used in the terraform"
  vpc_id      = aws_vpc.cr_vpc.id

  # HTTP access from anywhere
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # outbound internet access
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Our default security group to access
# the instances over SSH and HTTP
resource "aws_security_group" "ec2_sg" {
  name        = "cr_ec2_sg"
  description = "Used in the terraform"
  vpc_id      = aws_vpc.cr_vpc.id

  # SSH access from anywhere
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTP access from the VPC
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # outbound internet access
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_elb" "web" {
  name = "terraform-cr-elb"

  subnets         = [aws_subnet.cr_subnet.id, aws_subnet.elb_subnet.id]
  security_groups = [aws_security_group.elb.id]

  listener {
    instance_port     = 80
    instance_protocol = "http"
    lb_port           = 80
    lb_protocol       = "http"
  }
}

resource "aws_key_pair" "auth" {
  key_name   = var.key_name
  public_key = file(var.public_key_path)
}

resource "aws_launch_template" "cr_launch_template" {
  name_prefix   = "cr_launch_template"
  image_id      = "ami-0a02ee601d742e89f"
  instance_type = "t2.micro"
  user_data     = filebase64("${path.module}/userdata/userdata.sh")

  health_check_grace_period = 120
  key_name                  = aws_key_pair.auth.id
  vpc_security_group_ids    = [aws_security_group.ec2_sg.id]
}

resource "aws_autoscaling_group" "cr_autoscaling_group" {
  desired_capacity    = 1
  max_size            = 1
  min_size            = 1
  vpc_zone_identifier = [aws_subnet.cr_subnet.id]

  health_check_type   = "ELB"
  load_balancers      = [aws_elb.web.id]

  launch_template {
    id      = aws_launch_template.cr_launch_template.id
    version = "$Latest"
  }
}

# resource "aws_elb_attachment" "cr_elb_attachment" {
#   elb      = "${aws_elb.web.id}"
#   instance = "${aws_instance.foo.id}"
# }

# resource "aws_lb_target_group_attachment" "cr_attachment_tg" {
#   target_group_arn = "${aws_lb_target_group.cr_target_group.arn}"
#   target_id        = "${aws_autoscaling_group.cr_autoscaling_group.id}"
#   port             = 80
# }

# resource "aws_lb_target_group" "cr_target_group" {
#   name     = "cr_target_group"
#   port     = 80
#   protocol = "HTTP"
#   vpc_id   = "${aws_vpc.cr_vpc.id}"
# }