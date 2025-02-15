import os
import json

from .config import get_config

config = get_config()


class Cache:

    def __init__(self, path=None):
        if path:
            self.cache_path = path
        else:
            self.cache_path = os.path.join(config.archivist_results_path, ".archivist")
        self.cache = self._load()

    def _load(self):
        if not os.path.exists(self.cache_path):
            return {}
        with open(self.cache_path, "r") as f:
            return json.load(f)

    def _save(self, data):
        with open(self.cache_path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)

    def write(self, key, value):
        self.cache[key] = value
        self._save(self.cache)

    def read(self, key):
        return self.cache.get(key, None)

    def delete(self, key):
        if key in self.cache:
            del self.cache[key]
            self._save(self.cache)


def get_cache(path=None) -> Cache:
    return Cache(path)
