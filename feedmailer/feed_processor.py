import feedparser


class FeedProcessor:
    def __init__(self, config, seen_links):
        self.config = config
        self.seen_links = seen_links
        self.found = []

    def collect(self):
        for url in self.config.urls:
            feed = feedparser.parse(url)
            new = [e for e in feed.entries if e.link not in self.seen_links]
            self.found.extend(new)
        return self.found

    def as_markdown(self):
        return "\n".join([f"* [{e.title}]({e.link})" for e in self.found])
