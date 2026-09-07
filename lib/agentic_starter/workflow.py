"""Workflow authority, permitted deployment targets, and optional usage routing.

These are configuration decisions, not model rankings or compliance attestations.
The same pure resolver drives preflight, receipts, and dispatch validation.
"""

from __future__ import annotations

import copy
import json
import math
import shutil
import subprocess
from typing import Any

ROLES = ("planner", "reviewer", "coder", "critic")
BUILTIN_TARGETS = {
    "astra": ("codex", "gpt-6-astra"),
    "sol": ("codex", "gpt-5.6-sol"),
    "terra": ("codex", "gpt-5.6-terra"),
    "luna": ("codex", "gpt-5.6-luna"),
    "fable": ("claude", "fable"),
    "opus": ("claude", "opus"),
}

DEFAULT_WORKFLOW = {
    "mode": "auto",
    "primary_models": {"claude": "fable", "codex": "astra"},
    "eligible_primary_models": ["astra", "fable"],
    "review_preference": "cross-vendor",
    "adviser_models": {
        "claude": {"reviewer": ["astra"], "critic": ["astra"]},
        "codex": {"reviewer": ["fable"], "critic": ["fable"]},
    },
    "allowed_harnesses": ["claude", "codex"],
    "targets": {},
}


class WorkflowError(ValueError):
    """A route cannot be established from the declared authority."""


