"""Tests for the matrixllm package version."""

import matrixllm


def test_version_exists():
    """Test that the version is defined."""
    assert hasattr(matrixllm, "__version__")


def test_version_format():
    """Test that version follows semantic versioning format."""
    version = matrixllm.__version__
    assert isinstance(version, str)
    parts = version.split(".")
    assert len(parts) >= 2
    # Check that major and minor are numeric
    assert parts[0].isdigit()
    assert parts[1].isdigit()


def test_version_value():
    """Test the current version value."""
    assert matrixllm.__version__ == "0.2.0"


def test_all_exports():
    """Test that __all__ contains expected exports."""
    assert "__version__" in matrixllm.__all__
