from unittest import TestCase, mock
from feedmailer.app import App


class TestAppTestCase(TestCase):
    @mock.patch('feedmailer.app.Storage')
    @mock.patch('feedmailer.app.Config')
    @mock.patch('sys.argv', ['app.py', 'config.json', 'status.json'])
    def test_app_initialization(self, mock_config_class, mock_storage_class):
        mock_storage = mock.Mock()
        mock_storage.load.return_value = set()
        mock_storage_class.return_value = mock_storage
        
        app = App()
        
        mock_config_class.assert_called_once_with('config.json')
        mock_storage_class.assert_called_once_with('status.json')
        mock_storage.load.assert_called_once()
    
    @mock.patch('feedmailer.app.Mailer')
    @mock.patch('feedmailer.app.FeedProcessor')
    @mock.patch('feedmailer.app.Storage')
    @mock.patch('feedmailer.app.Config')
    @mock.patch('sys.argv', ['app.py', 'config.json', 'status.json'])
    def test_app_run_with_new_entries(self, mock_config_class, mock_storage_class, 
                                      mock_processor_class, mock_mailer_class):
        mock_config = mock.Mock()
        mock_config_class.return_value = mock_config
        
        mock_storage = mock.Mock()
        mock_storage.load.return_value = set()
        mock_storage_class.return_value = mock_storage
        
        mock_processor = mock.Mock()
        mock_entry = mock.Mock(link="https://example.com/1")
        mock_processor.found = [mock_entry]
        mock_processor.collect.return_value = [mock_entry]
        mock_processor.as_html.return_value = "<html><body><ul><li><a href='https://example.com/1'>Title</a></li></ul></body></html>"
        mock_processor.as_text.return_value = "* Title\n  https://example.com/1"
        mock_processor_class.return_value = mock_processor
        
        mock_mailer = mock.Mock()
        mock_mailer_class.return_value = mock_mailer
        
        app = App()
        app.run()
        
        mock_processor.collect.assert_called_once()
        mock_mailer.send.assert_called_once_with(
            "<html><body><ul><li><a href='https://example.com/1'>Title</a></li></ul></body></html>",
            "* Title\n  https://example.com/1"
        )
        mock_storage.save.assert_called_once()
    
    @mock.patch('feedmailer.app.Mailer')
    @mock.patch('feedmailer.app.FeedProcessor')
    @mock.patch('feedmailer.app.Storage')
    @mock.patch('feedmailer.app.Config')
    @mock.patch('sys.argv', ['app.py', 'config.json', 'status.json'])
    def test_app_run_without_new_entries(self, mock_config_class, mock_storage_class,
                                         mock_processor_class, mock_mailer_class):
        mock_storage = mock.Mock()
        mock_storage.load.return_value = set()
        mock_storage_class.return_value = mock_storage
        
        mock_processor = mock.Mock()
        mock_processor.found = []
        mock_processor.collect.return_value = []
        mock_processor_class.return_value = mock_processor
        
        mock_mailer = mock.Mock()
        mock_mailer_class.return_value = mock_mailer
        
        app = App()
        app.run()
        
        mock_processor.collect.assert_called_once()
        mock_mailer.send.assert_not_called()
        mock_storage.save.assert_not_called()
    
    @mock.patch('feedmailer.app.Storage')
    @mock.patch('feedmailer.app.Config')
    @mock.patch('sys.argv', ['app.py', 'config.json', 'status.json'])
    def test_app_update_state(self, mock_config_class, mock_storage_class):
        mock_storage = mock.Mock()
        mock_storage.load.return_value = {"https://example.com/old"}
        mock_storage_class.return_value = mock_storage
        
        app = App()
        
        mock_processor = mock.Mock()
        mock_entry = mock.Mock(link="https://example.com/new")
        mock_processor.found = [mock_entry]
        
        app._update_state(mock_processor)
        
        saved_links = mock_storage.save.call_args[0][0]
        self.assertIn("https://example.com/old", saved_links)
        self.assertIn("https://example.com/new", saved_links)


if __name__ == '__main__':
    from unittest import main
    main()
