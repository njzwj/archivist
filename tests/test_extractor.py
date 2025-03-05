import pytest

from src.container import Container
from src.config import Config


@pytest.fixture
def container():
    return Container()


@pytest.fixture
def mock_config():
    config = Config()
    config.config = config.default_config
    return config


@pytest.mark.parametrize(
    "input_tags,available_tags,expected",
    [
        ("0,1,1,0", "a,b,c,d", ["b", "c"]),
        ("1,,1", "a,b,c,d", ["a", "c"]),
        ("0,0,1,0,0,0,1", "a,b,c c,d", ["c c"]),
        ("0,1,0,", "a,b,c", ["b"]),
    ],
)
def test_convert_tag_output(
    mock_config, container, input_tags, available_tags, expected: list
):
    container.config.override(mock_config)
    container.extractor_service.reset()
    extractor_service = container.extractor_service()
    result = extractor_service.convert_tag_output(input_tags, available_tags)
    assert result == expected


@pytest.mark.parametrize(
    "content,expected",
    [
        ('```json{"key": "value"}', dict(key="value")),
        ('```json{"key": 1}```', dict(key=1)),
        ('{"key": [1, 2, 3]}', dict(key=[1, 2, 3])),
        ('```{"key": {"key2": 1}}```', dict(key=dict(key2=1))),
    ],
)
def test_extract_json(mock_config, container, content, expected):
    container.config.override(mock_config)
    container.extractor_service.reset()
    extractor_service = container.extractor_service()
    result = extractor_service.extract_json(content)
    assert result == expected
