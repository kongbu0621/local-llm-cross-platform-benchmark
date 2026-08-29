#!/usr/bin/env python3
"""Lightweight repository contract validation for CI."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_SUFFIXES = {
    ".safetensors",
    ".gguf",
    ".ckpt",
    ".pth",
    ".pt",
    ".engine",
    ".plan",
}

SECRET_PATTERNS = [
    re.compile(r"hf_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_json_and_yaml() -> list[str]:
    errors: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        try:
            if path.suffix == ".json":
                load_json(path)
            elif path.suffix in {".yaml", ".yml"}:
                with path.open("r", encoding="utf-8") as f:
                    yaml.safe_load(f)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"parse error: {path.relative_to(ROOT)}: {exc}")
    return errors


def validate_result_contracts() -> list[str]:
    errors: list[str] = []
    schema_path = ROOT / "schemas" / "benchmark-result.schema.json"
    if not schema_path.exists():
        return ["missing schemas/benchmark-result.schema.json"]
    schema = load_json(schema_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    results_dir = ROOT / "results"
    if not results_dir.exists():
        return errors
    for path in results_dir.rglob("*.json"):
        try:
            obj = load_json(path)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"invalid result json: {path.relative_to(ROOT)}: {exc}")
            continue
        for err in sorted(validator.iter_errors(obj), key=lambda e: list(e.path)):
            where = ".".join(str(p) for p in err.path) or "<root>"
            errors.append(f"schema error: {path.relative_to(ROOT)}:{where}: {err.message}")
    return errors


def validate_public_safety() -> list[str]:
    errors: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        rel = path.relative_to(ROOT)
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append(f"forbidden model artifact tracked: {rel}")
            continue
        if path.stat().st_size > 10 * 1024 * 1024:
            errors.append(f"unexpected >10MiB tracked file: {rel}")
            continue
        if path.suffix.lower() in {".md", ".txt", ".json", ".yaml", ".yml", ".py", ".sh"}:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for pattern in SECRET_PATTERNS:
                if pattern.search(text):
                    errors.append(f"possible secret in tracked text: {rel} ({pattern.pattern})")
    return errors


def validate_suite_freeze() -> list[str]:
    errors: list[str] = []
    matrix = ROOT / "suites" / "qwen38-27b" / "v1.0" / "test-matrix.yaml"
    if not matrix.exists():
        return ["missing qwen38-27b v1.0 test matrix"]
    data = yaml.safe_load(matrix.read_text(encoding="utf-8"))
    expected = {32768, 131072, 262144, 393216, 524288, 786432, 1048576}
    got = set(data["context_tokens"]["core"]) | set(data["context_tokens"]["deep_dive"])
    if got != expected:
        errors.append(f"unexpected qwen38 context set: {sorted(got)}")
    if len(data.get("models", [])) != 3:
        errors.append("qwen38 v1.0 must contain exactly three initial model arms")
    return errors


def main() -> int:
    errors = []
    errors += validate_json_and_yaml()
    errors += validate_result_contracts()
    errors += validate_public_safety()
    errors += validate_suite_freeze()
    if errors:
        print("VALIDATION FAILED")
        for item in errors:
            print(f"- {item}")
        return 1
    print("VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
