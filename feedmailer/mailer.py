import subprocess


class Mailer:
    def __init__(self, config):
        self.config = config

    def send(self, html_body, text_body):
        """Send email with both HTML and plain text versions.

        Args:
            html_body: HTML version of the email
            text_body: Plain text version of the email
        """
        # Create multipart email with boundary
        boundary = "===============FeedMailer==============="

        header = f"From: {self.config.sender}\nTo: {self.config.recipient}\n"
        header += "Subject: Feed Updates\n"
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
        print(msg)

        proc = subprocess.Popen(["sendmail", "-t"], stdin=subprocess.PIPE)
        proc.communicate(input=msg.encode('utf-8'))
