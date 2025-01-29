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


def test_process_sequence():
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


def test_process_branch():
    def p1(inputs: dict, **kwargs) -> dict:
        return {**inputs, "j": inputs["i"] + 1}

    def p2(inputs: dict, **kwargs) -> dict:
        return {**inputs, "k": inputs["i"] * 2}
    
    def p3(inputs: dict, **kwargs) -> dict:
        return {**inputs, "l": inputs["j"] * 3 + inputs["k"]}
    
    def p4(inputs: dict, **kwargs) -> dict:
        return {**inputs, "m": inputs["l"] * 2}
    
    def p5(inputs: dict, **kwargs) -> dict:
        return {**inputs, "n": inputs["l"] * 3}
    
    p1 = Pipeline("p1", ["i"], ["j"], p1)
    p2 = Pipeline("p2", ["i"], ["k"], p2)
    p3 = Pipeline("p3", ["j", "k"], ["l"], p3)
    p4 = Pipeline("p4", ["l"], ["m"], p4)
    p5 = Pipeline("p5", ["l"], ["n"], p5)
    orchestrator = PipelineOrchestrator()
    orchestrator.register(p1)
    orchestrator.register(p2)
    orchestrator.register(p3)
    orchestrator.register(p4)
    orchestrator.register(p5)
    inputs = {"i": 1}
    result = orchestrator.process("p3", inputs)
    assert result == {"i": 1, "j": 2, "k": 2, "l": 8}
    result = orchestrator.process("p5", inputs)
    assert result == {"i": 1, "j": 2, "k": 2, "l": 8, "n": 24}


def test_process_missing_input():
    def process(inputs: dict, **kwargs) -> dict:
        return {**inputs, "j": inputs["i"] + 1}
    
    p1 = Pipeline("p1", ["i"], ["j"], process)
    orchestrator = PipelineOrchestrator()
    orchestrator.register(p1)
    inputs = {"x": 1}
    with pytest.raises(ValueError):
        orchestrator.process("p1", inputs)
