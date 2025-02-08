from src.core.pipeline import PipelineOrchestrator
from .brief import brief_pipeline
from .tag import tag_pipeline
from .transcript import transcript_pipeline
from .scrape import scrape_pipeline

orchestrator = PipelineOrchestrator()
orchestrator.register(brief_pipeline)
orchestrator.register(tag_pipeline)
orchestrator.register(transcript_pipeline)
orchestrator.register(scrape_pipeline)

__all__ = ["orchestrator"]
