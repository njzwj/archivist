from src.core.pipeline import Pipeline
from src.core.models import get_chat_model
from langchain_core.prompts import PromptTemplate


model = get_chat_model()


def c(inputs):
    return inputs.content


tagging_chain = (
    PromptTemplate.from_template(
        """
    {object}
    ---
    **Task:** Tag the provided content. You can select one or multiple tags from below:
    {tags}
    Output the tags in a list format, for example:
    tag1,tag2
    because the output will be processed by splitting the string by comma, output direct after this line of prompt, without any additional explanation.
    """)
    | model
    | c
)


def tag_content(inputs: dict, **kwargs) -> dict:
    if "tags" not in kwargs:
        raise ValueError("Tags not provided")
    if "tags" in inputs:
        return inputs
    tags = tagging_chain.invoke({**inputs, "tags": kwargs["tags"]})
    return {**inputs, "tags": tags}


tag_pipeline = Pipeline(
    name="tag",
    input_keys=["object"],
    output_keys=["tags"],
    process_fn=tag_content,
)
