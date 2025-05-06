import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from logger import get_logger
logger = get_logger(__name__)

class EmailService:
    def __init__(self, smtp_server="localhost", smtp_port=1025, from_addr="paras.majethiya@tiezinteractive.com", to_addr="paras.majethiya@tiezinteractive.com"):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.from_addr = from_addr
        self.to_addr = to_addr

    def send_email(self, to_addr, subject, body):
        """Send an email to the specified recipients and return status"""
        msg = MIMEMultipart()
        msg['From'] = self.from_addr
        msg['To'] = ", ".join(to_addr)
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.sendmail(self.from_addr, to_addr, msg.as_string())
            logger.info("Email sent successfully!")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
