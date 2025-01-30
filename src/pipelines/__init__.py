from src.core.pipeline import PipelineOrchestrator
from .brief import brief_pipeline
from .tag import tag_pipeline

orchestrator = PipelineOrchestrator()
orchestrator.register(brief_pipeline)
orchestrator.register(tag_pipeline)

__all__ = ["orchestrator"]
