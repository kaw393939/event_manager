from builtins import Exception, int, str
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from settings.config import settings
import logging

class SMTPClient:
    def __init__(self, server: str, port: int, username: str, password: str):
        self.server = server
        self.port = port
        self.username = username
        self.password = password

    def send_email(self, subject: str, html_content: str, recipient: str):
        try:
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.username
            message['To'] = recipient
            message.attach(MIMEText(html_content, 'html'))
            
            # Create SMTP connection with a timeout (e.g., 10 seconds)
            with smtplib.SMTP(self.server, self.port, timeout=10) as server:
                logging.info("Connected to SMTP server")
                
                # Start TLS to secure the connection
                logging.info("Starting TLS...")
                server.starttls()
                logging.info("TLS established")
                
                # Log in using SMTP credentials
                logging.info("Logging into SMTP server...")
                server.login(self.username, self.password)
                logging.info("Logged in successfully")
                
                # Send the email
                logging.info("Sending email...")
                server.sendmail(self.username, recipient, message.as_string())
                logging.info(f"Email sent to {recipient}")
        except Exception as e:
            logging.error(f"Failed to send email: {str(e)}")
            raise
