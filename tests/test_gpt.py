import pytest
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

from src.config import Config
from src.container import Container
from src.services import GptProvider

@pytest.fixture
def mock_config():
    config = Config()
    config.config = config.default_config
    return config

@pytest.fixture
def container():
    return Container()

def test_gpt_provider_azure_openai(mock_config, container):
    container.config.override(mock_config)
    container.gpt_provider.reset()
    gpt_provider = container.gpt_provider()
    assert gpt_provider.gpt_provider == "AzureOpenAI"
    assert gpt_provider.chat_model_smart is not None
    assert type(gpt_provider.chat_model_smart) == AzureChatOpenAI
    assert gpt_provider.chat_model_efficient is not None
    assert type(gpt_provider.chat_model_efficient) == AzureChatOpenAI
    assert gpt_provider.embedding_model is not None
    assert type(gpt_provider.embedding_model) == AzureOpenAIEmbeddings
