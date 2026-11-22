"""POSIX test-command supervision: truthful exits and process-group cleanup.

No elapsed limit applies. A command runs until it finishes or the operator or an enclosing
tool cancels it; how long it took is a diagnostic, reported elsewhere.
"""

from __future__ import annotations

import locale
import math
import os
import selectors
import signal
import subprocess
import sys
import threading
import time
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path

INCOMPLETE = 124
SETTLE_POLL_SECONDS = 0.005
# How often a capturing supervisor looks for the command's exit while something else
# keeps the output open. It delays nothing: output that arrives wakes the loop at once.
EXIT_POLL_SECONDS = 0.05


def _group_gone(group_id: int) -> bool | None:
    """True when the group has no member, False when it has one, None when refused."""
    try:
        os.killpg(group_id, 0)
    except ProcessLookupError:
        return True
    except PermissionError:
        return None
    return False


def _stop(process: subprocess.Popen[bytes], grace: float) -> str:
    """Escalate within the one owned group, retaining any cleanup uncertainty.

    The grace bounds cleanup after a cancellation or an established leftover child. It is
    never a limit on a running test.
    """
    errors = []
    for signum in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(process.pid, signum)
        except ProcessLookupError:
            pass
        except PermissionError as exc:
            errors.append(f"owned group cleanup could not signal {signum}: {exc}")
        deadline = time.monotonic() + grace
        while time.monotonic() < deadline:
            process.poll()
            if _group_gone(process.pid):
                break
            time.sleep(SETTLE_POLL_SECONDS)
    if process.poll() is None or not _group_gone(process.pid):
        errors.append("the owned process group could not be confirmed gone")
    return "\n".join(errors)


def _group_outstanding(group_id: int, settle: float) -> bool:
    """Whether the child's group still has a member after its leader exited.

    A refused probe is ambiguous. For a few milliseconds after the last member of a
    group exits, and before the system has finished collecting it, this platform refuses
    a signal to that group exactly as it would refuse one to a group the caller may not
    signal. Counting the refusal as a live child reported finished commands as incomplete
    under parallel load. So a refusal is probed again within the cleanup grace: a group
    that turns out to be gone is finished, one that answers is outstanding, and one still
    refusing at the deadline is treated as outstanding, because that cannot be told apart
    from a child that escaped.
    """
    deadline = time.monotonic() + settle
    while True:
        gone = _group_gone(group_id)
        if gone is not None:
            return not gone
        if time.monotonic() >= deadline:
            return True
        time.sleep(SETTLE_POLL_SECONDS)


class _Capture:
    """Both output pipes, read without blocking by the supervising thread itself.

    A pipe reports end of file only when every writer has closed it, and reports "nothing
    yet" while a writer remains. So once the command and its group are gone, one more read
    tells a pipe that is finished from one that some other process still holds, with no
    clock involved.
    """

    def __init__(self, process: subprocess.Popen[bytes]) -> None:
        self.selector = selectors.DefaultSelector()
        self.chunks: dict[int, list[bytes]] = {}
        self.order = []
        for stream in (process.stdout, process.stderr):
            descriptor = stream.fileno()  # type: ignore[union-attr]
            os.set_blocking(descriptor, False)
            self.selector.register(descriptor, selectors.EVENT_READ)
            self.chunks[descriptor] = []
            self.order.append(descriptor)

    def read_ready(self) -> None:
        """Take everything already written; forget a pipe that reached end of file."""
        for descriptor in [key.fd for key in self.selector.get_map().values()]:
            while True:
                try:
                    chunk = os.read(descriptor, 65536)
                except BlockingIOError:
                    break
                except OSError:
                    chunk = b""
                if not chunk:
                    self.selector.unregister(descriptor)
                    break
                self.chunks[descriptor].append(chunk)

    def follow(self, process: subprocess.Popen[bytes], cancelled: Callable[[], bool]) -> int:
        """Read until the command exits, however long that takes.

        The selector absorbs an interruption raised inside its wait, so cancellation is
        also read here.
        """
        while self.selector.get_map():
            self.selector.select(EXIT_POLL_SECONDS)
            if cancelled():
                raise InterruptedError("supervisor interrupted")
            self.read_ready()
            if process.poll() is not None:
                break
        return process.wait()

    def still_open(self) -> bool:
        self.read_ready()
        return bool(self.selector.get_map())

    def text(self) -> tuple[str, str]:
        encoding = locale.getpreferredencoding(False)
        stdout, stderr = (
            b"".join(self.chunks[descriptor])
            .decode(encoding, errors="replace")
            .replace("\r\n", "\n")
            .replace("\r", "\n")
            for descriptor in self.order
        )
        return stdout, stderr


def _signal_name(number: int) -> str:
    try:
        return signal.Signals(number).name
    except ValueError:
        return f"signal {number}"


