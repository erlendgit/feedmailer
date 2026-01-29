import json
import tempfile
import os
from unittest import TestCase
from feedmailer.storage import Storage


class TestStorageTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_storage_load_empty_file(self):
        storage_file = os.path.join(self.temp_dir, "storage.json")
        storage = Storage(storage_file)
        
        result = storage.load()
        
        self.assertEqual(result, set())
    
    def test_storage_load_existing_data(self):
        storage_file = os.path.join(self.temp_dir, "storage.json")
        seen_links = ["https://example.com/1", "https://example.com/2"]
        with open(storage_file, 'w') as f:
            json.dump({"seen_links": seen_links}, f)
        
        storage = Storage(storage_file)
        result = storage.load()
        
        self.assertEqual(result, set(seen_links))
    
    def test_storage_load_invalid_json(self):
        storage_file = os.path.join(self.temp_dir, "storage.json")
        with open(storage_file, 'w') as f:
            f.write("invalid json")
        
        storage = Storage(storage_file)
        result = storage.load()
        
        self.assertEqual(result, set())
    
    def test_storage_save(self):
        storage_file = os.path.join(self.temp_dir, "storage.json")
        storage = Storage(storage_file)
        seen_links = {"https://example.com/1", "https://example.com/2"}
        
        storage.save(seen_links)
        
        with open(storage_file, 'r') as f:
            saved_data = json.load(f)
        self.assertEqual(set(saved_data["seen_links"]), seen_links)
    
    def test_storage_save_overwrites(self):
        storage_file = os.path.join(self.temp_dir, "storage.json")
        with open(storage_file, 'w') as f:
            json.dump({"seen_links": ["old"]}, f)
        storage = Storage(storage_file)
        
        new_links = {"https://example.com/new"}
        storage.save(new_links)
        
        with open(storage_file, 'r') as f:
            saved_data = json.load(f)
        self.assertEqual(set(saved_data["seen_links"]), new_links)
        self.assertNotIn("old", saved_data["seen_links"])


if __name__ == '__main__':
    from unittest import main
    main()
