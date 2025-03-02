from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

from src.config import Config

class GptProvider:

    def __init__(self, config: Config):
        self.config = config
        self.gpt_provider = config["Archivist"]["gpt_provider"]
        if self.gpt_provider == "AzureOpenAI":
            self.get_azure_openai_models(config["AzureOpenAI"])
        else:
            raise ValueError(f"Unsupported GPT provider: {self.gpt_provider}")
    
    def get_azure_openai_models(self, config):
        self.chat_model_smart = AzureChatOpenAI(
            azure_endpoint=config["endpoint"],
            api_version=config["api_version"],
            api_key=config["key"],
            deployment_name=config["deployment_smart"],
        )
        self.chat_model_efficient = AzureChatOpenAI(
            azure_endpoint=config["endpoint"],
            api_version=config["api_version"],
            api_key=config["key"],
            deployment_name=config["deployment_efficient"],
        )
        self.embedding_model = AzureOpenAIEmbeddings(
            azure_endpoint=config["endpoint"],
            api_version=config["api_version"],
            api_key=config["key"],
            deployment_name=config["deployment_embedding"],
        )
