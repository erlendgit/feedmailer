import json


class Storage:
    def __init__(self, path):
        self.path = path

    def load(self):
        try:
            with open(self.path, "r") as f:
                return set(json.load(f).get("seen_links", []))
        except (FileNotFoundError, json.JSONDecodeError):
            return set()

    def save(self, seen_links):
        with open(self.path, "w") as f:
            json.dump({"seen_links": list(seen_links)}, f)
