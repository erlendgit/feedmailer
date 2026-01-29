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
        
        expected_msg = (
            "From: sender@example.com\n"
            "To: recipient@example.com\n"
            "Subject: Feed Updates\n"
            "Content-Type: text/markdown\n\n"
            "Test email body"
        )
        mock_proc.communicate.assert_called_once_with(input=expected_msg.encode('utf-8'))
    
    def test_mailer_send_with_markdown(self):
        mailer = Mailer(self.mock_config)
        body = "* [Title](https://example.com)"
        
        mock_proc = mock.MagicMock()
        
        with mock.patch('subprocess.Popen', return_value=mock_proc):
            mailer.send(body)
        
        call_args = mock_proc.communicate.call_args
        sent_message = call_args[1]['input'].decode('utf-8')
        
        self.assertIn("Content-Type: text/markdown", sent_message)
        self.assertIn(body, sent_message)


if __name__ == '__main__':
    from unittest import main
    main()
