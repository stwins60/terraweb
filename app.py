from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, send_file, send_from_directory
from flask_cors import CORS
from wtforms import Form, SelectMultipleField
import datetime
import os
import helper, loghelper
import secrets
import shutil
import json
import yaml
import base64
import logging
from dotenv import load_dotenv
import mailer

app = Flask(__name__)

load_dotenv()



def generate_csrf_token():
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(16)
    return session["_csrf_token"]

app.secret_key = secrets.token_hex(16)
# app.wsgi_app = AuthenticationMiddleware(app.wsgi_app)
CORS(app, origins="*")
app.jinja_env.globals["csrf_token"] = generate_csrf_token


app.config['FLASK_APP'] = 'app.py'
app.config['FLASK_ENV'] = 'development'
headers = {
    'Content-Type': 'text/html',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept, Authorization',
    'Set-Cookie': 'HttpOnly;Secure;SameSite=Strict',
    'Cookies': f"[session={secrets.token_hex(16)}]"
}

#load static files
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

class MyForm(Form):
    dropdown_options = [
        'S3', 'EC2', 'RDS', 'Lambda', 'DynamoDB', 
        'API Gateway', 'VPC', 'Auto Scaling', 'Load Balancer', 'CloudFront', 'SNSTopic',
    ]
    selected_option = SelectMultipleField('Resources', choices=[(option, option) for option in dropdown_options])

@app.route('/', methods=['GET', 'POST'])
def index():
    form = MyForm()
    error = ""
    
    selected_options = request.form.getlist('resources') if request.method == 'POST' else []

    # CSRF protection
    if request.method == 'POST':
        csrf_token = session.pop("_csrf_token", None)
        if not csrf_token or csrf_token != request.form.get("_csrf_token"):
            abort(403)

        # Check authentication type
        auth_method = request.form.get("auth_method")
        aws_region = request.form.get("aws_region")

        if auth_method == "assume_role":
            role_arn = request.form.get("iam_role_arn")
            credentials = helper.assume_role(role_arn)
            if credentials is None:
                error = "Failed to assume role. Please check IAM permissions."
                loghelper.debug_logger.error(f"{datetime.datetime.now()} - Assume role failed")
                return render_template('demo.html', dropdown_options=form.dropdown_options, selected_options=selected_options, error=error, form=form)
        else:
            credentials = {
                "access_key": request.form.get("aws_access_key"),
                "secret_key": request.form.get("aws_secret_key"),
                "session_token": None
            }

        # Initialize Terraform Provider
        helper.providers(auth_method, credentials.get("access_key"), credentials.get("secret_key"), aws_region, request.form.get("iam_role_arn"))

        # Process selected AWS services
        for selected_option in selected_options:
            try:
                loghelper.info_logger.info(f"{datetime.datetime.now()} - {selected_option} is being created")
                app.logger.info(f"{datetime.datetime.now()} - {selected_option} is being created")

                # Map selected options to their corresponding helper functions
                service_mapping = {
                    "S3": lambda: helper.s3(request.form.get('s3_bucket_name')),
                    "EC2": lambda: helper.ec2(
                        request.form.get('instance_name'),
                        request.form.get('ami'),
                        request.form.get('instance_type'),
                        request.form.get('key_name'),
                        request.form.get('subnet_id'),
                        request.form.get('key_pair_public_key')
                    ),
                    "RDS": lambda: helper.rds(
                        request.form.get('database_name'),
                        request.form.get('engine'),
                        request.form.get('master_username'),
                        request.form.get('master_password')
                    ),
                    "IAM Role": lambda: helper.iam_role(request.form.get('role_name'), request.form.get('policy_arn')),
                    "Lambda": lambda: helper.lambda_function(
                        request.form.get('lambda_name'),
                        request.form.get('s3_bucket'),
                        request.form.get('handler'),
                        request.form.get('runtime'),
                        request.form.get('role')
                    ),
                    "DynamoDB": lambda: helper.dynamodb(request.form.get('table_name'), request.form.get('hash_key')),
                    "API Gateway": lambda: helper.api_gateway(request.form.get('api_name')),
                    "VPC": lambda: helper.vpc(request.form.get('vpc_name'), request.form.get('cidr_block')),
                    "Auto Scaling": lambda: helper.auto_scaling(
                        request.form.get('asg_name'),
                        request.form.get('min_size'),
                        request.form.get('max_size'),
                        request.form.get('ami'),
                        request.form.get('vpc_zone')
                    ),
                    "Load Balancer": lambda: helper.load_balancer(request.form.get('lb_name'), request.form.get('subnets'), request.form.get('type')),
                    "CloudFront": lambda: helper.cloudfront(request.form.get('distribution_name'), request.form.get('s3_origin')),
                    "SNSTopic": lambda: helper.sns_topic(request.form.get('sns_topic_name'))
                }

                # Call the corresponding function
                if selected_option in service_mapping:
                    service_mapping[selected_option]()
                
                loghelper.info_logger.info(f"{datetime.datetime.now()} - {selected_option} created successfully")
                app.logger.info(f"{datetime.datetime.now()} - {selected_option} created successfully")

            except Exception as e:
                error = str(e)
                loghelper.debug_logger.error(f"{datetime.datetime.now()} - {selected_option} creation failed: {error}")
                app.logger.error(f"{datetime.datetime.now()} - {selected_option} creation failed: {error}")

    return render_template('demo.html', dropdown_options=form.dropdown_options, selected_options=selected_options, error=error, form=form)

@app.route('/survey', methods=['GET', 'POST'])
# @login_required
def survey():
    form = MyForm()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        mailer.sendMyEmail("Survey", message, name, email)
        loghelper.info_logger.info(f"{datetime.datetime.now()} - User {email} submitted survey")
        app.logger.info(f"{datetime.datetime.now()} - User {email} submitted survey")
        flash("Thank you for your feedback!", "success")
        return redirect(url_for('index'))
    else:
        loghelper.debug_logger.error(f"{datetime.datetime.now()} - Survey submission failed")
        app.logger.error(f"{datetime.datetime.now()} - Survey submission failed")
    return render_template('survey.html', form=form)

@app.route('/terraform/download', methods=['GET', 'POST'])
def download():
    error = ""
    for i in os.listdir():
        if i.endswith(".tfstate"):
            loghelper.info_logger.info(f"{datetime.datetime.now()} - tfstate file found and downloaded")
            app.logger.info(f"{datetime.datetime.now()} - tfstate file found and downloaded")
            return send_file(i, as_attachment=True)

        else:
            error = "No tfstate file found"
            loghelper.debug_logger.error(f"{datetime.datetime.now()} - tfstate file not found")
            app.logger.error(f"{datetime.datetime.now()} - tfstate file not found")
            return render_template('app.html', error=error)
    
    for i in os.listdir():
        if i.endswith(".tfstate"):
            os.remove(i)
        if i == ".terraform":
            shutil.rmtree(i)
        if i.startswith(".terraform."):
            os.remove(i)
        # if i.startswith("main.tf"):
        #     os.remove(i)

    if os.path.exists("terraform.tf"):
        os.remove("terraform.tf")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005)
else:
    gunicon_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicon_logger.handlers
    app.logger.setLevel(gunicon_logger.level)
    