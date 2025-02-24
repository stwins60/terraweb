# 🌍 Terraform Web UI for AWS Deployment

This is a **Flask-based web application** that allows users to **provision AWS infrastructure using Terraform**. It supports **multiple AWS services**, offers **authentication via Access Keys or Assume Role**, and dynamically generates Terraform configurations.

---

## 🚀 **Features**
✔ **Multi-Service AWS Deployment** (S3, EC2, RDS, Lambda, VPC, etc.)  
✔ **Supports Assume Role & Access Key Authentication**  
✔ **Dynamically Toggles AWS Service Fields**  
✔ **Integrated with Terraform for AWS Resource Provisioning**  
✔ **Automatic IAM Role Credential Retrieval**  
✔ **Secure CSRF Protection**  

---

## 📜 **Installation Guide**
### 1️⃣ **Clone the Repository**
```bash
git clone https://github.com/stwins60/terraweb.git
cd terraweb
```
### 2️⃣ **Set Up Virtual Environment**
#### For Windows
```bash
python3 -m venv venv
venv\Scripts\activate
```
#### For Linux/Mac
```bash
python3 -m venv venv
source venv/bin/activate
```
### 3️⃣ **Install Dependencies**
```bash
pip install -r requirements.txt
```
### 4️⃣ **Set Environment Variables**
#### EMAIL Configuration
```bash
PORT=<smtp_port>
EMAIL=<smtp_email>
SERVER_PASS=<smtp_password>
SERVER=<smtp_server>
```
#### PostgreSQL Configuration
```bash
DATABASE_URL=<database_url>
```
### 5️⃣ **Run the Application**
```bash
python app.py
```
### 6️⃣ **Access the Web UI**
Open your browser and navigate to `http://localhost:5005`
