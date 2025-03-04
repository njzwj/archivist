from transformers import pipeline

from src.config import Config

class HuggingfaceService:

    default_whisper_model = "openai/whisper-large-v3-turbo"

    def __init__(self, config: Config):
        self.config = config
        self.get_whisper_model(self.default_whisper_model)
    
    def get_whisper_model(self, whiser_model_name):
        self.whisper_model = pipeline(
            "automatic-speech-recognition",
            model=whiser_model_name,
            chunk_length_s=30,
        )
