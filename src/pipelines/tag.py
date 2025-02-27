from langchain_core.prompts import PromptTemplate
import json
import warnings

from src.core.pipeline import Pipeline
from src.core.models import get_chat_model
from src.utils import get_config


config = get_config()


def c(inputs):
    return inputs.content


def get_summarize_chain():
    model = get_chat_model()
    summarize_chain = (
        PromptTemplate.from_template(
            """
        ```
        {object}
        ```
        Above is a piece of information pulled and processed from the internet.
        Summarize the content in a few sentences. The topic and key points should be clear. No more than 200 words.
        Write directly below this line without any additional explanation.
        """
        )
        | model
        | c
    )
    return summarize_chain


def get_tagging_chain():
    model = get_chat_model()
    tagging_chain = (
        PromptTemplate.from_template(
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
        | model
        | c
    )
    return tagging_chain


def tag_content(inputs: dict, **kwargs) -> dict:
    if "tags" in inputs.keys():
        return inputs

    if "tags" not in kwargs:
        kwargs["tags"] = config.tagging_categories
        warnings.warn(
            "Tags not provided, default is set by environment variable TAGGING_CATEGORIES"
        )
    available_tags = kwargs["tags"]
    obj = json.dumps(inputs, ensure_ascii=False)

    summarize_chain = get_summarize_chain()
    tagging_chain = get_tagging_chain()
    summary = summarize_chain.invoke({"object": obj})
    tags = tagging_chain.invoke({"inputs": summary, "tags": available_tags})

    available_tags = available_tags.split(",")
    tags = tags.split(",")
    if len(available_tags) > len(tags):
        available_tags = available_tags[: len(tags)]
    tags = [int(tag) for tag in tags]
    tags = [tag for i, tag in enumerate(available_tags) if tags[i] == 1]
    return {**inputs, "tags": tags}


description_string = """Tag the content and save it under the "tags" key.

Arguments:
  tags        Comma-separated tags for the content (e.g., "economy,technology,history").
              Default: set by the environment variable TAGGING_CATEGORIES.
"""


tag_pipeline = Pipeline(
    name="tag",
    input_keys=["title"],
    output_keys=["tags"],
    description=description_string,
    process=tag_content,
)
