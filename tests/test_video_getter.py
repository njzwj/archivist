import pytest

from src.container import Container

@pytest.fixture
def container():
    return Container()

@pytest.mark.parametrize("input_str,expected", [
])
def test_path_extractor(container, input_str, expected):
    service = container.video_getter_service()
    result = service.extract_path(input_str)
    assert result == expected
