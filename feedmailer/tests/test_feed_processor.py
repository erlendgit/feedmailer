from functools import wraps
from unittest import TestCase, mock
from unittest.mock import AsyncMock, MagicMock, patch

from feedmailer.feed_processor import FeedProcessor


def mock_aiohttp_session(func):
    """Decorator to automatically mock aiohttp session for tests."""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # Create mock session that can be used in async context
        mock_session = MagicMock()

        # Create a function that returns a new mock response each time
        # Store the URL for use by feedparser.parse mock
        urls_requested = []

        def create_mock_resp(url, *req_args, **req_kwargs):
            urls_requested.append(url)
            mock_resp = AsyncMock()
            # Return the URL as feed content so feedparser mock can identify which feed
            mock_resp.text = AsyncMock(return_value=f"<feed>{url}</feed>")
            mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
            mock_resp.__aexit__ = AsyncMock(return_value=None)
            return mock_resp

        mock_session.get = MagicMock(side_effect=create_mock_resp)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session._urls_requested = urls_requested  # For debugging

        with patch("aiohttp.ClientSession", return_value=mock_session):
            return func(self, *args, **kwargs)

    return wrapper


class TestFeedProcessorTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.mock_config = mock.Mock()
        self.mock_config.urls = ["https://example.com/feed"]

    @mock_aiohttp_session
    def test_feed_processor_collect_new_entries(self):
        seen_links = set()
        processor = FeedProcessor(self.mock_config, seen_links)

        mock_entry1 = mock.Mock(link="https://example.com/entry1", title="Entry 1")
        mock_entry2 = mock.Mock(link="https://example.com/entry2", title="Entry 2")
        mock_feed = mock.Mock(entries=[mock_entry1, mock_entry2])
        mock_feed.name = "Test Feed"

        with mock.patch("feedparser.parse", return_value=mock_feed):
            result = processor.collect()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], mock_entry1)
        self.assertEqual(result[1], mock_entry2)

    @mock_aiohttp_session
    def test_feed_processor_filters_seen_entries(self):
        seen_links = {"https://example.com/entry1"}
        processor = FeedProcessor(self.mock_config, seen_links)

        mock_entry1 = mock.Mock(link="https://example.com/entry1", title="Entry 1")
        mock_entry2 = mock.Mock(link="https://example.com/entry2", title="Entry 2")
        mock_feed = mock.Mock(entries=[mock_entry1, mock_entry2])
        mock_feed.name = "Test Feed"

        with mock.patch("feedparser.parse", return_value=mock_feed):
            result = processor.collect()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], mock_entry2)

    @mock_aiohttp_session
    def test_feed_processor_multiple_feeds(self):
        self.mock_config.urls = [
            "https://example.com/feed1",
            "https://example.com/feed2",
        ]
        processor = FeedProcessor(self.mock_config, set())

        mock_entry1 = mock.Mock(link="https://example.com/entry1", title="Entry 1")
        mock_entry2 = mock.Mock(link="https://example.com/entry2", title="Entry 2")

        def mock_parse(content):
            # Content now contains "<feed>URL</feed>" from aiohttp mock
            if "feed1" in content:
                return mock.Mock(entries=[mock_entry1], feed=mock.Mock(title="Feed 1"))
            elif "feed2" in content:
                return mock.Mock(entries=[mock_entry2], feed=mock.Mock(title="Feed 2"))
            else:
                return mock.Mock(entries=[], feed=mock.Mock(title="Unknown"))

        with mock.patch("feedparser.parse", side_effect=mock_parse):
            result = processor.collect()

        self.assertEqual(len(result), 2)
        # Verify context was populated with both feeds
        self.assertEqual(len(processor.context["feeds"]), 2)
        # Order is not guaranteed with async, so check both feeds are present
        feed_names = {feed["name"] for feed in processor.context["feeds"]}
        self.assertEqual(feed_names, {"Feed 1", "Feed 2"})
        self.assertIn("Feed 1", feed_names)
        self.assertIn("Feed 2", feed_names)

    def test_feed_processor_as_html(self):
        processor = FeedProcessor(mock.Mock(), set())
        mock_entry1 = mock.Mock(title="Entry 1", link="https://example.com/1")
        mock_entry2 = mock.Mock(title="Entry 2", link="https://example.com/2")

        # Set context with feeds structure that the template expects
        processor.context["feeds"] = [
            {"name": "Test Feed", "entries": [mock_entry1, mock_entry2]}
        ]

        html = processor.as_html()

        # Verify HTML structure matches actual template output
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("<html>", html)
        self.assertIn("<h1>Feed Updates</h1>", html)
        self.assertIn("<h3>Test Feed</h3>", html)
        self.assertIn('<a href="https://example.com/1">Entry 1</a>', html)
        self.assertIn('<a href="https://example.com/2">Entry 2</a>', html)
        self.assertIn("<ul>", html)
        self.assertIn("<li>", html)

    def test_feed_processor_as_text(self):
        processor = FeedProcessor(mock.Mock(), set())
        mock_entry1 = mock.Mock(title="Entry 1", link="https://example.com/1")
        mock_entry2 = mock.Mock(title="Entry 2", link="https://example.com/2")

        # Set context with feeds structure that the template expects
        processor.context["feeds"] = [
            {"name": "Test Feed", "entries": [mock_entry1, mock_entry2]}
        ]

        text = processor.as_text()

        # Verify text structure matches actual template output
        self.assertIn("Feed Updates", text)
        self.assertIn("============", text)
        self.assertIn("Test Feed", text)
        self.assertIn("---------", text)  # Underline for "Test Feed" (9 chars)
        self.assertIn("* Entry 1", text)
        self.assertIn("https://example.com/1", text)
        self.assertIn("* Entry 2", text)
        self.assertIn("https://example.com/2", text)

    def test_feed_processor_as_html_multiple_feeds(self):
        processor = FeedProcessor(mock.Mock(), set())
        mock_entry1 = mock.Mock(title="Entry 1", link="https://example.com/1")
        mock_entry2 = mock.Mock(title="Entry 2", link="https://example.com/2")
        mock_entry3 = mock.Mock(title="Entry 3", link="https://example.com/3")

        # Set context with multiple feeds
        processor.context["feeds"] = [
            {"name": "Feed One", "entries": [mock_entry1, mock_entry2]},
            {"name": "Feed Two", "entries": [mock_entry3]},
        ]

        html = processor.as_html()

        # Verify both feeds appear with their entries
        self.assertIn("<h3>Feed One</h3>", html)
        self.assertIn("<h3>Feed Two</h3>", html)
        self.assertIn('<a href="https://example.com/1">Entry 1</a>', html)
        self.assertIn('<a href="https://example.com/2">Entry 2</a>', html)
        self.assertIn('<a href="https://example.com/3">Entry 3</a>', html)

    def test_feed_processor_as_text_multiple_feeds(self):
        processor = FeedProcessor(mock.Mock(), set())
        mock_entry1 = mock.Mock(title="Entry 1", link="https://example.com/1")
        mock_entry2 = mock.Mock(title="Entry 2", link="https://example.com/2")

        # Set context with multiple feeds
        processor.context["feeds"] = [
            {"name": "Feed One", "entries": [mock_entry1]},
            {"name": "Feed Two", "entries": [mock_entry2]},
        ]

        text = processor.as_text()

        # Verify both feeds appear with their entries and underlines
        self.assertIn("Feed One", text)
        self.assertIn("--------", text)  # Underline for "Feed One" (8 chars)
        self.assertIn("Feed Two", text)
        self.assertIn("--------", text)  # Underline for "Feed Two" (8 chars)
        self.assertIn("* Entry 1", text)
        self.assertIn("* Entry 2", text)

    def test_feed_processor_as_html_empty_feeds(self):
        processor = FeedProcessor(mock.Mock(), set())
        processor.context["feeds"] = []

        html = processor.as_html()

        # Verify base structure exists even with no feeds
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("<h1>Feed Updates</h1>", html)

    def test_feed_processor_as_text_empty_feeds(self):
        processor = FeedProcessor(mock.Mock(), set())
        processor.context["feeds"] = []

        text = processor.as_text()

        # Verify header exists even with no feeds
        self.assertIn("Feed Updates", text)
        self.assertIn("============", text)

    @mock_aiohttp_session
    def test_feed_processor_zero_links_empty_feed(self):
        """Test that a feed with no entries raises AssertionError and is captured in zero_links"""
        processor = FeedProcessor(self.mock_config, set())

        # Mock a feed with no entries
        mock_feed = mock.Mock(entries=[])
        mock_feed.feed = mock.Mock(title="Empty Feed")

        with mock.patch("feedparser.parse", return_value=mock_feed):
            result = processor.collect()

        # Should return zero_links list since no entries found
        self.assertEqual(len(processor.found), 0)
        self.assertEqual(len(processor.context["zero_links"]), 1)
        self.assertIn("https://example.com/feed", processor.context["zero_links"][0])
        self.assertIn("No links found in feed", processor.context["zero_links"][0])
        # Result should be the zero_links list
        self.assertEqual(result, processor.context["zero_links"])

    @mock_aiohttp_session
    def test_feed_processor_zero_links_exception(self):
        """Test that exceptions during feed parsing are captured in zero_links"""
        processor = FeedProcessor(self.mock_config, set())

        # Mock feedparser.parse to raise an exception
        with mock.patch(
            "feedparser.parse", side_effect=Exception("Connection timeout")
        ):
            result = processor.collect()

        # Should capture the exception in zero_links
        self.assertEqual(len(processor.found), 0)
        self.assertEqual(len(processor.context["zero_links"]), 1)
        self.assertIn("https://example.com/feed", processor.context["zero_links"][0])
        self.assertIn("Connection timeout", processor.context["zero_links"][0])
        # Result should be the zero_links list
        self.assertEqual(result, processor.context["zero_links"])

    @mock_aiohttp_session
    def test_feed_processor_mixed_success_and_failures(self):
        """Test that successful feeds and failed feeds are both captured correctly"""
        self.mock_config.urls = [
            "https://example.com/feed1",
            "https://example.com/feed2",
            "https://example.com/feed3",
        ]
        processor = FeedProcessor(self.mock_config, set())

        mock_entry1 = mock.Mock(link="https://example.com/entry1", title="Entry 1")
        _mock_entry3 = mock.Mock(link="https://example.com/entry3", title="Entry 3")

        def mock_parse(content):
            # Content now contains "<feed>URL</feed>" from aiohttp mock
            if "feed1" in content:
                # Successful feed
                feed = mock.Mock(entries=[mock_entry1])
                feed.feed = mock.Mock(title="Good Feed")
                return feed
            elif "feed2" in content:
                # Empty feed
                feed = mock.Mock(entries=[])
                feed.feed = mock.Mock(title="Empty Feed")
                return feed
            else:
                msg = "Network error"
                raise Exception(msg)

        with mock.patch("feedparser.parse", side_effect=mock_parse):
            result = processor.collect()

        # Should have 1 found entry
        self.assertEqual(len(processor.found), 1)
        self.assertEqual(processor.found[0], mock_entry1)

        # Should have 2 zero_links entries (empty feed + exception)
        self.assertEqual(len(processor.context["zero_links"]), 2)
        # Don't check order since async may complete in any order
        zero_links_str = " ".join(processor.context["zero_links"])
        self.assertIn("feed2", zero_links_str)
        self.assertIn("No links found in feed", zero_links_str)
        self.assertIn("feed3", zero_links_str)
        self.assertIn("Network error", zero_links_str)

        # Should have 1 feed in context
        self.assertEqual(len(processor.context["feeds"]), 1)
        self.assertEqual(processor.context["feeds"][0]["name"], "Good Feed")

        # Result should be found entries (not zero_links) since we have entries
        self.assertEqual(result, processor.found)

    @mock_aiohttp_session
    def test_feed_processor_all_feeds_fail(self):
        """Test behavior when all feeds fail"""
        self.mock_config.urls = [
            "https://example.com/feed1",
            "https://example.com/feed2",
        ]
        processor = FeedProcessor(self.mock_config, set())

        def mock_parse(url):
            if url == "https://example.com/feed1":
                # Empty feed
                feed = mock.Mock(entries=[])
                feed.feed = mock.Mock(title="Empty Feed")
                return feed
            else:
                msg = "Parse error"
                raise Exception(msg)

        with mock.patch("feedparser.parse", side_effect=mock_parse):
            result = processor.collect()

        # Should have no found entries
        self.assertEqual(len(processor.found), 0)

        # Should have 2 zero_links entries
        self.assertEqual(len(processor.context["zero_links"]), 2)

        # Result should be zero_links list since no entries found
        self.assertEqual(result, processor.context["zero_links"])
        self.assertIsInstance(result, list)

    @mock_aiohttp_session
    def test_feed_processor_zero_links_all_entries_seen(self):
        """Test that feeds with all seen entries are skipped without adding to zero_links"""
        seen_links = {"https://example.com/entry1", "https://example.com/entry2"}
        processor = FeedProcessor(self.mock_config, seen_links)

        mock_entry1 = mock.Mock(link="https://example.com/entry1", title="Entry 1")
        mock_entry2 = mock.Mock(link="https://example.com/entry2", title="Entry 2")
        mock_feed = mock.Mock(entries=[mock_entry1, mock_entry2])
        mock_feed.feed = mock.Mock(title="Seen Feed")

        with mock.patch("feedparser.parse", return_value=mock_feed):
            result = processor.collect()

        # Should have no found entries (all were seen)
        self.assertEqual(len(processor.found), 0)

        # Should have no zero_links (feed had entries, they were just seen)
        self.assertEqual(len(processor.context["zero_links"]), 0)

        # Should have no feeds in context (no new entries)
        self.assertEqual(len(processor.context["feeds"]), 0)

        # Result should be empty list (no found, no zero_links)
        self.assertEqual(result, [])

    def test_feed_processor_as_html_with_zero_links(self):
        """Test that zero_links appear in HTML template"""
        processor = FeedProcessor(mock.Mock(), set())

        mock_entry = mock.Mock(title="Entry 1", link="https://example.com/1")
        processor.context["feeds"] = [{"name": "Good Feed", "entries": [mock_entry]}]
        processor.context["zero_links"] = [
            "https://bad.com/feed1: Connection timeout",
            "https://bad.com/feed2: No links found in feed",
        ]

        html = processor.as_html()

        # Verify both feeds and zero_links appear
        self.assertIn("<h3>Good Feed</h3>", html)
        self.assertIn('<a href="https://example.com/1">Entry 1</a>', html)
        self.assertIn("<h4>Zero links</h4>", html)
        self.assertIn("https://bad.com/feed1: Connection timeout", html)
        self.assertIn("https://bad.com/feed2: No links found in feed", html)

    def test_feed_processor_as_text_with_zero_links(self):
        """Test that zero_links appear in text template"""
        processor = FeedProcessor(mock.Mock(), set())

        mock_entry = mock.Mock(title="Entry 1", link="https://example.com/1")
        processor.context["feeds"] = [{"name": "Good Feed", "entries": [mock_entry]}]
        processor.context["zero_links"] = ["https://bad.com/feed: Connection error"]

        text = processor.as_text()

        # Verify both feeds and zero_links appear
        self.assertIn("Good Feed", text)
        self.assertIn("* Entry 1", text)
        self.assertIn("### Zero links", text)
        self.assertIn("https://bad.com/feed: Connection error", text)

    def test_feed_processor_as_html_only_zero_links(self):
        """Test HTML template with only zero_links (no successful feeds)"""
        processor = FeedProcessor(mock.Mock(), set())

        processor.context["feeds"] = []
        processor.context["zero_links"] = [
            "https://feed1.com: Parse error",
            "https://feed2.com: No links found in feed",
        ]

        html = processor.as_html()

        # Verify structure with only zero_links
        self.assertIn("<h1>Feed Updates</h1>", html)
        self.assertIn("<h4>Zero links</h4>", html)
        self.assertIn("https://feed1.com: Parse error", html)
        self.assertIn("https://feed2.com: No links found in feed", html)

    def test_feed_processor_as_text_only_zero_links(self):
        """Test text template with only zero_links (no successful feeds)"""
        processor = FeedProcessor(mock.Mock(), set())

        processor.context["feeds"] = []
        processor.context["zero_links"] = ["https://feed1.com: Network error"]

        text = processor.as_text()

        # Verify structure with only zero_links
        self.assertIn("Feed Updates", text)
        self.assertIn("### Zero links", text)
        self.assertIn("https://feed1.com: Network error", text)


if __name__ == "__main__":
    from unittest import main

    main()
