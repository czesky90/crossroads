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

  # HTTPS access from anywhere
  ingress {
    from_port   = 443
    to_port     = 443
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

  # HTTP access from anywhere
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTP access from anywhere
  ingress {
    from_port   = 443
    to_port     = 443
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

resource "aws_route53_zone" "primary" {
  name = var.domain_name
}

resource "aws_route53_record" "www" {
  zone_id = aws_route53_zone.primary.zone_id
  name    = "www.${var.domain_name}"
  type    = "A"

  alias {
    name                   = aws_elb.web.dns_name
    zone_id                = aws_elb.web.zone_id
    evaluate_target_health = false
  }
}

resource "aws_elb" "web" {
  name = "terraform-cr-elb"

  subnets         = [aws_subnet.cr_subnet.id, aws_subnet.elb_subnet.id]
  security_groups = [aws_security_group.elb.id]

  access_logs {
    bucket        = aws_s3_bucket.elb_logs_bucket.bucket
    bucket_prefix = "elb_logs"
    interval      = 60
  }

  listener {
    lb_port           = 443
    lb_protocol       = "https"
    instance_port     = 443
    instance_protocol = "https"
    ssl_certificate_id = aws_iam_server_certificate.self_signed_cert.arn
  }

  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    target              = "HTTPS:443/"
    interval            = 15
  }
}

resource "aws_iam_server_certificate" "self_signed_cert" {
  name             = "self_signed"
  certificate_body = file(var.cert_path)
  private_key      = file(var.key_cert_path)
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

  iam_instance_profile {
    arn  = aws_iam_instance_profile.cr_ec2_instance_profile.arn
  }

  key_name                  = aws_key_pair.auth.id
  vpc_security_group_ids    = [aws_security_group.ec2_sg.id]
}

resource "aws_iam_instance_profile" "cr_ec2_instance_profile" {
  name = "cr_ec2_instance_profile"
  role = aws_iam_role.cr_ec2_iam_role.name
}

resource "aws_autoscaling_group" "cr_autoscaling_group" {
  desired_capacity    = 1
  max_size            = 2
  min_size            = 1
  vpc_zone_identifier = [aws_subnet.cr_subnet.id]

  health_check_grace_period = 300
  health_check_type   = "ELB"
  load_balancers      = [aws_elb.web.id]

  launch_template {
    id      = aws_launch_template.cr_launch_template.id
    version = "$Latest"
  }
}

resource "aws_iam_role" "cr_ec2_iam_role" {
  name = "cr_ec2_iam_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement":[
    {
        "Action": "sts:AssumeRole",
        "Effect": "Allow",
        "Principal": {
            "Service": "ec2.amazonaws.com"
        }
    }
  ]
}
EOF

  tags = {
    env = "prod"
  }
}

resource "aws_iam_policy" "cr_ec2_iam_policy" {
  name        = "cr_ec2_iam_policy"
  path        = "/"
  description = "Access from EC2 to S3 bucket with API keys"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action":  [
        "s3:Get*",
        "s3:List*"
      ],
      "Resource": ["arn:aws:s3:::crossroad-api-keys",
                   "arn:aws:s3:::crossroad-api-keys/*"]
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "cr_role_attach" {
  role       = aws_iam_role.cr_ec2_iam_role.name
  policy_arn = aws_iam_policy.cr_ec2_iam_policy.arn
}

resource "aws_iam_role_policy_attachment" "cr_ecr_role_attach" {
  role       = aws_iam_role.cr_ec2_iam_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_s3_bucket" "elb_logs_bucket" {
  bucket = "cr-elb-logs-bucket"
  acl    = "private"
  force_destroy = true
  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::054676820928:root"
      },
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::cr-elb-logs-bucket/elb_logs/AWSLogs/189268696310/*"
    },
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "delivery.logs.amazonaws.com"
      },
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::cr-elb-logs-bucket/elb_logs/AWSLogs/189268696310/*",
      "Condition": {
        "StringEquals": {
          "s3:x-amz-acl": "bucket-owner-full-control"
        }
      }
    },
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "delivery.logs.amazonaws.com"
      },
      "Action": "s3:GetBucketAcl",
      "Resource": "arn:aws:s3:::cr-elb-logs-bucket"
    }
  ]
}
POLICY
  tags = {
    Name = "CR_BUCKET"
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