def validate(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != set(DEFAULT_WORKFLOW):
        raise WorkflowError("workflow has unknown or missing fields")
    if value["mode"] not in {"auto", "primary", "delegated"}:
        raise WorkflowError("workflow.mode must be auto, primary, or delegated")
    if value["review_preference"] not in {"cross-vendor", "same-harness"}:
        raise WorkflowError("invalid workflow review_preference")
    if (
        not isinstance(value["primary_models"], dict)
        or set(value["primary_models"]) != {"claude", "codex"}
        or not all(isinstance(v, str) and v for v in value["primary_models"].values())
    ):
        raise WorkflowError("workflow.primary_models requires explicit claude and codex pins")
    for field in ("eligible_primary_models", "allowed_harnesses"):
        items = value[field]
        if not isinstance(items, list) or not all(isinstance(v, str) and v for v in items):
            raise WorkflowError(f"workflow.{field} must be a string list")
        if len(items) != len(set(items)):
            raise WorkflowError(f"workflow.{field} has duplicates")
    if not set(value["allowed_harnesses"]) <= {"claude", "codex"}:
        raise WorkflowError("workflow allows an unsupported harness")
    advisers = value["adviser_models"]
    if not isinstance(advisers, dict) or set(advisers) != {"claude", "codex"}:
        raise WorkflowError("adviser_models requires both invoking harnesses")
    for pins in advisers.values():
        if not isinstance(pins, dict) or set(pins) != {"reviewer", "critic"}:
            raise WorkflowError("adviser_models requires reviewer and critic")
        for choices in pins.values():
            if (
                not isinstance(choices, list)
                or not all(isinstance(v, str) and v for v in choices)
                or len(set(choices)) != len(choices)
            ):
                raise WorkflowError("adviser choices must be an ordered unique selector list")
    if not isinstance(value["targets"], dict):
        raise WorkflowError("workflow.targets must be a mapping")
    for name, target in value["targets"].items():
        if not isinstance(name, str) or not name or not isinstance(target, dict):
            raise WorkflowError("invalid workflow target")
        fields = {
            "harness",
            "model",
            "provider",
            "backend",
            "auth",
            "efforts",
            "usage_windows",
            "terms",
            "credential_env",
            "backend_env",
        }
        if set(target) != fields:
            raise WorkflowError(f"target {name} has unknown or missing fields")
        if target["harness"] not in {"claude", "codex"} or target["auth"] not in {
            "subscription",
            "configured",
        }:
            raise WorkflowError(f"invalid harness/auth for {name}")
        for field in ("model", "provider", "backend"):
            if not isinstance(target[field], str) or not target[field].strip():
                raise WorkflowError(f"target {name}.{field} must be nonempty")
        if not isinstance(target["terms"], str):
            raise WorkflowError("target terms must name the operator's handling authority")
        if target["auth"] == "configured" and not target["terms"].strip():
            raise WorkflowError("configured backend requires declared handling authority")
        if not isinstance(target["backend_env"], dict) or not all(
            isinstance(k, str) and k and isinstance(v, str) and v
            for k, v in target["backend_env"].items()
        ):
            raise WorkflowError("backend_env must declare exact non-secret routing values")
        if target["backend"] != "direct" and not target["backend_env"]:
            raise WorkflowError("managed backend requires explicit routing environment")
        if any(k in target["backend_env"] for k in target["credential_env"]):
            raise WorkflowError(
                "credentials must be environment references, never routing literals"
            )
        for field in ("efforts", "usage_windows", "credential_env"):
            if not isinstance(target[field], list) or not all(
                isinstance(v, str) and v for v in target[field]
            ):
                raise WorkflowError(f"target {name}.{field} must be a string list")
    identities = [t["model"] for t in value["targets"].values()]
    if len(identities) != len(set(identities)):
        raise WorkflowError("custom target identities must be unambiguous")
    for name, deployment in value["targets"].items():
        if any(
            deployment["model"] == model and name != selector
            for selector, (_, model) in BUILTIN_TARGETS.items()
        ):
            raise WorkflowError("overriding a built-in identity requires its canonical selector")
    return value


def target(name: str, settings: dict[str, Any]) -> dict[str, Any]:
    custom = settings["targets"].get(name)
    if custom is not None:
        return {"selector": name, **copy.deepcopy(custom)}
    if name not in BUILTIN_TARGETS:
        raise WorkflowError(f"unknown deployment target {name}; configure its exact identity")
    harness, model = BUILTIN_TARGETS[name]
    return {
        "selector": name,
        "harness": harness,
        "model": model,
        "provider": "anthropic" if harness == "claude" else "openai",
        "backend": "direct",
        "auth": "subscription",
        "efforts": ["low", "medium", "high", "xhigh", "max"],
        "usage_windows": [],
        "terms": "operator-configured subscription access",
        "credential_env": [],
        "backend_env": {},
    }


def settings(document: dict[str, Any]) -> dict[str, Any]:
    return validate(document.get("workflow", copy.deepcopy(DEFAULT_WORKFLOW)))


def adviser_choices(config: dict[str, Any], harness: str, primary: str, role: str) -> list[str]:
    """Configured ordered destinations, followed by the fresh primary instance."""
    choices = []
    if config["review_preference"] == "cross-vendor":
        for name in config["adviser_models"][harness][role]:
            destination = target(name, config)
            if destination["harness"] in config["allowed_harnesses"] and name not in choices:
                choices.append(name)
    if primary not in choices:
        choices.append(primary)
    return choices


def resolve(
    document: dict[str, Any], harness: str, primary_model: str | None = None
) -> dict[str, Any]:
    config = settings(document)
    primary = primary_model or config["primary_models"][harness]
    eligible = primary in config["eligible_primary_models"]
    mode = config["mode"]
    if mode == "auto":
        mode = "primary" if eligible else "delegated"
    if mode == "primary" and not eligible:
        raise WorkflowError("primary mode requires a configured eligible primary model")
    if harness not in config["allowed_harnesses"]:
        raise WorkflowError("invoking harness is not permitted")
    main = target(primary, config)
    if main["harness"] != harness:
        raise WorkflowError("primary pin does not match the invoking harness")
    pins = document["role_models"]
    roles = {}
    reasons = []
    for role in ROLES:
        if mode == "primary" and role in {"planner", "coder"}:
            roles[role] = {"model": primary, "effort": None, "execution": "inline"}
            continue
        pin = (
            pins.get(harness, {}).get(role)
            or pins.get("default", {}).get(role)
            or {"model": "default"}
        )
        name = pin["model"]
        if mode == "delegated" and name == "default":
            roles[role] = {"model": "default", "effort": None, "execution": "native"}
            continue
        if mode == "primary":
            name = adviser_choices(config, harness, primary, role)[0]
        if name in {"default", "claude", "codex"}:
            name = primary if name == "default" else config["primary_models"][name]
        destination = target(name, config)
        if destination["harness"] not in config["allowed_harnesses"]:
            raise WorkflowError(f"{role} target is forbidden; select permitted pins")
        roles[role] = {
            "model": name,
            "effort": pin.get("effort"),
            "execution": "independent",
        }
    return {
        "mode": mode,
        "harness": harness,
        "primary_model": primary,
        "identity_basis": "explicit-configuration",
        "reported_model": None,
        "roles": roles,
        "fallbacks": reasons,
        "usage": {"state": "not-checked"},
    }


def usage_snapshot() -> dict[str, Any] | None:
    program = shutil.which("llm-usage")
    if program is None:
        return None
    try:
        result = subprocess.run(
            [program, "--json"], capture_output=True, text=True, timeout=60, check=False
        )
        value = json.loads(result.stdout)
    except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
        raise WorkflowError(f"llm-usage query failed: {type(exc).__name__}") from exc
    # The CLI returns 1 for a partial provider failure. Relevant provider
    # blocks are checked individually; an unrelated account is not a dependency.
    if result.returncode not in {0, 1} or not isinstance(value, dict):
        raise WorkflowError("llm-usage failed or returned malformed data")
    return value


def usage_windows(
    snapshot: dict[str, Any], deployment: dict[str, Any]
) -> list[dict[str, Any]] | None:
    if deployment["auth"] != "subscription" or deployment["backend"] != "direct":
        return None
    block = snapshot.get(deployment["provider"])
    if not isinstance(block, dict) or block.get("ok") is not True:
        raise WorkflowError(f"llm-usage failed for {deployment['provider']}")
    age = block.get("cache_age_seconds")
    if age is not None and (
        not isinstance(age, (int, float))
        or isinstance(age, bool)
        or not math.isfinite(age)
        or age > 900
    ):
        raise WorkflowError("llm-usage snapshot is stale or has invalid cache age")
    windows = block.get("windows")
    if not isinstance(windows, dict) or not windows:
        raise WorkflowError("llm-usage has no applicable window data")
    windows = dict(windows)
    selectors = deployment["usage_windows"]
    extra = block.get("additional_rate_limits", [])
    if not isinstance(extra, list):
        raise WorkflowError("invalid additional usage limits")
    for group in extra:
        if not isinstance(group, dict) or not isinstance(group.get("windows"), dict):
            raise WorkflowError("malformed additional usage group")
        name = group.get("metered_feature") or group.get("name")
        if not isinstance(name, str) or not name:
            raise WorkflowError("additional usage group has no identity")
        matches = name in {deployment["selector"], deployment["model"]}
        if not selectors and not matches:
            raise WorkflowError(f"ambiguous additional usage group {name}; configure usage_windows")
        for key, window in group["windows"].items():
            combined = name + "/" + key
            if matches or combined in selectors:
                windows[combined] = window
    selected = []
    for key, window in windows.items():
        if not isinstance(window, dict):
            raise WorkflowError("malformed usage window")
        # Explicit model mappings never discard shared account limits.
        shared = key in {"five_hour", "seven_day", "primary_window", "secondary_window"}
        if selectors and key not in selectors and not shared:
            continue
        if not selectors and key.startswith("seven_day_"):
            scope = key.removeprefix("seven_day_")
            if scope not in {"opus", "fable", "sonnet", "oauth_apps", "cowork"}:
                raise WorkflowError(f"unknown scoped usage window {key}; configure usage_windows")
            if scope != deployment["selector"]:
                continue
        active = window.get("is_active")
        if active is not None and not isinstance(active, bool):
            raise WorkflowError("invalid usage window activity")
        if active is False:
            continue
        percent, duration = window.get("utilization"), window.get("window_seconds")
        if (
            isinstance(percent, bool)
            or not isinstance(percent, (float, int))
            or not math.isfinite(percent)
            or percent < 0
            or isinstance(duration, bool)
            or not isinstance(duration, (float, int))
            or not math.isfinite(duration)
            or duration <= 0
        ):
            raise WorkflowError(f"invalid usage values for {key}")
        selected.append(
            {
                "window": key,
                "utilization": percent,
                "window_seconds": duration,
                "reset": window.get("resets_at", window.get("reset_at")),
            }
        )
    if not selected or (selectors and set(selectors) - set(windows)):
        raise WorkflowError("usage window mapping is missing or ambiguous")
    return selected


def apply_usage(
    resolution: dict[str, Any], config: dict[str, Any], snapshot: dict[str, Any] | None
) -> dict[str, Any]:
    result = copy.deepcopy(resolution)
    if snapshot is None:
        result["usage"] = {"state": "unavailable"}
        return result
    primary = result["primary_model"]
    windows = usage_windows(snapshot, target(primary, config))
    result["usage"] = {
        "state": "measured" if windows is not None else "not-covered",
        "primary": windows,
    }
    for window in windows or []:
        if window["utilization"] >= 95:
            raise WorkflowError(
                f"kickoff refused: primary {primary} {window['window']} "
                f"at {window['utilization']}% (limit >=95%); reset {window['reset']}"
            )
    secondary = {}
    for role in ("reviewer", "critic"):
        name = result["roles"][role]["model"]
        if name == "default":
            name = primary
        values = usage_windows(snapshot, target(name, config))
        secondary[role] = values
        if any(w["window_seconds"] == 604800 and w["utilization"] > 95 for w in values or []):
            result["roles"][role]["model"] = primary
            result["roles"][role]["effort"] = None
            result["fallbacks"].append(f"{role}: {name} weekly usage >95%; independent {primary}")
    result["usage"]["secondary"] = secondary
    return result


def child_environment(
    environment: dict[str, str], cli: str, model: str | None, config: dict[str, Any]
) -> dict[str, str]:
    environment = environment.copy()
    keys = (
        ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "ANTHROPIC_API_KEY")
        if cli == "claude"
        else ("OPENAI_API_KEY", "CODEX_API_KEY")
    )
    matches = [
        t
        for name, t in config["targets"].items()
        if t["harness"] == cli and model in {name, t["model"]}
    ]
    deployment = matches[0] if matches else None
    routing = {
        "CLAUDE_CODE_USE_BEDROCK",
        "CLAUDE_CODE_USE_VERTEX",
        "CLAUDE_CODE_USE_FOUNDRY",
        "ANTHROPIC_BASE_URL",
        "OPENAI_BASE_URL",
    }
    credentials = {
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "CODEX_API_KEY",
        "ANTHROPIC_AUTH_TOKEN",
        "CLAUDE_CODE_OAUTH_TOKEN",
    }
    saved = environment.copy()
    for key in set(keys) | routing | credentials:
        environment.pop(key, None)
    if deployment and deployment["auth"] == "configured":
        for key in deployment["credential_env"]:
            if not saved.get(key):
                raise WorkflowError(f"configured credential environment is missing: {key}")
            environment[key] = saved[key]
        environment.update(deployment["backend_env"])
    elif cli == "claude" and saved.get("CLAUDE_CODE_OAUTH_TOKEN"):
        environment["CLAUDE_CODE_OAUTH_TOKEN"] = saved["CLAUDE_CODE_OAUTH_TOKEN"]
    if cli == "claude":
        # Every generated Claude invocation is --print. Native background work
        # would be cleaned up when that CLI exits instead of reawakening it.
        environment["CLAUDE_CODE_DISABLE_BACKGROUND_TASKS"] = "1"
    environment["KICKOFF_DELEGATION_DEPTH"] = "1"
    return environment
