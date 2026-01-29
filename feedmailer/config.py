import json


class Config:
    def __init__(self, path):
        with open(path, 'r') as f:
            self.data = json.load(f)
        self.urls = self.data.get('urls', [])
        self.sender = self.data.get('from')
        self.recipient = self.data.get('to')
