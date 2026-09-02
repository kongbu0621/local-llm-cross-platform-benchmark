#!/usr/bin/env python3
"""Repository contract, semantic, dashboard, link, and public-safety validation."""

from __future__ import annotations

import json
import re
import subprocess
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


def result_files() -> list[Path]:
    results_dir = ROOT / "results"
    if not results_dir.exists():
        return []
    return sorted(results_dir.rglob("*.json"))


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
    for path in result_files():
        try:
            obj = load_json(path)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"invalid result json: {path.relative_to(ROOT)}: {exc}")
            continue
        for err in sorted(validator.iter_errors(obj), key=lambda e: list(e.path)):
            where = ".".join(str(p) for p in err.path) or "<root>"
            errors.append(f"schema error: {path.relative_to(ROOT)}:{where}: {err.message}")
    return errors


def validate_result_semantics() -> list[str]:
    """Catch semantic states that the permissive v1 JSON schema cannot express."""
    errors: list[str] = []
    seen_ids: set[str] = set()

    for path in result_files():
        obj = load_json(path)
        rel = path.relative_to(ROOT)
        exp_id = obj.get("experiment_id")
        if exp_id in seen_ids:
            errors.append(f"duplicate experiment_id: {exp_id} ({rel})")
        seen_ids.add(exp_id)

        workload = obj.get("workload", {})
        measurements = obj.get("measurements", {})
        stability = obj.get("stability", {})
        mode = obj.get("comparison_mode")

        # A warm main batch is valid evidence, but it must never masquerade as
        # the frozen strict-comparable cold-cache isolation contract.
        if workload.get("cache_state") != "cold" and mode == "strict_comparable":
            errors.append(f"non-cold result cannot be strict_comparable: {rel}")

        effective_pp = measurements.get("effective_prefill_tps_derived")
        pure_pp = measurements.get("pp_tps")
        if effective_pp is not None and pure_pp is not None:
            method = str(measurements.get("measurement_method", "")).lower()
            if "pure prefill" not in method:
                errors.append(
                    f"pp_tps present beside derived Effective Prefill without explicit pure-prefill method: {rel}"
                )

        # Failed requests may have zeros in raw vLLM output; canonical results
        # must use null for nonexistent latency/throughput measurements.
        if not stability.get("completed", False):
            for key in ("pp_tps", "ttft_ms", "decode_tps", "e2e_wall_ms"):
                if measurements.get(key) == 0:
                    errors.append(f"failed result uses zero instead of null for {key}: {rel}")

        # The repository's E2E@32K contract requires 32K output. A 32K+256
        # performance record is valid, but it must stay explicitly partial.
        if workload.get("actual_input_tokens") == 32768 and workload.get("actual_output_tokens") == 256:
            if obj.get("coverage_status") != "partial_suite_metrics" and stability.get("completed", False):
                errors.append(f"32K+256 completed result must remain partial_suite_metrics: {rel}")

    return errors


def validate_hardware_result_coherence() -> list[str]:
    errors: list[str] = []
    registry_path = ROOT / "hardware" / "registry.json"
    if not registry_path.exists():
        return ["missing hardware/registry.json"]
    registry = load_json(registry_path)
    nodes = {item["node_id"]: item for item in registry.get("nodes", [])}
    result_nodes = {
        node_id
        for path in result_files()
        for node_id in load_json(path).get("hardware", {}).get("node_ids", [])
    }
    for node_id in sorted(result_nodes):
        if node_id not in nodes:
            errors.append(f"result references unknown hardware node: {node_id}")
            continue
        if nodes[node_id].get("status") != "tested":
            errors.append(f"result-bearing node must have status=tested: {node_id}")
        profile = ROOT / nodes[node_id].get("profile", "")
        if not profile.exists():
            errors.append(f"missing hardware profile for result-bearing node: {node_id}")
        elif load_json(profile).get("status") != "tested":
            errors.append(f"result-bearing hardware profile must have status=tested: {node_id}")
    return errors


def run_repo_check(script_name: str, label: str) -> list[str]:
    script = ROOT / "scripts" / script_name
    if not script.exists():
        return [f"missing scripts/{script_name}"]
    proc = subprocess.run(
        [sys.executable, str(script), "--check"] if script_name == "render_results_dashboard.py" else [sys.executable, str(script)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode == 0:
        return []
    detail = (proc.stdout + proc.stderr).strip()
    return [f"{label} failed: {detail}"]


def validate_dashboard_sync() -> list[str]:
    return run_repo_check("render_results_dashboard.py", "README dashboard validation")


def validate_markdown_links() -> list[str]:
    return run_repo_check("check_markdown_links.py", "Markdown link validation")


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
    errors: list[str] = []
    errors += validate_json_and_yaml()
    errors += validate_result_contracts()
    errors += validate_result_semantics()
    errors += validate_hardware_result_coherence()
    errors += validate_dashboard_sync()
    errors += validate_markdown_links()
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
