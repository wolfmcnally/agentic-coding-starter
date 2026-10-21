"""POSIX test-command hang supervision, separate from performance measurement."""

from __future__ import annotations

import math
import os
import signal
import subprocess
import sys
import threading
from collections.abc import Sequence
from pathlib import Path

INCOMPLETE = 124
DEFAULT_HANG_SECONDS = 1800


def _stop(process: subprocess.Popen[str], grace: float) -> str:
    """Escalate within the one owned group, retaining any cleanup uncertainty."""
    errors = []
    for signum in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(process.pid, signum)
        except ProcessLookupError:
            pass
        except PermissionError as exc:
            errors.append(f"owned group cleanup could not signal {signum}: {exc}")
        if signum == signal.SIGTERM:
            try:
                process.communicate(timeout=grace)
            except subprocess.TimeoutExpired:
                pass
    return "\n".join(errors)


def _group_exists(group_id: int) -> bool:
    try:
        os.killpg(group_id, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def run_command(
    command: Sequence[str],
    *,
    cwd: Path,
    timeout: float = DEFAULT_HANG_SECONDS,
    capture: bool = False,
    cleanup_grace: float = 0.5,
    environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Return 124 for incomplete work; preserve completed child statuses.

    The monotonic deadline includes child setup/teardown and ignores chatter.
    The child owns a new session: TERM/INT/HUP are forwarded through this
    supervisor; SIGKILL of the supervisor cannot be handled. Startup before
    this process and descendants detaching again need enclosing supervision.
    """
    if isinstance(timeout, bool) or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("hang deadline must be finite and positive")
    if isinstance(cleanup_grace, bool) or not math.isfinite(cleanup_grace) or cleanup_grace <= 0:
        raise ValueError("cleanup grace must be finite and positive")
    old_handlers = {}
    process = None
    cancelled = False
    cleaning = False

    def interrupted(_signum: int, _frame: object) -> None:
        nonlocal cancelled
        cancelled = True
        if process is not None and not cleaning:
            raise InterruptedError("supervisor interrupted")

    if threading.current_thread() is threading.main_thread():
        for signum in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
            old_handlers[signum] = signal.signal(signum, interrupted)
    try:
        process = subprocess.Popen(
            list(command),
            cwd=cwd,
            text=True,
            start_new_session=True,
            env=environment,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.PIPE if capture else None,
        )
        cleanup_detail = ""
        try:
            if cancelled:
                raise InterruptedError("interrupted during child startup")
            stdout, stderr = process.communicate(timeout=timeout)
            code = process.returncode
            if code < 0 or _group_exists(process.pid):
                cleaning = True
                cleanup_detail = _stop(process, cleanup_grace)
                code = INCOMPLETE
        except (subprocess.TimeoutExpired, InterruptedError, KeyboardInterrupt):
            cleaning = True
            cleanup_detail = _stop(process, cleanup_grace)
            try:
                stdout, stderr = process.communicate(timeout=2)
            except subprocess.TimeoutExpired as exc:
                stdout = exc.output or ""
                stderr = exc.stderr or ""
                if isinstance(stdout, bytes):
                    stdout = stdout.decode(errors="replace")
                if isinstance(stderr, bytes):
                    stderr = stderr.decode(errors="replace")
                stderr += "\noutput drain incomplete; a descendant escaped supervision"
            code = INCOMPLETE
        if code == INCOMPLETE:
            diagnostic = (
                "TEST INCOMPLETE: hang, interruption or outstanding child; correctness unknown"
            )
            if cleanup_detail:
                diagnostic += "\n" + cleanup_detail
            if capture:
                stderr = (stderr or "") + "\n" + diagnostic
            else:
                print(diagnostic, file=sys.stderr, flush=True)
        return subprocess.CompletedProcess(list(command), code, stdout or "", stderr or "")
    finally:
        for signum, handler in old_handlers.items():
            signal.signal(signum, handler)


def main() -> int:
    import yaml

    root = Path(__file__).resolve().parents[2]
    try:
        manifest = yaml.safe_load((root / "tests/proof-estate.yaml").read_text())
        timeout = manifest["hang_timeout_seconds"]
        result = run_command([sys.executable, *sys.argv[1:]], cwd=root, timeout=timeout)
    except (OSError, ValueError, TypeError, KeyError, yaml.YAMLError) as exc:
        print(f"TEST INCOMPLETE: supervisor could not run: {exc}", file=sys.stderr)
        return INCOMPLETE
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
