from setuptools import setup, find_packages

setup(
    name="power-llm",
    version="0.1",
    packages=find_packages(),
    author="njzwj",
    description="A collection of utilities of LLM",
    entry_points={
        "console_scripts": [
            "get=src.cli:get",
            "brief=src.cli:brief",
        ],
    },
)
