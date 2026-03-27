"""Shared pytest fixtures for QIAS Mawarith RAG tests."""

import pytest
import yaml
from pathlib import Path


@pytest.fixture
def project_root():
    """Return project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def config_path(project_root):
    """Return path to config file."""
    return str(project_root / "config" / "rag_config.yaml")


@pytest.fixture
def config(config_path):
    """Load and return the configuration dictionary."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture
def sample_question():
    """Return a sample Arabic inheritance question."""
    return "مات وترك: أم و أب و بنت. ما هو نصيب كل وريث؟"


@pytest.fixture
def sample_heirs():
    """Return a sample heir list for testing."""
    return [
        {"heir": "أم", "count": 1},
        {"heir": "أب", "count": 1},
        {"heir": "بنت", "count": 1},
    ]
