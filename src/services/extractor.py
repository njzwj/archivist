import logging
import json
from langchain_core.prompts import PromptTemplate

from src.services import GptService
from src.config import Config


class ExtractorService:

    summarize_prompt = PromptTemplate.from_template(
        """
        ```
        {inputs}
        ```
        Above is a piece of information pulled and processed from the internet.
        Summarize the content in a few sentences. The topic and key points should be clear. No more than 200 words.
        Write directly below this line without any additional explanation.
        """
    )

    tag_prompt = PromptTemplate.from_template(
        """
        Content:
        ```
        {inputs}
        ```
        **Task:** Tag the provided content.
        Output the tags in a specific format, for example:
        
        Input is about a new product launch in E3. Avaiable tags are: [economy,technology,history]
        Economy is the best tag, the other two are not relevant. So, output will be:
        1,0,0

        Another example. If input is about modern word history and economy. Available tags are: [economy,technology,history]
        Economy and history are relevant, technology is not. So, output will be:
        1,0,1

        A bad example. If input is about US economy in a decade. Available tags are: [economy,technology,history]
        A bad output will be:
        1,0,0,1
        Because there are only 3 tags available, so the output should be 3 digits.
        1,0,0 is the correct output.

        So the output should be comma separated 0s and 1s only. And MUST be in the same order and same number as the available tags.

        because the output will be processed by splitting the string by comma, output direct after this line of prompt, without any additional explanation. Available tags are: [{tags}]. You can choose one or multiple tags. Make sure to output in the correct format.
        """
    )

    write_outline_prompt = PromptTemplate.from_template(
        """
        ```
        {inputs}
        ```
        **Task:** Write an outline for the provided content.
        Output the outline in a specific format, for example:
        
        Input is about a new product launch in E3. Outline should be:
        1. Introduction
          1. Keypoints are
          2. What's new
        2. Product Description
          1. Sony's new product
          2. Microsoft's new product
        3. Features
        4. Conclusion

        Guidelines:
        - Write conclusions or assertions. Describe the conclusion or the point the original text is trying to make, not description of the topic. e.g., "The product is expected to be a game-changer in the industry." not "The product expectations.", should be "The ecnonomy has been growing at a steady pace." not "The economy growing rate."
        - Use bullet points for lists and sublists.
        Write directly below this line without any additional explanation. Using markdown format. In the language of **{language}**. Skip the triple backticks.
        """
    )

    write_article_prompt = PromptTemplate.from_template(
        """
        ```
        {inputs}
        ```
        **Task:** Write an article on the provided content/transcript above.

        Key Requirements:
        - Maintain Core Ideas: Preserve the main arguments and essential details.
        - Average article length: If the content is too long, make it more compact, retain information by make it more concise.
        - Avoid spoken language: Convert spoken language to written language.
        - Improve Structure & Flow: Ensure logical organization with smooth transitions.
        - Enhance Clarity & Depth: Keep the content informative, engaging, and nuanced.
        - Refine Style & Tone: Adopt a professional, polished, and journalistic tone.

        Writing Guidelines:
        - Develop ideas in well-structured paragraphs—avoid excessive lists or headings.
        - Use clear, concise language—avoid jargon, complex terms, or overly casual expressions.
        - Maintain a formal, professional tone—avoid personal opinions or informal language.
        - Do not over simplify.
        - Write the provided content into **{language}**. Retain original terms/names when meaning is unclear.

        Format Instructions:
        - Use Markdown for formatting.
        - Avoid excessive subheadings, but ensure readability.

        **Task:** Write an article on the provided content.
        Write directly below this line without any additional explanation. In the language of **{language}**. Skip the triple backticks. Write direcly below this line without any additional explanation.
        """
    )

    extract_metadata_prompt = PromptTemplate.from_template(
        """Here is a web-scrapped content. Please extract the keys from the content.
        content:
        ```
        {inputs}
        ```
        Extract the following keys:
        - published_at (the published date time, e.g., 2022-01-31 18:23:45)
        - author
        Ouput format:
        ```json
        {{"title": "How to invest", "published_at": "2021-01-01 17:20:15","author": "John Doe"}}
        ```
        But replace the values with the actual values from the content.
        The original content may not contain exactly the same name for the keys. Decide the best value to use for each key.
        If the key is not found, leave it empty.
        Do not include any other keys.
        """
    )

    def __init__(self, gpt: GptService, config: Config, logger: logging.Logger):
        self.gpt = gpt
        self.config = config
        self.logger = logger

    def convert_tag_output(self, tags: str, available_tags: str):
        tags = tags.split(",")
        available_tags = available_tags.split(",")
        if len(available_tags) > len(tags):
            available_tags = available_tags[: len(tags)]
        tags = [int(tag) if tag.strip().isdigit() else 0 for tag in tags]
        tags = [tag for i, tag in enumerate(available_tags) if tags[i] == 1]
        return tags

    def extract_json(self, content: str):
        content = content.replace("```json", "").replace("```", "")
        return json.loads(content)

    def extract_metadata(self, content: str):
        metadata_chain = (
            self.extract_metadata_prompt
            | self.gpt.chat_model_efficient.bind(max_tokens=256, temperature=0)
        )
        metadata = metadata_chain.invoke(dict(inputs=content)).content
        metadata = self.extract_json(metadata)
        if (
            "published_at" not in metadata
            or "author" not in metadata
            or "title" not in metadata
        ):
            self.logger.warning(
                f"Failed to extract metadata. Extracted: {json.dumps(metadata, ensure_ascii=False)}"
            )
        return metadata

    def extract_tags(self, content: str, tags: str = None):
        if tags is None:
            tags = self.config["Tools"]["tags"]
        summarize_chain = self.summarize_prompt | self.gpt.chat_model_efficient.bind(
            max_tokens=512, temperature=0
        )
        tagging_chain = self.tag_prompt | self.gpt.chat_model_smart.bind(
            max_tokens=256, temperature=0
        )
        summary = summarize_chain.invoke(dict(inputs=content)).content
        self.logger.debug(f"Summary: {summary}")
        tags_raw = tagging_chain.invoke(dict(inputs=content, tags=tags)).content

        return self.convert_tag_output(tags_raw, tags)

    def rewrite_content(self, content: str, language: str = None):
        if language is None:
            language = self.config["Tools"]["language"]

        bulletin_chain = self.write_outline_prompt | self.gpt.chat_model_efficient.bind(
            max_tokens=512, temperature=0
        )
        bulletin = bulletin_chain.invoke(
            dict(inputs=content, language=language)
        ).content

        rewrite_chain = self.write_article_prompt | self.gpt.chat_model_smart.bind(
            max_tokens=4096, temperature=0
        )
        rewritten_content = rewrite_chain.invoke(
            dict(inputs=content, language=language)
        ).content

        return f"{bulletin}\n\n---\n\n{rewritten_content}"
