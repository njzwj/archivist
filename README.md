# Archivist

![License](https://img.shields.io/badge/license-MIT-purple)
![Status](https://img.shields.io/badge/status-under_development-lightgray)

TL;DR: **Archivist** is designed to
- Keep track of what we've consumed (online videos).
- Extract valuable insights.
- Retrieve and read about it later.

The long version: **Archivist** is designed to efficiently manage and process consumed content, primarily from video platforms such as Bilibili and YouTube. Future updates will extend support to additional content types.

## Key Features

1. **Content Management**: Handles video content from public platforms, extracting and organizing information for further processing.
2. **Data Processing**: Provides flexible processing capabilities, including:
   - **Tagging**
   - **Summarization**
   - **Idea and insight generation**
3. **Extensibility**: Built with simple, modular mechanisms for easy expansion.

## Installation and Setup

### Prerequisites
- **Conda Installation**: Ensure Conda is installed on your system.
- **Environment Setup**: Create a new Conda environment and install the required dependencies.

### Environment Configuration
- Run `init` gives you an env file in user folder.
- Define necessary environment variables within the `.env` file.
- By default, the system reads from `~/.archivist.env`, but you can specify a different path using the `ARCHIVIST_ENV_PATH` environment variable.
- The output directory is also specified within this `.env` file.

## Fetching Video Transcripts

To retrieve a transcript from a video, run the following command:

```bash
get 'https://www.youtube.com/...' -o output/path language=Japanese tags=learning,health,...
```

- The transcript is saved as a JSON file, named after the video title.
- If `output-dir` is omitted, the file is saved in the default directory.
- Once typed kwargs, it caches and you don't need to type again.

Next time run

```bash
get 'https://www.youtube.com/...'
```

It uses the last kwargs you use.

## Running Pipelines on Documents

Pipelines can be executed on existing documents to generate new summaries and insights. Usage:

```bash
mpipe pipeline [kwargs, [...]]
```

To generate tags for each document:

```bash
mpipe tag tags=learning,studying
```

To generate a briefing:

```bash
mpipe brief language=Japanese
```

## View Formatted Contents

To start a local server for browsing tagged posts, run the following command:

```bash
serve [argv...]
serve 8001
```

This equals to `manage.py runserver` in django.

![Server](./images/serve.png)

## TODOs

[] Support Cookie for websites protected by login.

[x] Add cache kwargs so no need to type every time.

[x] Develope `mpipe`: A tool for tagging, rewriting, summarizing, and modifying stored files.

[x] Added `serve`: A server tool to display categorized pages for viewing collected content.

[x] Enhance `get` to fetch more text data from pages, including those without videos.

[x] Streamline default pipelines for get so that each time I won't need to run `mpipe` for multiple times.


## References

- **You-Get**: A reliable tool for video content retrieval.
- **Hugging Face**: A powerful and user-friendly NLP framework supporting various processing tasks.
