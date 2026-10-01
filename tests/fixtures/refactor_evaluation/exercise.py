"""Prepare, check and locally qualify the refactoring evaluation pack; never invokes a model."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
NARRATION = ("# add the item to the list of items", "# loop over the items and add up the totals")


def write_files(destination: Path, files: dict[str, str]) -> None:
    for name, body in files.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body)


def git(destination: Path, *arguments: str) -> None:
    identity = ("-c", "user.name=evaluation", "-c", "user.email=evaluation@example.invalid")
    subprocess.run(
        ["git", *identity, *arguments], cwd=destination, check=True, capture_output=True, text=True
    )


def prepare(destination: Path, pack: dict, skill: Path | None = None) -> None:
    destination = destination.resolve()
    if destination == ROOT or ROOT in destination.parents:
        raise ValueError("workspace must be outside this repository")
    destination.mkdir(parents=True, exist_ok=False)
    write_files(destination, pack["files"])
    for name in pack["executable"]:
        (destination / name).chmod(0o755)
    (destination / "AGENTS.md").symlink_to("CLAUDE.md")
    if skill is not None:
        shutil.copytree(skill, destination / ".claude" / "skills" / skill.name)
        mirror = destination / ".agents" / "skills"
        mirror.mkdir(parents=True)
        (mirror / skill.name).symlink_to(f"../../.claude/skills/{skill.name}")
    git(destination, "init", "--quiet", "--initial-branch=master")
    git(destination, "add", "--all")
    git(destination, "commit", "--quiet", "--message", "Initial package")


def run(destination: Path, *command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command, cwd=destination, capture_output=True, text=True, timeout=120, check=False
    )


def probe(destination: Path, pack: dict) -> dict:
    # The probe stays in evaluator memory, never copied into the model's workspace.
    result = run(destination, sys.executable, "-B", "-c", pack["probe"])
    if result.returncode:
        raise ValueError(f"probe did not run: {result.stderr.strip()[-400:]}")
    return json.loads(result.stdout)


def definitions(destination: Path) -> dict[str, str]:
    found = {}
    for source in sorted((destination / "shop").rglob("*.py")):
        for node in ast.walk(ast.parse(source.read_text())):
            if isinstance(node, ast.FunctionDef | ast.ClassDef):
                found.setdefault(node.name, ast.dump(node))
    return found


def depth(node: ast.AST) -> int:
    nested = max((depth(child) for child in ast.iter_child_nodes(node)), default=0)
    return nested + isinstance(node, ast.If)


def facts(destination: Path) -> dict:
    sources = {
        path.relative_to(destination).as_posix(): path.read_text()
        for path in sorted((destination / "shop").rglob("*.py"))
    }
    text = "\n".join(sources.values())
    trees = [ast.parse(body) for body in sources.values()]
    functions = {
        node.name: node
        for tree in trees
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
    }
    summary = functions.get("summary")
    in_loop = summary is not None and any(
        isinstance(call, ast.Call) and getattr(call.func, "attr", "") == "subtotal"
        for loop in ast.walk(summary)
        if isinstance(loop, ast.For)
        for call in ast.walk(loop)
    )
    discount = functions.get("_discount_for")
    return {
        "reuse: inline rounding copies in pricing": sources.get("shop/pricing.py", "").count(
            "quantize("
        ),
        "complexity: if-depth of _discount_for": depth(discount) if discount else "absent",
        "dead code: _legacy_total present": "_legacy_total" in functions,
        "special case: GIFT literals in cart": sources.get("shop/cart.py", "").count('"GIFT"'),
        "pass-through: helpers module present": "shop/helpers.py" in sources,
        "residue: _debug_log present": "_debug_log" in text,
        "residue: narrating comments": sum(text.count(line) for line in NARRATION),
        "waste: subtotal recomputed in loop": in_loop,
        "convention: lowercase constant present": "_default_currency" in text,
    }


def check(destination: Path, pack: dict) -> dict:
    with tempfile.TemporaryDirectory(prefix="refactor-original-") as temporary:
        original = Path(temporary) / "work"
        write_files(original, pack["files"])
        expected = probe(original, pack)
        before = definitions(original)
    tests = run(destination, "./bin/test")
    try:
        observed = probe(destination, pack)
        after = definitions(destination)
        observations = facts(destination)
    except (ValueError, SyntaxError) as error:
        return {"tests_pass": tests.returncode == 0, "unreadable": str(error)}
    shipped = destination / "tests" / "test_shop.py"
    return {
        "tests_pass": tests.returncode == 0,
        "tests_file_unchanged": shipped.exists()
        and shipped.read_text() == pack["files"]["tests/test_shop.py"],
        "probe_differences": sorted(k for k in expected if observed.get(k) != expected[k]),
        "decoys_changed": [name for name in pack["decoys"] if after.get(name) != before[name]],
        "facts": observations,
    }


def qualify(pack: dict) -> None:
    with tempfile.TemporaryDirectory(prefix="refactor-fixture-") as temporary:
        workspace = Path(temporary) / "work"
        prepare(workspace, pack)
        baseline = check(workspace, pack)
        clean = baseline["tests_pass"] and not baseline["probe_differences"]
        if not clean or baseline["decoys_changed"] or not baseline["tests_file_unchanged"]:
            raise ValueError(f"original package is not a clean baseline: {baseline}")
        seeded = baseline["facts"]
        write_files(workspace, pack["reference"])
        reference = check(workspace, pack)
        if not reference["tests_pass"] or reference["probe_differences"]:
            raise ValueError(f"reference refactoring rejected: {reference}")
        if reference["decoys_changed"] or reference["facts"] == seeded:
            raise ValueError(f"reference left the seeds or touched a decoy: {reference}")
        write_files(workspace, pack["wrong"])
        for name in pack["wrong_removes"]:
            (workspace / name).unlink()
        wrong = check(workspace, pack)
        if not wrong["tests_pass"]:
            raise ValueError("the wrong refactoring must pass the shipped tests to be a trap")
        if wrong["probe_differences"] != pack["wrong_differences"]:
            raise ValueError(f"wrong refactoring differences moved: {wrong['probe_differences']}")
        if not wrong["decoys_changed"]:
            raise ValueError("the wrong refactoring must change a decoy")
        # A package that cannot be imported is a measurement failure, not a detection.
        write_files(workspace, {"shop/__init__.py": "raise RuntimeError('unrelated failure')\n"})
        broken = check(workspace, pack)
        differing = len(broken["probe_differences"])
        if broken["tests_pass"] or differing <= len(wrong["probe_differences"]):
            raise ValueError(f"an unimportable package was not reported as such: {broken}")
    print(
        "original clean; reference accepted with seeds addressed and decoys intact; "
        f"wrong refactoring passes shipped tests and fails {len(pack['wrong_differences'])} probes"
    )
    print("LOCAL FIXTURE QUALIFICATION ONLY; no model result")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("prepare", "check", "qualify", "digest"))
    parser.add_argument("--workspace", type=Path)
    parser.add_argument("--skill", type=Path, help="skill directory to install in the workspace")
    args = parser.parse_args()
    pack = json.loads((HERE / "pack.json").read_text())
    if args.operation == "digest":
        for source in sorted(HERE.iterdir()):
            if source.is_file():
                print(hashlib.sha256(source.read_bytes()).hexdigest(), source.name)
        return 0
    if args.operation == "qualify":
        qualify(pack)
        return 0
    if args.workspace is None:
        parser.error("prepare and check require --workspace")
    if args.operation == "prepare":
        prepare(args.workspace, pack, args.skill.resolve() if args.skill else None)
        print(f"Prepared public inputs only: {args.workspace.resolve()}")
        return 0
    print(json.dumps(check(args.workspace.resolve(), pack), indent=1))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"FIXTURE ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
