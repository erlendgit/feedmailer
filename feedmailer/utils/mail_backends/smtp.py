import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from feedmailer.utils.mail_backends.base import MailBackend


class SMTPBackend(MailBackend):
    """Mail backend using SMTP."""

    def __init__(
        self, host="localhost", port=587, username=None, password=None, use_tls=True
    ):
        """Initialize SMTP backend.

        Args:
            host: SMTP server hostname
            port: SMTP server port
            username: Optional username for authentication
            password: Optional password for authentication
            use_tls: Whether to use TLS/STARTTLS
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls

    def send(self, sender, recipient, subject, html_body, text_body):
        """Send email using SMTP."""
        # Create message
        msg = MIMEMultipart("alternative")
        msg["From"] = sender
        msg["To"] = recipient
        msg["Subject"] = subject

        # Attach text and HTML parts
        part_text = MIMEText(text_body, "plain", "utf-8")
        part_html = MIMEText(html_body, "html", "utf-8")
        msg.attach(part_text)
        msg.attach(part_html)

        # Send via SMTP
        with smtplib.SMTP(self.host, self.port) as server:
            if self.use_tls:
                server.starttls()
            if self.username and self.password:
                server.login(self.username, self.password)
            server.send_message(msg)
