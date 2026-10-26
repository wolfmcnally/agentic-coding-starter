"""Synthetic qualifying runs use persistent storage; disposable fixtures clean up normally."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def tmp_path():
    root = Path(__file__).resolve().parents[1] / ".kickoff" / "proof-runtime"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="case-", dir=root) as directory:
        yield Path(directory)
