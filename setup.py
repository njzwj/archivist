from setuptools import setup, find_packages

setup(
    name="archivist",
    version="0.1.1",
    packages=find_packages(),
    author="njzwj",
    description="Organizing, summarizing, and categorizing web content and videos, making it simple to review and retrieve information",
    entry_points={
        "console_scripts": [
            "get=src.cli:get",
            "mpipe=src.cli:mpipe",
            "serve=src.cli:serve",
        ],
    },
)
