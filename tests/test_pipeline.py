import pytest

from src.core.pipeline import Pipeline, PipelineOrchestrator

def test_pipeline():
    def process(inputs: dict, **kwargs) -> dict:
        return inputs

    pipeline = Pipeline("test", ["input"], ["output"], process)
    orchestrator = PipelineOrchestrator()
    orchestrator.register(pipeline)

    inputs = {"input": "test"}
    result = orchestrator.process("test", inputs)
    assert result == inputs

def test_pipeline_with_loop():
    def process(inputs: dict, **kwargs) -> dict:
        return inputs

    p1 = Pipeline("p1", ["i"], ["j"], process)
    p2 = Pipeline("p2", ["j"], ["k"], process)
    p3 = Pipeline("p3", ["k"], ["i"], process)
    orchestrator = PipelineOrchestrator()
    orchestrator.register(p1)
    orchestrator.register(p2)
    with pytest.raises(ValueError):
        orchestrator.register(p3)
