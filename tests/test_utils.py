import pytest
from src.utils import parse_arguments


def test_parse_arguments():
    args = [
        "output_dir=/tmp",
        "url=https://www.youtube.com/watch?v=123",
        "language=Chinese",
    ]
    result = parse_arguments(args)
    assert result == {
        "output_dir": "/tmp",
        "url": "https://www.youtube.com/watch?v=123",
        "language": "Chinese",
    }
