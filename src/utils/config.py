# Config definition, load config from certain directory, etc
import dotenv
import os

POWER_LLM_ENV_PATH = os.path.expanduser(
    os.getenv("POWER_LLM_ENV_PATH", "~/.power-llm.env")
)

dotenv.load_dotenv(dotenv_path=POWER_LLM_ENV_PATH)


class Config:

    power_llm_env_path = POWER_LLM_ENV_PATH
    azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    azure_openai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    power_llm_results_path = os.path.expanduser(os.getenv("POWER_LLM_RESULTS_PATH"))


def get_config():
    return Config()
