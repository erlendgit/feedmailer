from feedmailer.utils.mail_backends.sendmail import SendmailBackend
from feedmailer.utils.mail_backends.smtp import SMTPBackend


class Mailer:
    """Main mailer class that delegates to a backend."""

    def __init__(self, config):
        self.config = config
        self.backend = self._create_backend_from_config()

    def _create_backend_from_config(self):
        """Create backend based on config settings."""
        backend_type = getattr(self.config, "mail_backend", "sendmail")

        if backend_type == "smtp":
            return SMTPBackend(
                host=getattr(self.config, "smtp_host", "localhost"),
                port=getattr(self.config, "smtp_port", 587),
                username=getattr(self.config, "smtp_username", None),
                password=getattr(self.config, "smtp_password", None),
                use_tls=getattr(self.config, "smtp_use_tls", True),
            )
        else:
            return SendmailBackend()

    def send(self, html_body, text_body, subject="Feed Updates"):
        """Send email with both HTML and plain text versions.

        Args:
            html_body: HTML version of the email
            text_body: Plain text version of the email
            subject: Email subject line (default: "Feed Updates")
        """
        self.backend.send(
            sender=self.config.sender,
            recipient=self.config.recipient,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
        )
