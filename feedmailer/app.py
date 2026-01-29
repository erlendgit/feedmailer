import argparse

from feedmailer.config import Config
from feedmailer.storage import Storage
from feedmailer.feed_processor import FeedProcessor
from feedmailer.mailer import Mailer


class App:
    def __init__(self):
        args = self._parse_args()
        self.config = Config(args.config)
        self.storage = Storage(args.status)
        self.seen = self.storage.load()

    def _parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("config")
        parser.add_argument("status")
        return parser.parse_args()

    def run(self):
        processor = FeedProcessor(self.config, self.seen)
        if processor.collect():
            Mailer(self.config).send(processor.as_markdown())
            self._update_state(processor)

    def _update_state(self, processor):
        new_links = {e.link for e in processor.found}
        self.storage.save(self.seen | new_links)
