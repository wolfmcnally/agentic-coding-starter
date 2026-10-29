"""Explicit target-only retirement and transfer classification; no live cutover."""

from __future__ import annotations

import ast
import hashlib
import json
import re
from pathlib import Path
from typing import Any

RETIRED_TOOLS = (
    "renumber-phases",
    "log-append",
    "log-relocate",
    "check-log",
    "check-log-prefix",
    "check-log-monotonic",
)
SHARED = {
    "bin/normalize-final-newline": "Execution/index normalization; remove flat-log repair.",
    "lib/agentic_starter/log_blocks.py": "Historical body and terminal Lessons parsing.",
    "bin/kickoff-evidence": "Advice/acceptance: new-schema semantics still need qualification.",
    "bin/check": "Aggregate gate: replace removed executable and log callers.",
    ".githooks/pre-commit": "Preserve actual-index immutable-record validation.",
    "bin/kickoff-command-zero": "Command admission: use structured-record validation.",
    "bin/check-catalogs": "Catalogs/links: new phase semantics need live-cutover qualification.",
}
HISTORY = {"log", "docs", "reports", "lessons", "lessons-archived", "user-actions-archived"}
INTENTIONAL = {
    "lib/agentic_starter/multioperator_transition.py",
    "lib/agentic_starter/multioperator.py",
    "tests/test_multioperator.py",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def inventory(root: Path) -> dict[str, Any]:
    obsolete = {}
    for name in RETIRED_TOOLS:
        path = root / "bin" / name
        if path.exists():
            if path.is_symlink() or not path.is_file():
                raise ValueError("retirement target is not a regular file: " + str(path))
            obsolete["bin/" + name] = sha(path.read_bytes())
    return {"obsolete": obsolete, "shared": SHARED}


def token_pattern(name: str) -> str:
    return r"(?<![A-Za-z0-9_-])" + re.escape(name) + r"(?![A-Za-z0-9_-])"


def active_files(root: Path):
    for path in root.rglob("*"):
        if (
            not path.is_file()
            or path.is_symlink()
            or path.relative_to(root).parts[0]
            in HISTORY | {".git", ".collaboration-views", "collaboration"}
        ):
            continue
        relative = path.relative_to(root)
        if relative.as_posix() in {".claude/CLAUDE.md", "CLAUDE.local.md"}:
            continue  # Unrelated local instructions are outside the conversion.
        if (
            relative.parts[0]
            not in {"bin", "policies", "briefs", "plan", "tests", ".claude", ".githooks", "lib"}
            and len(relative.parts) != 1
        ):
            continue
        if relative.parts[0] == "lib" and relative.parts[:2] != ("lib", "agentic_starter"):
            continue
        if path.suffix in {"", ".py", ".md", ".yaml", ".yml", ".sh", ".toml"}:
            yield path


def audit(root: Path) -> dict[str, Any]:
    present = [name for name in RETIRED_TOOLS if (root / "bin" / name).exists()]
    dangling = []
    for path in active_files(root):
        relative = path.relative_to(root).as_posix()
        if relative in INTENTIONAL:
            continue  # Explicit retirement selectors/negative-test oracles are not callers.
        try:
            text = path.read_text()
        except UnicodeError:
            continue
        for name in RETIRED_TOOLS:
            if re.search(token_pattern(name), text):
                dangling.append({"path": relative, "obsolete": name})
    if present or dangling:
        raise ValueError(
            "obsolete target tools/references remain: "
            + json.dumps({"present": present, "dangling": dangling})
        )
    return {
        "obsolete_absent": True,
        "retired_reference_tokens_absent": True,
        "historical_text_exempt": sorted(HISTORY),
        "intentional_selectors": sorted(INTENTIONAL),
    }


def remove_function(text: str, name: str) -> str:
    lines = text.splitlines(keepends=True)
    found = [
        node
        for node in ast.parse(text).body
        if isinstance(node, ast.FunctionDef) and node.name == name
    ]
    if not found:
        return text
    if len(found) != 1:
        raise ValueError("ambiguous target-only test cleanup")
    node = found[0]
    start = min([node.lineno, *[decorator.lineno for decorator in node.decorator_list]]) - 1
    return "".join(lines[:start] + lines[node.end_lineno :])


def promote_constitution(root: Path) -> dict[str, Any]:
    """Convert only the repository constitution; preserve other instruction files."""
    old, primary = root / "CLAUDE.md", root / "AGENTS.md"
    if not old.is_file() or old.is_symlink():
        raise ValueError("expected regular pre-migration CLAUDE constitution")
    original = old.read_bytes()
    if primary.is_symlink():
        if primary.resolve() != old.resolve():
            raise ValueError("constitutional symlink does not name the original constitution")
    elif primary.exists() and (not primary.is_file() or primary.read_bytes() != original):
        raise ValueError("conflicting AGENTS constitution; owner must reconcile")
    if primary.exists() or primary.is_symlink():
        primary.unlink()
    primary.write_bytes(original)
    old.unlink()
    changes = []
    for path in active_files(root):
        relative = path.relative_to(root).as_posix()
        if relative in INTENTIONAL:
            continue
        text = path.read_text()
        before = text
        # Only exact top-level references; vendor/global/local instruction names stay literal.
        text = re.sub(r"(?<![A-Za-z0-9_./-])CLAUDE\.md(?![A-Za-z0-9_-])", "AGENTS.md", text)
        if relative == "tests/test_mirror_parity.py":
            alias = '    (tmp_path / "AGENTS.md").symlink_to("AGENTS.md")\n'
            if alias not in text:
                raise ValueError("recipient instruction-parity fixture differs; adapt its recipe")
            text = text.replace(alias, "")
        if relative == "AGENTS.md":
            text = text.replace(
                "`AGENTS.md` points here.", "`AGENTS.md` is the regular primary constitution."
            )
        if relative == "bin/check-harness-parity":
            lines = text.splitlines(keepends=True)
            node = next(
                n
                for n in ast.parse(text).body
                if isinstance(n, ast.FunctionDef) and n.name == "check_instructions"
            )
            replacement = [
                "def check_instructions() -> None:\n",
                '    primary = ROOT / "AGENTS.md"\n',
                "    if primary.is_symlink() or not primary.is_file():\n",
                '        report("instructions", "AGENTS.md", "must be a regular primary file")\n',
                '    old = ROOT / "CLAUDE.md"\n',
                "    if old.exists() or old.is_symlink():\n",
                '        report("instructions", "CLAUDE.md", "legacy constitution remains")\n',
            ]
            text = "".join(lines[: node.lineno - 1] + replacement + lines[node.end_lineno :])
        if text != before:
            path.write_text(text)
            changes.append(relative)
    return {
        "original_sha256": sha(original),
        "primary_sha256": sha(primary.read_bytes()),
        "rewritten_paths": changes,
    }


def retire(root: Path, approved: dict[str, str], package: Path) -> dict[str, Any]:
    observed = inventory(root)
    if observed["obsolete"] != approved:
        raise ValueError(
            "retirement inventory/preimage mismatch; obtain the recipient-owned exact recipe"
        )
    changes = []
    for name in RETIRED_TOOLS:
        path = root / "bin" / name
        if path.exists():
            path.unlink()
            changes.append(
                {"path": "bin/" + name, "action": "retired", "pre_sha256": approved["bin/" + name]}
            )
    old_test = root / "tests/test_renumber_phases.py"
    if old_test.exists():
        changes.append(
            {
                "path": "tests/test_renumber_phases.py",
                "action": "retired",
                "pre_sha256": sha(old_test.read_bytes()),
            }
        )
        old_test.unlink()
    # Install only this qualified capability, never donor judgments or project runtime values.
    for relative in (
        "bin/multioperator",
        "lib/agentic_starter/multioperator.py",
        "lib/agentic_starter/multioperator_transition.py",
    ):
        source, target = package / relative, root / relative
        if target.exists() and target.read_bytes() != source.read_bytes():
            raise ValueError("recipient-owned migration tool differs: " + relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
        target.chmod(source.stat().st_mode & 0o777)
    replacements = {
        "bin/kickoff-command-zero": [
            (
                'run_checked(["./bin/check-log"], root, "log policy")',
                'run_checked(["./bin/multioperator", "validate", "--root", "."], '
                'root, "record policy")',
            )
        ],
        ".githooks/pre-commit": [
            ("./bin/check-log --staged", "./bin/multioperator validate --root . --staged")
        ],
        "bin/check": [
            (
                "test-governance check-log check-log-prefix "
                "check-log-monotonic kickoff-command-zero",
                "test-governance multioperator kickoff-command-zero",
            ),
            ("log-append log-relocate normalize-final-newline", "normalize-final-newline"),
            (
                "run_gate policy-log ./bin/check-log",
                "run_gate policy-log ./bin/multioperator validate --root .",
            ),
        ],
        "bin/normalize-final-newline": [('Path("LOG.md"), ', "")],
    }
    for relative, rules in replacements.items():
        path = root / relative
        if not path.exists():
            continue
        text = path.read_text()
        for before, after in rules:
            if before not in text:
                raise ValueError(
                    "shared caller differs; adapt its recipe before rehearsal: " + relative
                )
            text = text.replace(before, after)
        path.write_text(text)
    # Remove obsolete Python-tool operands from lint/format and corresponding fixture argv.
    operands = "|".join(map(re.escape, RETIRED_TOOLS))
    for path in active_files(root):
        relative = path.relative_to(root).as_posix()
        if relative in INTENTIONAL:
            continue
        try:
            text = path.read_text()
        except UnicodeError:
            continue
        before = text
        if relative == "bin/README.md":
            text = "".join(
                line
                for line in text.splitlines(keepends=True)
                if not any(re.search(token_pattern(name), line) for name in RETIRED_TOOLS)
            )
            text += (
                "\n- `multioperator` — structured records and isolated migration rehearsal; "
                "current-format semantics require separate qualification.\n"
            )
        elif relative == "tests/proof-estate.yaml":
            blocks = re.split(r"(?m)(?=^- id: )", text)
            text = "".join(
                block for block in blocks if "tests/test_renumber_phases.py" not in block
            )
        text = re.sub(r"\.\./bin/(?:" + operands + r")\s*", "", text)
        # Path redirection is mechanical, not a claim that mixed workflow semantics are qualified.
        for name in sorted(RETIRED_TOOLS, key=len, reverse=True):
            text = re.sub(token_pattern(name), "multioperator", text)
        text = text.replace("tests/test_renumber_phases.py", "tests/test_multioperator.py")
        if text != before:
            path.write_text(text)
            changes.append(
                {
                    "path": relative,
                    "action": "caller/reference-cleanup",
                    "pre_sha256": sha(before.encode()),
                    "post_sha256": sha(text.encode()),
                }
            )
    # The old test is one mixed scenario; preserve its still-shared normalization boundary.
    normalizer = root / "tests/test_log_control_plane.py"
    if normalizer.exists():
        normalizer.write_text(NORMALIZER_TEST)
        changes.append(
            {
                "path": "tests/test_log_control_plane.py",
                "action": "rewrite-shared-normalization-proof",
            }
        )
    target_test = root / "tests/test_multioperator.py"
    source_test = package / "tests/test_multioperator.py"
    target_test.parent.mkdir(parents=True, exist_ok=True)
    target_test.write_text(
        remove_function(
            source_test.read_text(), "test_actual_starter_rehearsal_preserves_source_and_history"
        )
    )
    constitution = promote_constitution(root)
    result = audit(root)
    return {
        "inventory": observed,
        "constitution": constitution,
        "changes": changes,
        "audit": result,
        "shared_semantic_adoption_pending": [
            "candidate/close/phase capture and current actor adapters",
            "complete new-schema catalog/skill semantics",
            "recipient proof retirement/admission and full gate",
        ],
        "source_proof_judgments_transferred": False,
    }


NORMALIZER_TEST = """from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def test_shared_normalization_survives_record_migration(tmp_path):
    root = tmp_path / "repo"
    (root / "plan").mkdir(parents=True)
    (root / "plan/INDEX.md").write_text("index\\n\\n")
    (root / "candidate-partition.yaml").write_text(
        "schema: agentic.candidate-partition.v1\\nactive:\\n"
        "  - {quote}/candidate-partition.yaml{quote}\\n"
        "bookkeeping:\\n  - {quote}/plan/INDEX.md{quote}\\n")
    subprocess.run(["git", "init", "-b", "master", str(root)], check=True, capture_output=True)
    normalizer = ROOT / "bin/normalize-final-newline"
    passed = subprocess.run(
        [str(normalizer), "--root", str(root), "--path", "plan/INDEX.md"], capture_output=True)
    assert passed.returncode == 0 and (root / "plan/INDEX.md").read_bytes() == b"index\\n"
    denied = subprocess.run(
        [str(normalizer), "--root", str(root), "--path", "LOG.md"], capture_output=True)
    assert denied.returncode == 2
""".replace("{quote}", chr(92) + chr(34))
