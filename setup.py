from setuptools import setup, find_packages

setup(
    name="archivist",
    version="1.0.0",
    packages=find_packages(),
    author="njzwj",
    author_email="njzwj2013@gmail.com",
    description="Organizing, summarizing, and categorizing web content and videos, making it simple to review and retrieve information",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="N/A",
    install_requires=[
        "click",
        "dependency-injector",
        "langchain",
        "langchain-openai",
        "langchain-community",
        "python-dotenv",
        "transformers",
        "django",
        "beautifulsoup4",
        "fake-useragent",
        "html2text",
        "markdown",
        "torch",
        "you-get",
    ],
    extras_require={
        "dev": ["pytest"],
    },
    entry_points={
        "console_scripts": [
            "arc=src.cli:main",
        ],
    },
)
