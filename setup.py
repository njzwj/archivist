from setuptools import setup, find_packages

setup(
    name="archivist",
    version="0.1.1",
    packages=find_packages(),
    author="njzwj",
    author_email="njzwj2013@gmail.com",
    description="Organizing, summarizing, and categorizing web content and videos, making it simple to review and retrieve information",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="N/A",
    install_requires=[],
    extras_require={
        "dev": ["pytest"],
    },
    entry_points={
        "console_scripts": [
            "get=src.cli:get",
            "mpipe=src.cli:mpipe",
            "serve=src.cli:serve",
        ],
    },
)
