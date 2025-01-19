from langchain_core.prompts import PromptTemplate
import json
import os
import re
import subprocess
import datetime

from ..core.models import get_azure_chat_openai

model = get_azure_chat_openai()

def c(inputs):
    return inputs.content

refine_transcript = PromptTemplate.from_template(
    """
    Refine the following transcript:
    '''
    {transcript}
    '''
    Above is a transcript of a video downloaded from the internet by a model.
    Refine the transcript, fix errors caused by the model, and make any necessary edits.
    Possible errors include misheard words, incorrect punctuation, homophones, and other transcription errors.
    Write directly without any explanation or additional information.
    """
) | model | c

extract_title = PromptTemplate.from_template(
    """
    '''
    {transcript}
    '''
    Above is a transcript of a video.
    Based on the above transcript, extract the title of the video.
    - Use the language of the transcript. If transcript is in English, extract the title in English.
      If Chinese, extract the title in Chinese, so on and so forth.
    - Return plain text, without any formatting, spaces, line breaks, etc.
    - Title should be a single sentence, not a paragraph.
    - Clear and concise, to the point. Best describe the content of the video.
    """
) | model | c

extract_tags = (
    lambda inputs: { "input": json.dumps(inputs, ensure_ascii=False) }
) | PromptTemplate.from_template(
    """
    '''
    {input}
    '''
    Above is a piece of information scraped and processed from the internet.
    You act as a content creator and need to generate tags for this piece of information.
    - The tags should be relevant to the content.
    - The tags should be concise and informative.
    - The tags should be separated by commas.
    - Tags should in English.
    - Tags should be single words or short phrases.
    Write directly below this line, without any explanation. Because post processing splits the text by comma, avoid using commas in the tags.
    """
) | model | c | (lambda x: [tag.strip() for tag in x.split(",")])

write_article = PromptTemplate.from_template(
    """
    {transcript}
    ---
    Above is a content from internet. **Rewrite** it as a professional article (like The Economist article). Here are the key requirements:
    - Keep the main idea and key points.
    - Into well organized article, informative and engaging.
    - Well structured and developed.
    - In the size of an average blog post.
    - Papagraphs should be informative, not too scattered.
    - Reorganize if needed, better order, flow and coherence.
    - Write using {language}. For names, terms you cannot infer, keep them in the original language.
    Format requirements:
    - Summarize keypoints briefly in the beginning, in lists and bullet points.
    - Rewrite the main content in paragraphs.
    - Use markdown.
    - Avoid using too many headings, lists, and bullet points.
    Example:
    - 要点1
      - 要点1.1
      ...
    ...
    
    正文内容

    Output directly below this line, without any explanation.
    """
) | model | c

format_markdown = PromptTemplate.from_template(
    """
    {content}
    ---
    Above is a markdown content. **Format** it to a more readable markdown content. Here are the key requirements:
    - Keep the original content.
    - Use h2 as each section title.
    - Use h1 as the title of the whole article.
    - Unless necessary, avoid using h3 and h4.
    - Make each section format aligned.
    Output directly below this line, without any explanation and xml tags.
    """
) | model | c
