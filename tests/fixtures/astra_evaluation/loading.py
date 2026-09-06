"""Disposable loading fixture construction and scoring; no live model calls."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from exercise import ROOT, write_files

HERE = Path(__file__).resolve().parent
RESOURCE = ".claude/skills/fixture/resource.md"


def prepare(workspace: Path, pack: dict) -> None:
    workspace = workspace.resolve()
    if workspace == ROOT or ROOT in workspace.parents:
        raise ValueError("workspace must be outside this repository")
    workspace.mkdir(parents=True, exist_ok=False)
    write_files(workspace, pack["files"])
    for name, target in pack["symlinks"].items():
        link = workspace / name
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(target)


def read_tokens(workspace: Path) -> dict:
    tokens = {}
    for name, relative in (
        ("root", "AGENTS.md"),
        ("entry", ".agents/skills/fixture/SKILL.md"),
        ("resource", ".agents/skills/fixture/resource.md"),
    ):
        prefix = f"{name.title()} token: "
        values = [
            line[len(prefix) :]
            for line in (workspace / relative).read_text().splitlines()
            if line.startswith(prefix)
        ]
        if len(values) != 1:
            raise ValueError(f"{name}: expected exactly one token")
        tokens[name] = values[0]
    return tokens


def resume(workspace: Path, pack: dict) -> None:
    if read_tokens(workspace) != pack["oracle"]["initial"]:
        raise ValueError("resume requires the unchanged initial fixture")
    (workspace / RESOURCE).write_text(pack["resumed_resource"])
    (workspace / "result.json").unlink(missing_ok=True)


def check(workspace: Path, response: Path, expected: dict) -> None:
    if read_tokens(workspace) != expected:
        raise ValueError("fixture inputs do not match the selected stage")
    if json.loads(response.read_text()) != expected:
        raise ValueError("terminal response differs from oracle")
    if json.loads((workspace / "result.json").read_text()) != expected:
        raise ValueError("workspace result differs from oracle")


def qualify(pack: dict) -> None:
    with tempfile.TemporaryDirectory(prefix="astra-loading-") as temporary:
        workspace = Path(temporary) / "work"
        response = Path(temporary) / "response.json"
        prepare(workspace, pack)
        for stage in ("initial", "resumed"):
            expected = pack["oracle"][stage]
            if stage == "resumed":
                resume(workspace, pack)
                if (workspace / "result.json").exists():
                    raise ValueError("resume inherited the prior result")
            response.write_text(json.dumps(expected))
            (workspace / "result.json").write_text(json.dumps(expected))
            check(workspace, response, expected)
            wrong = dict(expected, resource="stale-token")
            response.write_text(json.dumps(wrong))
            try:
                check(workspace, response, expected)
            except ValueError:
                pass
            else:
                raise ValueError("stale token was accepted")
            response.write_text(json.dumps(expected))
            (workspace / "result.json").unlink()
            try:
                check(workspace, response, expected)
            except FileNotFoundError:
                pass
            else:
                raise ValueError("missing workspace write was accepted")
            print(f"{stage}: reference accepted; stale response and missing write rejected")
        (workspace / RESOURCE).unlink()
        try:
            read_tokens(workspace)
        except FileNotFoundError:
            pass
        else:
            raise ValueError("missing resource was accepted")
        print("missing resource rejected; LOCAL CONTROLS ONLY, live loading remains unrun")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("prepare", "resume", "check", "qualify-loading"))
    parser.add_argument("--workspace", type=Path)
    parser.add_argument("--stage", choices=("initial", "resumed"))
    parser.add_argument("--response", type=Path)
    args = parser.parse_args()
    pack = json.loads((HERE / "loading.json").read_text())
    if args.operation == "qualify-loading":
        qualify(pack)
        return
    if args.workspace is None:
        parser.error("--workspace is required")
    if args.operation == "prepare":
        prepare(args.workspace, pack)
    elif args.operation == "resume":
        resume(args.workspace, pack)
    else:
        if args.stage is None or args.response is None:
            parser.error("check requires --stage and --response")
        check(args.workspace, args.response, pack["oracle"][args.stage])
    print("FIXTURE OK; provider identity and actual permissions require separate live evidence")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        raise SystemExit(f"LOADING FIXTURE ERROR: {exc}") from exc
