# Archivist

![License](https://img.shields.io/badge/license-MIT-purple)
![Status](https://img.shields.io/badge/status-under_development-lightgray)

TL;DR: **Archivist** is designed to
- Keep track of what we've consumed, including online videos and web pages.
- Extract valuable insights.
- Retrieve and read about it later.

## Usage

Clone the repo, run `pip install -e .` to install package to your environment. `conda` is recommended.

To get a page/video transcript to your workspace.

```bash
arc get 'https://www.youtube.com/...'
```

To read these contents:

```bash
arc serve
```

![Server](./images/serve.png)

## Installation and Setup

### Prerequisites

- **Conda Installation**: Ensure Conda is installed on your system.
- **Environment Setup**: Create a new Conda environment and install the required dependencies.
- **ffmpeg**: Archivist relies on ffmpeg to extract audios.

### Environment Configuration

- Run `arc init` to get a copy of `.archivist.ini` to your home folder `~`.
- Fill config file.

```ini
# config
[Archivist]
log_level = debug # log level, info | debug | warning | error
workspace = ~/archivist # workspace
gpt_provider = AzureOpenAI # Only support Azure OpenAI for now

[AzureOpenAI]
endpoint = https://yourservice.openai.azure.com
api_version = 2024-12-01-preview
key = YOUR-KEY
deployment_smart = gpt-4o
deployment_efficient = gpt-4o-mini
deployment_embedding = text-embedding-ada-003-small

[Tools]
tags = economy,health,education,environment,technology,politics,society,culture,language,science,religion,history,geography,arts,sports,philosophy # tagging
language = zh-cn # output language
```

## Appendix

Archivist uses the following tools:

1. **Huggingface** is used to provide `whisper-v3-turbo` model to transcript. Make sure your computer is able to run this model.
1. **ffmpeg** is used to extract audio from video.
1. **you-get** is used to fetch video data.

Known issues:

1. Ouputs from inner tools are not supressed.
1. Cookies are not supported, some websites will block the video downloading.
