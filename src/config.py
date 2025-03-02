import os
import configparser


class Config:

    default_config_path = os.path.expanduser("~/.archivist.ini")

    default_config = {
        "Archivist": {
            "log_level": "debug",
            "workspace": "~/archivist",
            "gpt_provider": "AzureOpenAI",
        },
        "AzureOpenAI": {
            "endpoint": "https://contoso.openai.azure.com",
            "api_version": "2024-12-01-preview",
            "key": "YOUR_KEY",
            "deployment_smart": "gpt-4o",
            "deployment_efficient": "gpt-4o-mini",
            "deployment_embedding": "text-embedding-ada-003-small",
        },
        "Tools": {
            "tags": "economy,health,education,environment,technology,politics,society,culture,language,science,religion,history,geography,arts,sports,philosophy",
        },
    }

    def __init__(self, config_path=default_config_path):
        self.config_path = config_path

    def check_config_exists(self):
        return os.path.exists(self.config_path)

    def load_config(self):
        parser = configparser.ConfigParser()
        self.config = parser.read(self.config_path)

    def write_config(self, config=None):
        if config is None:
            config = self.default_config
        parser = configparser.ConfigParser()
        parser.read_dict(config)
        with open(self.config_path, "w") as configfile:
            parser.write(configfile)

    def get_config(self):
        if self.config is None:
            self.load_config()
        return self.config

    def __getitem__(self, key):
        return self.get_config()[key]
