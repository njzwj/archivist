from langchain_openai import AzureChatOpenAI
from transformers import pipeline

from ..utils import get_config

config = get_config()


def get_azure_chat_openai(**kwargs):
    model = AzureChatOpenAI(
        azure_endpoint=config.azure_openai_endpoint,
        azure_deployment=config.azure_openai_deployment,
        openai_api_version=config.azure_openai_api_version,
        openai_api_key=config.azure_openai_api_key,
        temperature=0,
        **kwargs,
    )
    return model


def get_chat_model(**kwargs):
    """
    Placeholder function for more chat models in the future.
    """
    return get_azure_chat_openai(**kwargs)


def get_hf_whisper_large_v3_turbo(**kwargs):
    model = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-large-v3-turbo",
        chunk_length_s=30,
        **kwargs,
    )
    return model
