from src.core.pipeline import Pipeline
from src.core.models import get_chat_model
from langchain_core.prompts import PromptTemplate

def c(inputs):
    return inputs.content


def get_write_brief_chain():
    model = get_chat_model()

    write_brief_chain = (
        PromptTemplate.from_template(
            """
        Transcript:
        ```
        {transcript}
        ```

        Task: Rewrite the provided transcript above into an outline and professional article, similar in style to *The Economist*. In **{language}**.

        Key Requirements:
        - Maintain Core Ideas: Preserve the main arguments and essential details.
        - Improve Structure & Flow: Ensure logical organization with smooth transitions.
        - Enhance Clarity & Depth: Keep the content informative, engaging, and nuanced.
        - Refine Style & Tone: Adopt a professional, polished, and journalistic tone.

        Writing Guidelines:
        - Introduction: Summarize key points concisely using bullet points.
        - Main Body: Develop ideas in well-structured paragraphs—avoid excessive lists or headings.
        - Detail Retention: Do not over-simplify; keep subtle details from the original.
        - Write the provided content into **{language}**. Retain original terms/names when meaning is unclear.

        Format Instructions:
        - Use Markdown for formatting.
        - Avoid excessive subheadings, but ensure readability.
        - 2 parts, the first part is the keypoints in bullet points, the second part is the article.
    
        Here is a format instruction:
        <format_instruction>
        [Keypoints in bullet points, possibly nested, but not required]
        ...
        ---
        [Body that is summarized and rewritten with details]
        </format_instruction>

        Here is a format example:
        <format_example>
        - In new research, scientists have discovered a new species of fish.
        - The fish was found in the Amazon River.
        - It has a unique color pattern.
        - The discovery is significant because it may help us understand the ecosystem better.
        - ...
        
        ---

        Recent studies have shown that the Amazon River is home to a new species of fish. The fish, which has a unique color pattern, was discovered by scientists during a research expedition. This discovery is significant because it may help us understand the ecosystem better. The new species is expected to be named after the lead researcher, Dr. Jane Doe...
        </format_example>

        - Place the final rewritten article **directly below** this line without any additional explanation, omitting any quote marks.
        """
        )
        | model
        | c
    )

    return write_brief_chain


def write_brief(inputs: dict, **kwargs) -> dict:
    language = kwargs.get("language", "Original language")
    if "language" not in kwargs:
        raise Warning("Target language not provided, using the original language")
    if "briefing" in inputs:
        return inputs
    write_brief_chain = get_write_brief_chain()
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
