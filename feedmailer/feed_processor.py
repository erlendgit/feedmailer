import asyncio
import os

import aiohttp
import feedparser
from jinja2 import Environment, FileSystemLoader, select_autoescape


class FeedProcessor:
    def __init__(self, config, seen_links):
        self.config = config
        self.seen_links = seen_links
        self.found = []
        self.context = {"feeds": [], "zero_links": []}

        # Setup Jinja2 environment
        template_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )

    async def _fetch_feed(self, session, url):
        """Fetch and parse a single feed asynchronously."""
        try:
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                content = await resp.text()
                # feedparser.parse can handle string content
                response = feedparser.parse(content)

                all_links = [e.link for e in response.entries]
                if len(all_links) == 0:
                    msg = "No links found in feed"
                    raise AssertionError(msg)

                new = [e for e in response.entries if e.link not in self.seen_links]
                if not new:
                    return None

                return {"url": url, "feed_title": response.feed.title, "entries": new}
        except Exception as e:
            return {"url": url, "error": str(e)}

    async def collect_async(self):
        """Collect feeds asynchronously in parallel."""
        async with aiohttp.ClientSession() as session:
            tasks = [self._fetch_feed(session, url) for url in self.config.urls]
            results = await asyncio.gather(*tasks)

        for result in results:
            if result is None:
                # No new entries, skip
                continue
            elif "error" in result:
                # Error occurred
                self.context["zero_links"].append(f"{result['url']}: {result['error']}")
            else:
                # Success
                self.found.extend(result["entries"])
                self.context["feeds"].append(
                    {"name": result["feed_title"], "entries": result["entries"]}
                )

        return self.found or self.context["zero_links"]

    def collect(self):
        """Synchronous wrapper for collect_async to maintain backward compatibility."""
        return asyncio.run(self.collect_async())

    def as_html(self):
        template = self.jinja_env.get_template("email/overview.html")
        return template.render(**self.context)

    def as_text(self):
        template = self.jinja_env.get_template("email/overview.txt")
        return template.render(**self.context)
