from unittest import TestCase, mock
from feedmailer.mailer import Mailer


class TestMailerTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.mock_config = mock.Mock()
        self.mock_config.sender = "sender@example.com"
        self.mock_config.recipient = "recipient@example.com"
    
    def test_mailer_send(self):
        mailer = Mailer(self.mock_config)
        body = "Test email body"
        
        mock_proc = mock.MagicMock()
        
        with mock.patch('subprocess.Popen', return_value=mock_proc) as mock_popen:
            mailer.send(body)
        
        mock_popen.assert_called_once_with(["sendmail", "-t"], stdin=-1)
        
        # Check that communicate was called
        call_args = mock_proc.communicate.call_args
        sent_message = call_args[1]['input'].decode('utf-8')

        # Verify multipart structure
        self.assertIn("MIME-Version: 1.0", sent_message)
        self.assertIn("Content-Type: multipart/alternative", sent_message)
        self.assertIn("Content-Type: text/plain; charset=utf-8", sent_message)
        self.assertIn("Content-Type: text/html; charset=utf-8", sent_message)

        # Verify content in both parts
        self.assertIn("<p>Test email body</p>", sent_message)  # HTML part
        self.assertIn("Test email body", sent_message)  # Plain text part

    def test_mailer_send_with_markdown(self):
        mailer = Mailer(self.mock_config)
        body = "* [Title](https://example.com)"
        
        mock_proc = mock.MagicMock()
        
        with mock.patch('subprocess.Popen', return_value=mock_proc):
            mailer.send(body)
        
        call_args = mock_proc.communicate.call_args
        sent_message = call_args[1]['input'].decode('utf-8')
        
        # Verify multipart email with both HTML and plain text
        self.assertIn("Content-Type: multipart/alternative", sent_message)
        self.assertIn("Content-Type: text/plain; charset=utf-8", sent_message)
        self.assertIn("Content-Type: text/html; charset=utf-8", sent_message)

        # Verify markdown was converted to HTML
        self.assertIn('<a href="https://example.com">Title</a>', sent_message)
        self.assertIn('<ul>', sent_message)
        self.assertIn('<li>', sent_message)


if __name__ == '__main__':
    from unittest import main
    main()
