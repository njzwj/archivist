from langchain_core.prompts import PromptTemplate
import json
import warnings

from src.core.pipeline import Pipeline
from src.core.models import get_chat_model
from src.utils import get_config


model = get_chat_model()
config = get_config()


def c(inputs):
    return inputs.content


summarize_chain = (
    PromptTemplate.from_template(
        """
    {object}
    ---
    Above is a piece of information pulled and processed from the internet.
    Summarize the content in a few sentences. The topic and key points should be clear.
    Write directly below this line without any additional explanation.
    """)
    | model
    | c
)


tagging_chain = (
    PromptTemplate.from_template(
        """
    {inputs}
    ---
    **Task:** Tag the provided content.
    Output the tags in a specific format, for example:
    
    Input is about a new product launch in E3. Avaiable tags are: economy,technology,history
    Economy is the best tag, the other two are not relevant. So, output will be:
    economy 1
    technology 0
    history 0

    Another example. If input is about modern word history and economy. Available tags are: economy,technology,history
    Economy and history are relevant, technology is not. So, output will be:
    economy 1
    technology 0
    history 1

    A bad example. If input is about US economy in a decade. Available tags are: economy,technology,history
    If output is:
    US 1
    economy 1
    technology 0
    history 0
    it is wrong. US is not a tag. So, output will be:
    economy 1
    technology 0
    history 0

    because the output will be processed by splitting the string by comma, output direct after this line of prompt, without any additional explanation. Available tags are: [{tags}]. You can choose one or multiple tags. Make sure to output the tags in the correct format.
    """)
    | model
    | c
)


def tag_content(inputs: dict, **kwargs) -> dict:
    if "tags" not in kwargs:
        kwargs["tags"] = config
        warnings.warn("Tags not provided, default is set by environment variable TAGGING_CATEGORIES")
    obj = json.dumps(inputs, ensure_ascii=False)
    summary = summarize_chain.invoke({"object": obj})
    tags = tagging_chain.invoke({"inputs": summary, "tags": kwargs["tags"]})
    tags = tags.split("\n")
    tags = [tag.split(" ") for tag in tags]
    tags = [tag[0] for tag in tags if tag[1] == "1"]
    return {**inputs, "tags": tags}


tag_pipeline = Pipeline(
    name="tag",
    input_keys=["title"],
    output_keys=["tags"],
    process=tag_content,
)
