import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_verification_email(email: str, token: str):
    sender_email = "admin@healme.tech"
    receiver_email = email
    smtp_server = "us2.smtp.mailhostbox.com"
    smtp_port = 587
    smtp_password = "KuStYCx7"
    smtp_username = "admin@healme.tech"
    
    message = MIMEMultipart("alternative")
    message["Subject"] = "Email Verification"
    message["From"] = sender_email
    message["To"] = receiver_email

    verification_link = f"http://healme.tech/auth/verify/{token}"
    text = f"Hi,\nPlease verify your email by clicking on the following link: {verification_link}"
    part = MIMEText(text, "plain")

    message.attach(part)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()  # Identify ourselves to the server
            server.starttls()  # Secure the connection
            server.ehlo()  # Re-identify ourselves as an encrypted connection
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully")
    except smtplib.SMTPException as e:
        print(f"Error: {e}")
