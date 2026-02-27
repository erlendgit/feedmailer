import feedparser
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os


class FeedProcessor:
    def __init__(self, config, seen_links):
        self.config = config
        self.seen_links = seen_links
        self.found = []
        self.context = {
            "feeds": [],
            "zero_links": []
        }

        # Setup Jinja2 environment
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def collect(self):
        for url in self.config.urls:
            try:
                response = feedparser.parse(url)
                all = [e.link for e in response.entries]
                if len(all) == 0:
                    msg = "No links found in feed"
                    raise AssertionError(msg)
                new = [e for e in response.entries if e.link not in self.seen_links]
                if not new:
                    continue
                self.found.extend(new)
                self.context['feeds'].append({
                    "name": response.feed.title,
                    "entries": new
                })
            except Exception as e:
                self.context['zero_links'].append(f"{url}: {e}")
                pass
        return self.found or self.context['zero_links']

    def as_html(self):
        template = self.jinja_env.get_template('email/overview.html')
        return template.render(**self.context)

    def as_text(self):
        template = self.jinja_env.get_template('email/overview.txt')
        return template.render(**self.context)
