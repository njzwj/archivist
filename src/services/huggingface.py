from transformers import pipeline
import logging

from src.config import Config

class HuggingfaceService:

    default_whisper_model = "openai/whisper-large-v3-turbo"

    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.get_whisper_model(self.default_whisper_model)
    
    def get_whisper_model(self, whiser_model_name):
        self.whisper_model = pipeline(
            "automatic-speech-recognition",
            model=whiser_model_name,
            chunk_length_s=30,
        )

    def transcribe(self, audio_path):
        chunks = self.whisper_model(audio_path, batch_size=4, return_timestamps=True)["chunks"]
        transcript = "\n".join([chunk["text"] for chunk in chunks])
        return transcript
