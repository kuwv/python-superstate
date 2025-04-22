"""Provide tests for project version."""
from superstate import __version__


def test_version() -> None:
    """Test project metadata version."""
    assert __version__ == '1.6.2a3'
