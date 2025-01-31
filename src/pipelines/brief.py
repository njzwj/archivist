from src.core.pipeline import Pipeline
from src.core.models import get_chat_model
from langchain_core.prompts import PromptTemplate

model = get_chat_model()


def c(inputs):
    return inputs.content


write_brief_chain = (
    PromptTemplate.from_template(
        """
    Transcript:
    ```
    {transcript}
    ```

    Task: Rewrite the provided transcript above into a professional article, similar in style to *The Economist*. In **{language}**.

    Key Requirements:
    - Maintain Core Ideas: Preserve the main arguments and essential details.
    - Improve Structure & Flow: Ensure logical organization with smooth transitions.
    - Enhance Clarity & Depth: Keep the content informative, engaging, and nuanced.
    - Refine Style & Tone: Adopt a professional, polished, and journalistic tone.
    - Length: Comparable to an average blog post.

    Writing Guidelines:
    - Introduction: Summarize key points concisely using bullet points.
    - Main Body: Develop ideas in well-structured paragraphs—avoid excessive lists or headings.
    - Detail Retention: Do not over-simplify; keep subtle details from the original.
    - Write the provided content into **{language}**. Retain original terms/names when meaning is unclear.

    Format Instructions:
    - Use Markdown for formatting.
    - Avoid excessive subheadings, but ensure readability.
 
    Here is an example:
    - Bulleting 1
      - 1.1
      ...
    ...
    
    Body

    - Place the final rewritten article **directly below** this prompt—without any additional explanation.
    """
    )
    | model
    | c
)


def write_brief(inputs: dict, **kwargs) -> dict:
    language = kwargs.get("language", "Original language")
    if "language" not in kwargs:
        raise Warning("Target language not provided, using the original language")
    if "briefing" in inputs:
        return inputs
    brief = write_brief_chain.invoke({**inputs, "language": language})
    return {**inputs, "briefing": brief}


description_string = """Create a brief transcript of the article and save it under the "briefing" key.
Skips if the "briefing" key already exists.

Arguments:
  language    The language for the brief (default: original language).
              Example: "kolingon" or "english".
"""


brief_pipeline = Pipeline(
    name="brief",
    input_keys=["transcript"],
    output_keys=["brief"],
    description=description_string,
    process=write_brief,
)
