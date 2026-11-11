"""Synthetic qualifying runs use persistent storage; disposable fixtures clean up normally."""

import os
import tempfile
from pathlib import Path

import pytest


def isolate_fixture_git_signing(environment: dict[str, str]) -> None:
    """Fixture repositories never sign: the operator's signing setup is not under test.

    A machine that signs every commit hands that setting to each throwaway repository a
    test creates, and a signing agent asked to sign many commits at once refuses some of
    them. Git reads these variables after every configuration file, so the override holds
    whatever the machine configures. Entries a caller already supplied are kept, and a
    nested test run that inherits these does not add them twice.
    """
    count = int(environment.get("GIT_CONFIG_COUNT", "0") or "0")
    supplied = {environment.get(f"GIT_CONFIG_KEY_{index}") for index in range(count)}
    for key in ("commit.gpgsign", "tag.gpgsign"):
        if key in supplied:
            continue
        environment[f"GIT_CONFIG_KEY_{count}"] = key
        environment[f"GIT_CONFIG_VALUE_{count}"] = "false"
        count += 1
    environment["GIT_CONFIG_COUNT"] = str(count)


isolate_fixture_git_signing(os.environ)


@pytest.fixture
def tmp_path():
    root = Path(__file__).resolve().parents[1] / ".kickoff" / "proof-runtime"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="case-", dir=root) as directory:
        yield Path(directory)
