from unittest import TestCase, mock
from feedmailer.feed_processor import FeedProcessor


class TestFeedProcessorTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.mock_config = mock.Mock()
        self.mock_config.urls = ["https://example.com/feed"]
    
    def test_feed_processor_collect_new_entries(self):
        seen_links = set()
        processor = FeedProcessor(self.mock_config, seen_links)
        
        mock_entry1 = mock.Mock(link="https://example.com/entry1", title="Entry 1")
        mock_entry2 = mock.Mock(link="https://example.com/entry2", title="Entry 2")
        mock_feed = mock.Mock(entries=[mock_entry1, mock_entry2])
        
        with mock.patch('feedparser.parse', return_value=mock_feed):
            result = processor.collect()
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], mock_entry1)
        self.assertEqual(result[1], mock_entry2)
    
    def test_feed_processor_filters_seen_entries(self):
        seen_links = {"https://example.com/entry1"}
        processor = FeedProcessor(self.mock_config, seen_links)
        
        mock_entry1 = mock.Mock(link="https://example.com/entry1", title="Entry 1")
        mock_entry2 = mock.Mock(link="https://example.com/entry2", title="Entry 2")
        mock_feed = mock.Mock(entries=[mock_entry1, mock_entry2])
        
        with mock.patch('feedparser.parse', return_value=mock_feed):
            result = processor.collect()
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], mock_entry2)
    
    def test_feed_processor_multiple_feeds(self):
        self.mock_config.urls = ["https://example.com/feed1", "https://example.com/feed2"]
        processor = FeedProcessor(self.mock_config, set())
        
        mock_entry1 = mock.Mock(link="https://example.com/entry1", title="Entry 1")
        mock_entry2 = mock.Mock(link="https://example.com/entry2", title="Entry 2")
        
        def mock_parse(url):
            if url == "https://example.com/feed1":
                return mock.Mock(entries=[mock_entry1])
            else:
                return mock.Mock(entries=[mock_entry2])
        
        with mock.patch('feedparser.parse', side_effect=mock_parse):
            result = processor.collect()
        
        self.assertEqual(len(result), 2)
    
    def test_feed_processor_as_markdown(self):
        processor = FeedProcessor(mock.Mock(), set())
        processor.found = [
            mock.Mock(title="Entry 1", link="https://example.com/1"),
            mock.Mock(title="Entry 2", link="https://example.com/2")
        ]
        
        markdown = processor.as_markdown()
        
        self.assertEqual(markdown, "* [Entry 1](https://example.com/1)\n* [Entry 2](https://example.com/2)")
    
    def test_feed_processor_as_markdown_empty(self):
        processor = FeedProcessor(mock.Mock(), set())
        processor.found = []
        
        markdown = processor.as_markdown()
        
        self.assertEqual(markdown, "")


if __name__ == '__main__':
    from unittest import main
    main()
