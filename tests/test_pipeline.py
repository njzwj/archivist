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


def test_pipeline_call_generate():
    def p1(inputs: dict, **kwargs) -> dict:
        return {**inputs, "j": inputs["i"] + 1}

    def p2(inputs: dict, **kwargs) -> dict:
        return {**inputs, "k": inputs["j"] + 1}

    p1 = Pipeline("p1", ["i"], ["j"], p1)
    p2 = Pipeline("p2", ["j"], ["k"], p2)
    orchestrator = PipelineOrchestrator()
    orchestrator.register(p1)
    orchestrator.register(p2)
    inputs = {"i": 1}
    result = orchestrator.process("p1", inputs)
    assert result == {"i": 1, "j": 2}
    result = orchestrator.process("p2", inputs)
    assert result == {"i": 1, "j": 2, "k": 3}
