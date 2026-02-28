import json


class Config:
    def __init__(self, path):
        with open(path, "r") as f:
            self.data = json.load(f)
        self.urls = self.data.get("urls", [])
        self.sender = self.data.get("from")
        self.recipient = self.data.get("to")

        # Mail backend configuration
        self.mail_backend = self.data.get(
            "mail_backend", "sendmail"
        )  # 'sendmail' or 'smtp'

        # SMTP settings (optional, only used if mail_backend == 'smtp')
        smtp_config = self.data.get("smtp", {})
        self.smtp_host = smtp_config.get("host", "localhost")
        self.smtp_port = smtp_config.get("port", 587)
        self.smtp_username = smtp_config.get("username")
        self.smtp_password = smtp_config.get("password")
        self.smtp_use_tls = smtp_config.get("use_tls", True)
