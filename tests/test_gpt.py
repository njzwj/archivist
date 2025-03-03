import pytest
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

from src.config import Config
from src.container import Container
from src.services import GptService


@pytest.fixture
def mock_config():
    config = Config()
    config.config = config.default_config
    return config


@pytest.fixture
def container():
    return Container()


def test_gpt_service_azure_openai(mock_config, container):
    container.config.override(mock_config)
    container.gpt_service.reset()
    gpt_service = container.gpt_service()
    assert gpt_service.gpt_provider == "AzureOpenAI"
    assert gpt_service.chat_model_smart is not None
    assert type(gpt_service.chat_model_smart) == AzureChatOpenAI
    assert gpt_service.chat_model_efficient is not None
    assert type(gpt_service.chat_model_efficient) == AzureChatOpenAI
    assert gpt_service.embedding_model is not None
    assert type(gpt_service.embedding_model) == AzureOpenAIEmbeddings
