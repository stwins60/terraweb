import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
import loghelper

load_dotenv()

USERNAME = os.getenv('EMAIL')
SERVER = os.getenv('SERVER')
SERVER_PASS = os.getenv('SERVER_PASS')
PORT = os.getenv('PORT')

def sendMyEmail(subject, msg, name="Idris", email="idrisniyi94@gmail.com"):
    try:
        server = smtplib.SMTP_SSL(SERVER, PORT)
        server.ehlo()
        server.login(USERNAME, SERVER_PASS)
        print('Connected to server')
        sender_email = "ifagbemi@africantech.dev"
        receiver_email = 'idrisniyi94@gmail.com'
        html = """
        <html>
            <body>
                <p style="color: black;">Name: {}</p>
                <p style="color: black;">Email: {}</p>
                <h5 style="color: black;">Review Message: {}</h5>
            </body>
        </html>
        """.format(name, email, msg)
        part = MIMEText(html, 'html')
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = sender_email
        message['To'] = receiver_email
        message.attach(part)

        # message = 'From: {}\nTo: {}\nSubject: {}\n\n{}'.format(sender_email, receiver_email, subject, msg)
        # message = 'From: {}\nTo: {}\nSubject: {}\n\n{}'.format(sender_email, receiver_email, 'Test', 'This is a test email')
        server.sendmail(sender_email, receiver_email, message.as_string())
        print('Email sent successfully')
        loghelper.info_logger.info(f"Email sent successfully to {receiver_email}")
    except Exception as e:
        print(e)
        print('Failed to connect to server')
        loghelper.debug_logger.error(f"Failed to connect to server: {e}")