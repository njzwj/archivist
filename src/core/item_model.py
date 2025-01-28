import os
import json


class ItemModel:

    def __init__(self, data, file_path=None):
        self.data = data
        self.file_path = file_path

    def save(self, file_path, **kwargs):
        if file_path is None:
            file_path = self.file_path
        with open(file_path, "w") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2, **kwargs)

    def keys(self):
        return self.data.keys()

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    @staticmethod
    def from_file(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
        return ItemModel(data, file_path)
