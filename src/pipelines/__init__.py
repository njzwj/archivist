from src.core.pipeline import PipelineOrchestrator
from .article import article_pipeline
from .tag import tag_pipeline

orchestrator = PipelineOrchestrator()
orchestrator.register(article_pipeline)
orchestrator.register(tag_pipeline)

__all__ = [
    "orchestrator"
]
