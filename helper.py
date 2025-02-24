import os
import shutil
import time
import boto3
from python_terraform import Terraform, IsFlagged

# Create and initialize Terraform working directory
if os.path.exists('terraform'):
    shutil.rmtree('terraform')
os.mkdir('terraform')
folder_dir = os.path.join(os.getcwd(), 'terraform')

tf = Terraform(working_dir=folder_dir)


def assume_role(role_arn):
    """Assumes an IAM role and retrieves temporary credentials."""
    try:
        sts_client = boto3.client('sts')
        response = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName="TerraformSession"
        )

        credentials = response['Credentials']
        return {
            "access_key": credentials['AccessKeyId'],
            "secret_key": credentials['SecretAccessKey'],
            "session_token": credentials['SessionToken']
        }
    except Exception as e:
        print(f"Error assuming role: {e}")
        return None


def providers(auth_method, access_key=None, secret_key=None, region=None, role_arn=None):
    """ Configures AWS Provider with either Access Key or Assume Role """
    if auth_method == "assume_role" and role_arn:
        creds = assume_role(role_arn)
        if not creds:
            print("Failed to assume role. Exiting...")
            return

        terraform_config = f"""
        provider "aws" {{
            region = "{region}"
            access_key = "{creds['access_key']}"
            secret_key = "{creds['secret_key']}"
            token      = "{creds['session_token']}"
        }}
        """
    else:
        terraform_config = f"""
        provider "aws" {{
            region = "{region}"
            access_key = "{access_key}"
            secret_key = "{secret_key}"
        }}
        """

    with open(f"{folder_dir}/providers.tf", "w") as f:
        f.write(terraform_config)

    tf.init()
    tf.fmt(diff=True)


def s3(bucket_name):
    """ Creates an S3 Bucket """
    terraform_config = f"""
    resource "aws_s3_bucket" "this" {{
        bucket = "{bucket_name}"
    }}
    """
    with open(f"{folder_dir}/S3.tf", "w") as f:
        f.write(terraform_config)

    tf.plan(no_color=IsFlagged, refresh=False, capture_output=True)
    tf.apply(capture_output=True, skip_plan=True)


def vpc(vpc_name, cidr_block):
    """ Creates a VPC """
    terraform_config = f"""
    resource "aws_vpc" "this" {{
        cidr_block = "{cidr_block}"
        tags = {{
            Name = "{vpc_name}"
        }}
    }}
    """
    with open(f"{folder_dir}/VPC.tf", "w") as f:
        f.write(terraform_config)

    tf.plan(no_color=IsFlagged, refresh=False, capture_output=True)
    tf.apply(capture_output=True, skip_plan=True)


def ec2(instance_name, ami, instance_type, key_name, subnet_id, public_key):
    """ Creates an EC2 Instance """
    terraform_config = f"""
    resource "aws_instance" "this" {{
        ami           = "{ami}"
        instance_type = "{instance_type}"
        key_name      = "{key_name}"
        subnet_id     = "{subnet_id}"
        depends_on    = [aws_key_pair.this]
        tags = {{
            Name = "{instance_name}"
        }}
    }}

    resource "aws_key_pair" "this" {{
        key_name   = "{key_name}"
        public_key = "{public_key}"
    }}
    """
    with open(f"{folder_dir}/EC2.tf", "w") as f:
        f.write(terraform_config)

    tf.plan(no_color=IsFlagged, refresh=False, capture_output=True)
    tf.apply(capture_output=True, skip_plan=True)


def rds(db_name, cluster_identifier, engine, instance_class, username, password):
    """ Creates an RDS Cluster """
    terraform_config = f"""
    resource "aws_rds_cluster" "this" {{
        cluster_identifier = "{cluster_identifier}"
        engine             = "{engine}"
        database_name      = "{db_name}"
        master_username    = "{username}"
        master_password    = "{password}"
    }}
    """
    with open(f"{folder_dir}/RDS.tf", "w") as f:
        f.write(terraform_config)

    tf.plan(no_color=IsFlagged, refresh=False, capture_output=True)
    tf.apply(capture_output=True, skip_plan=True)


def load_balancer(lb_name, subnets, type):
    """ Creates an Elastic Load Balancer """
    terraform_config = f"""
    resource "aws_lb" "this" {{
        name               = "{lb_name}"
        internal           = false
        load_balancer_type = "{type}"
        security_groups    = []
        subnets            = {subnets}
    }}
    """
    with open(f"{folder_dir}/ELB.tf", "w") as f:
        f.write(terraform_config)

    tf.plan(no_color=IsFlagged, refresh=False, capture_output=True)
    tf.apply(capture_output=True, skip_plan=True)


def auto_scaling(asg_name, min_size, max_size, instance_type, ami, vpc_zone):
    """ Creates an Auto Scaling Group """
    terraform_config = f"""
    resource "aws_autoscaling_group" "this" {{
        name                 = "{asg_name}"
        min_size             = {min_size}
        max_size             = {max_size}
        desired_capacity     = {min_size}
        vpc_zone_identifier  = ["{vpc_zone}"]
        launch_configuration = aws_launch_configuration.this.id
    }}

    resource "aws_launch_configuration" "this" {{
        name          = "{asg_name}-config"
        image_id      = "{ami}"
        instance_type = "{instance_type}"
    }}
    """
    with open(f"{folder_dir}/ASG.tf", "w") as f:
        f.write(terraform_config)

    tf.plan(no_color=IsFlagged, refresh=False, capture_output=True)
    tf.apply(capture_output=True, skip_plan=True)


def cloudfront(distribution_name, s3_origin):
    """ Creates a CloudFront Distribution """
    terraform_config = f"""
    resource "aws_cloudfront_distribution" "this" {{
        origin {{
            domain_name = "{s3_origin}"
            origin_id   = "{distribution_name}"
        }}
        enabled = true
    }}
    """
    with open(f"{folder_dir}/CloudFront.tf", "w") as f:
        f.write(terraform_config)

    tf.plan(no_color=IsFlagged, refresh=False, capture_output=True)
    tf.apply(capture_output=True, skip_plan=True)


def api_gateway(api_name):
    """ Creates an API Gateway """
    terraform_config = f"""
    resource "aws_api_gateway_rest_api" "this" {{
        name = "{api_name}"
    }}
    """
    with open(f"{folder_dir}/APIGateway.tf", "w") as f:
        f.write(terraform_config)

    tf.plan(no_color=IsFlagged, refresh=False, capture_output=True)
    tf.apply(capture_output=True, skip_plan=True)


def sns_topic(topic_name):
    """ Creates an SNS Topic """
    terraform_config = f"""
    resource "aws_sns_topic" "this" {{
        name = "{topic_name}"
    }}
    """
    with open(f"{folder_dir}/SNS.tf", "w") as f:
        f.write(terraform_config)

    tf.plan(no_color=IsFlagged, refresh=False, capture_output=True)
    tf.apply(capture_output=True, skip_plan=True)

def lambda_function(lambda_name, s3_bucket, handler, runtime, role):
    """ Creates a Lambda Function """
    terraform_config = f"""
    resource "aws_lambda_function" "this" {{
        function_name = "{lambda_name}"
        s3_bucket     = "{s3_bucket}"
        handler       = "{handler}"
        runtime       = "{runtime}"
        role          = "{role}"
    }}
    """
    with open(f"{folder_dir}/Lambda.tf", "w") as f:
        f.write(terraform_config)

    tf.plan(no_color=IsFlagged, refresh=False, capture_output=True)
    tf.apply(capture_output=True, skip_plan=True)
    