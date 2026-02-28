from unittest import TestCase, mock

from feedmailer.mailer import Mailer, SendmailBackend, SMTPBackend


class TestMailerTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.mock_config = mock.Mock()
        self.mock_config.sender = "sender@example.com"
        self.mock_config.recipient = "recipient@example.com"
        self.mock_config.mail_backend = "sendmail"

    def test_mailer_send_with_sendmail_backend(self):
        """Test sending with default sendmail backend."""
        mailer = Mailer(self.mock_config)
        html_body = "<p>Test email body</p>"
        text_body = "Test email body"

        mock_proc = mock.MagicMock()

        with mock.patch("subprocess.Popen", return_value=mock_proc) as mock_popen:
            mailer.send(html_body, text_body)

        mock_popen.assert_called_once_with(["sendmail", "-t"], stdin=-1)

        # Check that communicate was called
        call_args = mock_proc.communicate.call_args
        sent_message = call_args[1]["input"].decode("utf-8")

        # Verify multipart structure
        self.assertIn("MIME-Version: 1.0", sent_message)
        self.assertIn("Content-Type: multipart/alternative", sent_message)
        self.assertIn("Content-Type: text/plain; charset=utf-8", sent_message)
        self.assertIn("Content-Type: text/html; charset=utf-8", sent_message)

        # Verify content in both parts
        self.assertIn("<p>Test email body</p>", sent_message)  # HTML part
        self.assertIn("Test email body", sent_message)  # Plain text part

    def test_mailer_send_with_list(self):
        """Test sending email with list content."""
        mailer = Mailer(self.mock_config)
        html_body = '<ul><li><a href="https://example.com">Title</a></li></ul>'
        text_body = "* Title\n  https://example.com"

        mock_proc = mock.MagicMock()

        with mock.patch("subprocess.Popen", return_value=mock_proc):
            mailer.send(html_body, text_body)

        call_args = mock_proc.communicate.call_args
        sent_message = call_args[1]["input"].decode("utf-8")

        # Verify multipart email with both HTML and plain text
        self.assertIn("Content-Type: multipart/alternative", sent_message)
        self.assertIn("Content-Type: text/plain; charset=utf-8", sent_message)
        self.assertIn("Content-Type: text/html; charset=utf-8", sent_message)

        # Verify HTML content
        self.assertIn('<a href="https://example.com">Title</a>', sent_message)
        self.assertIn("<ul>", sent_message)
        self.assertIn("<li>", sent_message)

    def test_mailer_with_smtp_backend(self):
        """Test sending with SMTP backend."""
        self.mock_config.mail_backend = "smtp"
        self.mock_config.smtp_host = "smtp.example.com"
        self.mock_config.smtp_port = 587
        self.mock_config.smtp_username = "user@example.com"
        self.mock_config.smtp_password = "password123"
        self.mock_config.smtp_use_tls = True

        mailer = Mailer(self.mock_config)
        html_body = "<p>Test SMTP email</p>"
        text_body = "Test SMTP email"

        with mock.patch("smtplib.SMTP") as mock_smtp_class:
            mock_server = mock.MagicMock()
            mock_smtp_class.return_value.__enter__.return_value = mock_server

            mailer.send(html_body, text_body, subject="Test Subject")

            # Verify SMTP connection
            mock_smtp_class.assert_called_once_with("smtp.example.com", 587)
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once_with("user@example.com", "password123")
            mock_server.send_message.assert_called_once()

            # Verify message content
            sent_msg = mock_server.send_message.call_args[0][0]
            self.assertEqual(sent_msg["From"], "sender@example.com")
            self.assertEqual(sent_msg["To"], "recipient@example.com")
            self.assertEqual(sent_msg["Subject"], "Test Subject")

    def test_sendmail_backend_direct(self):
        """Test SendmailBackend directly."""
        backend = SendmailBackend()

        mock_proc = mock.MagicMock()
        with mock.patch("subprocess.Popen", return_value=mock_proc) as mock_popen:
            backend.send(
                sender="from@example.com",
                recipient="to@example.com",
                subject="Direct Test",
                html_body="<b>HTML</b>",
                text_body="TEXT",
            )

            mock_popen.assert_called_once()
            call_args = mock_proc.communicate.call_args
            sent_message = call_args[1]["input"].decode("utf-8")

            self.assertIn("From: from@example.com", sent_message)
            self.assertIn("To: to@example.com", sent_message)
            self.assertIn("Subject: Direct Test", sent_message)
            self.assertIn("<b>HTML</b>", sent_message)
            self.assertIn("TEXT", sent_message)

    def test_smtp_backend_direct(self):
        """Test SMTPBackend directly."""
        backend = SMTPBackend(
            host="mail.example.com",
            port=465,
            username="testuser",
            password="testpass",
            use_tls=False,
        )

        with mock.patch("smtplib.SMTP") as mock_smtp_class:
            mock_server = mock.MagicMock()
            mock_smtp_class.return_value.__enter__.return_value = mock_server

            backend.send(
                sender="from@example.com",
                recipient="to@example.com",
                subject="Direct SMTP Test",
                html_body="<b>HTML Content</b>",
                text_body="Text Content",
            )

            mock_smtp_class.assert_called_once_with("mail.example.com", 465)
            mock_server.starttls.assert_not_called()  # use_tls=False
            mock_server.login.assert_called_once_with("testuser", "testpass")


if __name__ == "__main__":
    from unittest import main

    main()
