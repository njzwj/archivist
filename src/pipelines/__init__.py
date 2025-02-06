from src.core.pipeline import PipelineOrchestrator
from .brief import brief_pipeline
from .tag import tag_pipeline
from .transcript import transcript_pipeline

orchestrator = PipelineOrchestrator()
orchestrator.register(brief_pipeline)
orchestrator.register(tag_pipeline)
orchestrator.register(transcript_pipeline)

__all__ = ["orchestrator"]
