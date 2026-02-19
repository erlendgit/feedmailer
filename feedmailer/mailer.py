import subprocess
import markdown
from html.parser import HTMLParser


class HTMLToText(HTMLParser):
    """Simple HTML to plain text converter."""
    def __init__(self):
        super().__init__()
        self.text = []

    def handle_data(self, data):
        self.text.append(data)

    def get_text(self):
        return ''.join(self.text)


class Mailer:
    def __init__(self, config):
        self.config = config

    def _markdown_to_html(self, markdown_text):
        """Convert markdown to HTML."""
        return markdown.markdown(markdown_text)

    def _html_to_text(self, html_text):
        """Convert HTML to plain text."""
        parser = HTMLToText()
        parser.feed(html_text)
        return parser.get_text()

    def send(self, body):
        # Generate HTML from markdown
        html_body = self._markdown_to_html(body)

        # Generate plain text from HTML (better than from markdown)
        # But also keep original markdown as fallback
        text_body = self._html_to_text(html_body)

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

        proc = subprocess.Popen(["sendmail", "-t"], stdin=subprocess.PIPE)
        proc.communicate(input=msg.encode('utf-8'))