def run_command(
    command: Sequence[str],
    *,
    cwd: Path,
    capture: bool = False,
    cleanup_grace: float = 0.5,
) -> subprocess.CompletedProcess[str]:
    """Run to completion with no elapsed limit; return 124 only for incomplete work.

    A completed command keeps its own exit status. The result is incomplete, with the
    reason named, when the run was cancelled, when a signal ended the command, or when
    the command exited and left work behind: a member of its process group, or a
    descendant outside the group that still holds the captured output.

    The child owns a new session: TERM/INT/HUP are forwarded through this supervisor;
    SIGKILL of the supervisor cannot be handled. Startup before this process and
    descendants detaching again need enclosing supervision.
    """
    if isinstance(cleanup_grace, bool) or not math.isfinite(cleanup_grace) or cleanup_grace <= 0:
        raise ValueError("cleanup grace must be finite and positive")
    old_handlers = {}
    process = None
    cancelled: int | None = None
    cleaning = False

    def interrupted(signum: int, _frame: object) -> None:
        nonlocal cancelled
        if cancelled is None:
            cancelled = signum
        if process is not None and not cleaning:
            raise InterruptedError("supervisor interrupted")

    if threading.current_thread() is threading.main_thread():
        for signum in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
            old_handlers[signum] = signal.signal(signum, interrupted)
    try:
        process = subprocess.Popen(
            list(command),
            cwd=cwd,
            start_new_session=True,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.PIPE if capture else None,
        )
        output = _Capture(process) if capture else None
        code = INCOMPLETE
        reason = ""
        cleanup_detail = ""
        try:
            if cancelled is not None:
                raise InterruptedError("interrupted during child startup")
            code = (
                output.follow(process, lambda: cancelled is not None) if output else process.wait()
            )
            if code < 0:
                reason = f"{_signal_name(-code)} ended the test command"
            elif _group_outstanding(process.pid, cleanup_grace):
                reason = (
                    f"the test command exited with status {code} "
                    "and left a member of its process group running"
                )
            cleaning = True
            if reason:
                cleanup_detail = _stop(process, cleanup_grace)
        except (InterruptedError, KeyboardInterrupt):
            cleaning = True
            name = _signal_name(cancelled) if cancelled is not None else "SIGINT"
            reason = f"cancelled by {name} before the test command finished"
            cleanup_detail = _stop(process, cleanup_grace)
        stdout = stderr = ""
        if output:
            held = "a descendant outside the process group still holds the captured output"
            if output.still_open():
                if reason:
                    cleanup_detail = "\n".join(filter(None, (cleanup_detail, held)))
                else:
                    reason = f"the test command exited with status {code}, and {held}"
            stdout, stderr = output.text()
        if not reason:
            return subprocess.CompletedProcess(list(command), code, stdout, stderr)
        diagnostic = f"TEST INCOMPLETE: {reason}; correctness unknown"
        if cleanup_detail:
            diagnostic += "\n" + cleanup_detail
        if capture:
            stderr += "\n" + diagnostic
        else:
            print(diagnostic, file=sys.stderr, flush=True)
        return subprocess.CompletedProcess(list(command), INCOMPLETE, stdout, stderr)
    finally:
        if process is not None:
            for stream in (process.stdout, process.stderr):
                if stream is not None:
                    stream.close()
        for signum, handler in old_handlers.items():
            signal.signal(signum, handler)


def pytest_arguments(arguments: Sequence[str]) -> list[str]:
    """Parallelize independent pytest work without multiplying nested pools.

    Explicit pytest worker options remain the diagnostic override. Single-function
    selections and collection do not repay worker startup. Automatic workers use
    the scheduler's CPU-based bound, with an explicit pytest diagnostic override.
    """
    args = list(arguments)
    if args[:2] != ["-m", "pytest"]:
        return args
    selected = [arg for arg in args[2:] if "::" in arg and not arg.startswith("-")]
    explicit = any(
        arg == "-n" or arg.startswith("--numprocesses") or arg.startswith("-n") for arg in args[2:]
    )
    nested = bool(os.environ.get("PYTEST_XDIST_WORKER"))
    if nested:
        # Last option wins, including an inherited explicit automatic worker request.
        return [*args, "-n", "0"]
    if explicit:
        return [*args[:2], "--dist=loadgroup", "--max-worker-restart=0", *args[2:]]
    if "--collect-only" in args or len(selected) == 1:
        return [*args[:2], "-n", "0", *args[2:]]
    return [
        *args[:2],
        "-n",
        "auto",
        "--dist=loadgroup",
        "--max-worker-restart=0",
        *args[2:],
    ]


SCRIPT_SHEBANG = b"#!/usr/bin/env -S uv run --script"


def prepare_script_environments(
    root: Path, arguments: Sequence[str], environment: Mapping[str, str] | None = None
) -> list[str]:
    """Build each script tool's cached environment once, before parallel workers start.

    A tool that declares its own dependencies gets an environment the first time it runs.
    Parallel workers that all start such a tool at once build that environment together,
    and each can remove what another is using. Building it here, serially, leaves the
    workers nothing to build. Returns the tools prepared; a tool that cannot be prepared
    is named and left for its own test to report.

    The build lands in whichever cache `environment` selects, the caller's own by default.
    A project that gives each worker a private cache gains nothing from the supervisor's
    build, so each worker passes its own environment here before it runs tools together.
    """
    if "-n" in arguments and arguments[arguments.index("-n") + 1] == "0":
        return []
    prepared = []
    for tool in sorted((root / "bin").glob("*")):
        try:
            if not tool.is_file() or not tool.read_bytes().startswith(SCRIPT_SHEBANG):
                continue
        except OSError:
            continue
        built = subprocess.run(
            ["uv", "sync", "--script", str(tool), "--quiet"],
            capture_output=True,
            text=True,
            env=None if environment is None else dict(environment),
        )
        if built.returncode == 0:
            prepared.append(tool.name)
        else:
            print(
                f"TEST NOTE: could not prepare {tool.name}: {built.stderr.strip()}", file=sys.stderr
            )
    return prepared


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    try:
        arguments = pytest_arguments(sys.argv[1:])
        prepare_script_environments(root, arguments)
        result = run_command([sys.executable, *arguments], cwd=root)
    except (OSError, ValueError) as exc:
        print(f"TEST INCOMPLETE: supervisor could not run: {exc}", file=sys.stderr)
        return INCOMPLETE
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
