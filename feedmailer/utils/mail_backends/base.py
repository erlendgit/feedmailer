from abc import ABC, abstractmethod


class MailBackend(ABC):
    """Abstract base class for mail backends."""

    @abstractmethod
    def send(self, sender, recipient, subject, html_body, text_body):
        """Send email with both HTML and plain text versions.

        Args:
            sender: Email sender address
            recipient: Email recipient address
            subject: Email subject line
            html_body: HTML version of the email
            text_body: Plain text version of the email
        """
        pass
