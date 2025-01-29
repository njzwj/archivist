from src.core.pipeline import Pipeline
from src.core.models import get_chat_model
from langchain_core.prompts import PromptTemplate

model = get_chat_model()


def c(inputs):
    return inputs.content


write_article_chain = (
    PromptTemplate.from_template(
        """
    {transcript}
    ---

    **Task:** Rewrite the provided transcript into a professional article, similar in style to *The Economist*.  

    ### **Key Requirements:**  
    - **Maintain Core Ideas:** Preserve the main arguments and essential details.  
    - **Improve Structure & Flow:** Ensure logical organization with smooth transitions.  
    - **Enhance Clarity & Depth:** Keep the content informative, engaging, and nuanced.  
    - **Refine Style & Tone:** Adopt a professional, polished, and journalistic tone.  
    - **Length:** Comparable to an average blog post.  

    ### **Writing Guidelines:**  
    - **Introduction:** Summarize key points concisely using bullet points.  
    - **Main Body:** Develop ideas in well-structured paragraphs—avoid excessive lists or headings.  
    - **Language:** Use {language}. Retain original terms/names when meaning is unclear.  
    - **Detail Retention:** Do not over-simplify; keep subtle details from the original.  

    ### **Format Instructions:**  
    - Use **Markdown** for formatting.  
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


def write_article(inputs: dict, **kwargs) -> dict:
    language = inputs.get("language", "the original language")
    if "language" not in kwargs:
        raise Warning("Target language not provided, using the original language")
    if "article" in inputs:
        return inputs
    article = write_article_chain.invoke({**inputs, "language": language})
    return {**inputs, "article": article}


article_pipeline = Pipeline(
    "article",
    ["transcript"],
    ["article"],
    write_article)
