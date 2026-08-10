"""The network-egress guard is itself tested for being armed.

A verification that can only say "good" is not a verification: if the guard
in conftest.py silently stopped patching, every test would keep passing while
quietly regaining network access. This test proves the tripwire fires.
"""

from __future__ import annotations

import socket

import pytest


def test_real_network_egress_fails_loudly(guard_network_egress: str) -> None:
    assert guard_network_egress == "network egress guard active"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        with pytest.raises(pytest.fail.Exception, match="real network egress"):
            sock.connect(("192.0.2.1", 80))
