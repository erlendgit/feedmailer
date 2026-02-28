import json
import os
import tempfile
from unittest import TestCase

from feedmailer.config import Config


class TestConfigTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_config_loads_data(self):
        config_file = os.path.join(self.temp_dir, "config.json")
        config_data = {
            "urls": ["https://example.com/feed1", "https://example.com/feed2"],
            "from": "sender@example.com",
            "to": "recipient@example.com",
        }
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        config = Config(config_file)

        self.assertEqual(config.urls, config_data["urls"])
        self.assertEqual(config.sender, config_data["from"])
        self.assertEqual(config.recipient, config_data["to"])

    def test_config_handles_missing_fields(self):
        config_file = os.path.join(self.temp_dir, "config.json")
        config_data = {"from": "sender@example.com"}
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        config = Config(config_file)

        self.assertEqual(config.urls, [])
        self.assertEqual(config.sender, "sender@example.com")
        self.assertIsNone(config.recipient)

    def test_config_raises_on_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            Config("/nonexistent/config.json")

    def test_config_raises_on_invalid_json(self):
        config_file = os.path.join(self.temp_dir, "config.json")
        with open(config_file, "w") as f:
            f.write("invalid json {")

        with self.assertRaises(json.JSONDecodeError):
            Config(config_file)

    def test_config_default_mail_backend(self):
        """Test that default mail backend is sendmail."""
        config_file = os.path.join(self.temp_dir, "config.json")
        config_data = {
            "urls": ["https://example.com/feed"],
            "from": "sender@example.com",
            "to": "recipient@example.com",
        }
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        config = Config(config_file)

        self.assertEqual(config.mail_backend, "sendmail")

    def test_config_smtp_backend(self):
        """Test loading SMTP backend configuration."""
        config_file = os.path.join(self.temp_dir, "config.json")
        config_data = {
            "urls": ["https://example.com/feed"],
            "from": "sender@example.com",
            "to": "recipient@example.com",
            "mail_backend": "smtp",
            "smtp": {
                "host": "smtp.gmail.com",
                "port": 587,
                "username": "user@gmail.com",
                "password": "secret",
                "use_tls": True,
            },
        }
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        config = Config(config_file)

        self.assertEqual(config.mail_backend, "smtp")
        self.assertEqual(config.smtp_host, "smtp.gmail.com")
        self.assertEqual(config.smtp_port, 587)
        self.assertEqual(config.smtp_username, "user@gmail.com")
        self.assertEqual(config.smtp_password, "secret")
        self.assertTrue(config.smtp_use_tls)

    def test_config_smtp_defaults(self):
        """Test SMTP defaults when only backend is specified."""
        config_file = os.path.join(self.temp_dir, "config.json")
        config_data = {
            "urls": ["https://example.com/feed"],
            "from": "sender@example.com",
            "to": "recipient@example.com",
            "mail_backend": "smtp",
        }
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        config = Config(config_file)

        self.assertEqual(config.mail_backend, "smtp")
        self.assertEqual(config.smtp_host, "localhost")
        self.assertEqual(config.smtp_port, 587)
        self.assertIsNone(config.smtp_username)
        self.assertIsNone(config.smtp_password)
        self.assertTrue(config.smtp_use_tls)


if __name__ == "__main__":
    from unittest import main

    main()
