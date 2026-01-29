import json
import tempfile
import os
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
            "to": "recipient@example.com"
        }
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
        
        config = Config(config_file)
        
        self.assertEqual(config.urls, config_data["urls"])
        self.assertEqual(config.sender, config_data["from"])
        self.assertEqual(config.recipient, config_data["to"])
    
    def test_config_handles_missing_fields(self):
        config_file = os.path.join(self.temp_dir, "config.json")
        config_data = {"from": "sender@example.com"}
        with open(config_file, 'w') as f:
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
        with open(config_file, 'w') as f:
            f.write("invalid json {")
        
        with self.assertRaises(json.JSONDecodeError):
            Config(config_file)


if __name__ == '__main__':
    from unittest import main
    main()
