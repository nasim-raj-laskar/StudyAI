import pytest
import os

def test_src_structure():
    """Verify that the src directory structure is intact."""
    assert os.path.exists("src")
    assert os.path.exists("src/common")
    assert os.path.exists("src/utils")

def test_import_app():
    """Verify that the main app components can be imported."""
    try:
        from src.utils.helpers import QuizManager
        assert QuizManager is not None
    except ImportError as e:
        pytest.fail(f"Failed to import QuizManager: {e}")
