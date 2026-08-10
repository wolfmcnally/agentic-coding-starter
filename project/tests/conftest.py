"""Shared fixtures for the example test suite."""

from __future__ import annotations

import socket
from collections.abc import Iterator

import pytest

_LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


@pytest.fixture(scope="session", autouse=True)
def guard_network_egress() -> Iterator[str]:
    """Fail any test that opens a real network connection to a nonlocal host.

    Tests are hermetic: a test that silently reaches the network passes or
    fails with the weather. Local sockets (loopback, unix-domain) stay allowed
    so servers under test still work. The guard is itself exercised by
    test_hermeticity.py — a guard whose failure mode is silence needs a test
    proving it is armed.
    """
    sentinel = "network egress guard active"
    original_connect = socket.socket.connect

    def guarded_connect(self: socket.socket, address: object) -> None:
        if self.family == getattr(socket, "AF_UNIX", object()):
            return original_connect(self, address)
        host = address[0] if isinstance(address, tuple) and address else None
        if isinstance(host, str) and host in _LOCAL_HOSTS:
            return original_connect(self, address)
        pytest.fail(f"test attempted real network egress: connect({address!r})")

    patcher = pytest.MonkeyPatch()
    patcher.setattr(socket.socket, "connect", guarded_connect)
    try:
        yield sentinel
    finally:
        patcher.undo()
