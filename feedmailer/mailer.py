import subprocess


class Mailer:
    def __init__(self, config):
        self.config = config

    def send(self, body):
        header = f"From: {self.config.sender}\nTo: {self.config.recipient}\n"
        msg = f"{header}Subject: Feed Updates\nContent-Type: text/markdown\n\n{body}"
        proc = subprocess.Popen(["sendmail", "-t"], stdin=subprocess.PIPE)
        proc.communicate(input=msg.encode('utf-8'))
