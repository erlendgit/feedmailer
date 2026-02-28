import subprocess

from feedmailer.utils.mail_backends.base import MailBackend


class SendmailBackend(MailBackend):
    """Mail backend using sendmail subprocess."""

    def send(self, sender, recipient, subject, html_body, text_body):
        """Send email using sendmail command."""
        boundary = "===============FeedMailer==============="

        header = f"From: {sender}\nTo: {recipient}\n"
        header += f"Subject: {subject}\n"
        header += "MIME-Version: 1.0\n"
        header += f'Content-Type: multipart/alternative; boundary="{boundary}"\n\n'

        # Plain text part
        msg = header
        msg += f"--{boundary}\n"
        msg += "Content-Type: text/plain; charset=utf-8\n\n"
        msg += text_body + "\n\n"

        # HTML part
        msg += f"--{boundary}\n"
        msg += "Content-Type: text/html; charset=utf-8\n\n"
        msg += html_body + "\n\n"

        msg += f"--{boundary}--\n"

        proc = subprocess.Popen(["sendmail", "-t"], stdin=subprocess.PIPE)
        proc.communicate(input=msg.encode("utf-8"))
