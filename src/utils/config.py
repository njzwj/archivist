# Config definition, load config from certain directory, etc
import dotenv
import os
import platform

ARCHIVIST_ENV_PATH = os.path.expanduser(
    os.getenv("ARCHIVIST_ENV_PATH", "~/.archivist.env")
)

if not os.path.exists(ARCHIVIST_ENV_PATH):
    if os.path.exists(os.path.expanduser("~/.archivist.env")):
        ARCHIVIST_ENV_PATH = os.path.expanduser("~/.archivist.env")
    elif os.path.exists(".env"):
        ARCHIVIST_ENV_PATH = ".env"
    else:
        ARCHIVIST_ENV_PATH = ".env.sample"

dotenv.load_dotenv(dotenv_path=ARCHIVIST_ENV_PATH)

cookies = dict(
    darwin=dict(
        chrome="~/Library/Application Support/Google/Chrome/Default/Cookies",
        edge="~/Library/Application Support/Microsoft Edge/Default/Cookies",
        firefox="~/Library/Application Support/Firefox/Profiles",
    ),
    linux=dict(
        chrome="~/.config/google-chrome/Default/Cookies",
        edge="~/.config/microsoft-edge/Default/Cookies",
        firefox="~/.mozilla/firefox",
    ),
    windows=dict(
        chrome="~/AppData/Local/Google/Chrome/User Data/Default/Cookies",
        edge="~/AppData/Local/Microsoft/Edge/User Data/Default/Cookies",
        firefox="~/AppData/Roaming/Mozilla/Firefox/Profiles",
    ),
)


def search_cookies_firefox(path):
    # traverse and find path/*.default/cookies.sqlite
    for root, dirs, files in os.walk(path):
        for dir in dirs:
            if dir.endswith(".default") or dir.endswith(".default-release"):
                if os.path.exists(os.path.join(root, dir, "cookies.sqlite")):
                    return os.path.join(root, dir, "cookies.sqlite")
    return None


def load_cookies_platform(paths):
    # enable firefox for now
    for browser, path in paths.items():
        p = os.path.expanduser(path)
        if os.path.exists(p):
            if browser == "firefox":
                p = search_cookies_firefox(p)
                return p
    return None


def get_platform():
    system = platform.system().lower()
    if system == "darwin":
        return "darwin"
    elif system == "windows":
        return "windows"
    elif system == "linux":
        return "linux"
    else:
        return "unknown"


def load_cookies():
    platform = get_platform()
    path = load_cookies_platform(cookies[platform])
    if path:
        return path
    raise FileNotFoundError("Cannot find cookies file")


class Config:

    archivist_env_path = ARCHIVIST_ENV_PATH
    azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    azure_openai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    archivist_results_path = (
        "~"
        if os.getenv("ARCHIVIST_RESULTS_PATH") is None
        else os.path.expanduser(os.getenv("ARCHIVIST_RESULTS_PATH"))
    )
    tagging_categories = os.getenv("TAGGING_CATEGORIES", "")


def get_config():
    return Config()
