#!/usr/bin/env python3
"""Repository contract, evidence-chain, semantic, dashboard, link, and safety validation."""

from __future__ import annotations

import json
import math
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

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

RAW_MEASUREMENT_MAP = {
    "ttft_ms": "mean_ttft_ms",
    "ttft_std_ms": "std_ttft_ms",
    "ttft_p50_ms": "p50_ttft_ms",
    "ttft_p90_ms": "p90_ttft_ms",
    "ttft_p95_ms": "p95_ttft_ms",
    "ttft_p99_ms": "p99_ttft_ms",
    "tpot_ms_per_token": "mean_tpot_ms",
    "tpot_std_ms_per_token": "std_tpot_ms",
    "tpot_p50_ms_per_token": "p50_tpot_ms",
    "tpot_p90_ms_per_token": "p90_tpot_ms",
    "tpot_p95_ms_per_token": "p95_tpot_ms",
    "tpot_p99_ms_per_token": "p99_tpot_ms",
    "e2e_wall_ms": "mean_e2el_ms",
    "e2e_std_ms": "std_e2el_ms",
    "e2e_p50_ms": "p50_e2el_ms",
    "e2e_p90_ms": "p90_e2el_ms",
    "e2e_p95_ms": "p95_e2el_ms",
    "e2e_p99_ms": "p99_e2el_ms",
    "inter_token_mean_ms": "mean_itl_ms",
    "inter_token_std_ms": "std_itl_ms",
    "inter_token_p50_ms": "p50_itl_ms",
    "inter_token_p90_ms": "p90_itl_ms",
    "inter_token_p95_ms": "p95_itl_ms",
    "inter_token_p99_ms": "p99_itl_ms",
    "benchmark_duration_s": "duration",
    "request_throughput_rps": "request_throughput",
    "output_throughput_tps": "output_throughput",
    "peak_output_throughput_tps": "max_output_tokens_per_s",
    "runner_peak_concurrent_requests": "max_concurrent_requests",
    "total_token_throughput_tps": "total_token_throughput",
    "total_input_tokens": "total_input_tokens",
    "total_output_tokens": "total_output_tokens",
}


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


def iter_dicts(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from iter_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_dicts(child)


def close_enough(actual: Any, expected: Any) -> bool:
    if isinstance(actual, bool) or isinstance(expected, bool):
        return actual == expected
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        return math.isclose(float(actual), float(expected), rel_tol=1e-6, abs_tol=1e-3)
    return actual == expected


def validate_result_evidence_chain() -> list[str]:
    """Prove canonical result -> redacted raw result -> manifest SHA linkage."""
    errors: list[str] = []

    for path in result_files():
        obj = load_json(path)
        rel = path.relative_to(ROOT)
        evidence = obj.get("evidence", {})
        measurements = obj.get("measurements", {})
        workload = obj.get("workload", {})
        stability = obj.get("stability", {})

        for key in ("environment_snapshot", "raw_log", "raw_result", "server_log", "manifest"):
            value = evidence.get(key)
            if value is None:
                continue
            target = ROOT / value
            if not target.is_file():
                errors.append(f"missing evidence.{key}: {rel} -> {value}")

        raw_path_str = evidence.get("raw_result")
        manifest_path_str = evidence.get("manifest")
        source_sha = evidence.get("result_sha256")
        if not raw_path_str:
            errors.append(f"canonical result missing evidence.raw_result: {rel}")
            continue
        raw_path = ROOT / raw_path_str
        if not raw_path.is_file():
            continue

        try:
            raw = load_json(raw_path)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"raw result is not valid JSON: {rel} -> {raw_path_str}: {exc}")
            continue

        # Tested-at time should preserve the runner's local timestamp exactly.
        raw_date = raw.get("date")
        tested_at = obj.get("tested_at")
        if raw_date and tested_at:
            try:
                normalized = datetime.fromisoformat(tested_at).strftime("%Y%m%d-%H%M%S")
                if normalized != raw_date:
                    errors.append(f"tested_at does not match raw date: {rel}: {normalized} != {raw_date}")
            except ValueError:
                errors.append(f"invalid tested_at for raw-date comparison: {rel}: {tested_at}")

        scalar_pairs = {
            "workload.prompt_count": (workload.get("prompt_count"), raw.get("num_prompts")),
            "workload.concurrency": (workload.get("concurrency"), raw.get("max_concurrency")),
            "stability.completed_requests": (stability.get("completed_requests"), raw.get("completed")),
            "stability.failed_requests": (stability.get("failed_requests"), raw.get("failed")),
        }
        for label, (canonical_value, raw_value) in scalar_pairs.items():
            if canonical_value is not None and raw_value is not None and canonical_value != raw_value:
                errors.append(f"canonical/raw mismatch {label}: {rel}: {canonical_value} != {raw_value}")

        if stability.get("completed", False):
            input_lens = raw.get("input_lens", [])
            output_lens = raw.get("output_lens", [])
            if input_lens and any(v != workload.get("actual_input_tokens") for v in input_lens):
                errors.append(f"raw input lengths disagree with canonical actual_input_tokens: {rel}")
            if output_lens and any(v != workload.get("actual_output_tokens") for v in output_lens):
                errors.append(f"raw output lengths disagree with canonical actual_output_tokens: {rel}")

            for canonical_key, raw_key in RAW_MEASUREMENT_MAP.items():
                canonical_value = measurements.get(canonical_key)
                raw_value = raw.get(raw_key)
                if canonical_value is None or raw_value is None:
                    continue
                if not close_enough(canonical_value, raw_value):
                    errors.append(
                        f"canonical/raw measurement mismatch {canonical_key}: {rel}: "
                        f"{canonical_value} != raw {raw_key}={raw_value}"
                    )

            tpot = measurements.get("tpot_ms_per_token")
            decode = measurements.get("decode_tps")
            if tpot and decode is not None and not close_enough(decode, 1000.0 / tpot):
                errors.append(f"derived decode_tps does not equal 1000/TPOT: {rel}")

            ttft = measurements.get("ttft_ms")
            effective_pp = measurements.get("effective_prefill_tps_derived")
            input_tokens = workload.get("actual_input_tokens")
            if ttft and input_tokens and effective_pp is not None:
                expected_pp = input_tokens / (ttft / 1000.0)
                if not close_enough(effective_pp, expected_pp):
                    errors.append(f"derived Effective Prefill does not equal input/TTFT: {rel}")

        if source_sha and manifest_path_str:
            manifest_path = ROOT / manifest_path_str
            if manifest_path.is_file():
                manifest = load_json(manifest_path)
                matched = any(
                    entry.get("repo_path") == raw_path_str and entry.get("sha256") == source_sha
                    for entry in iter_dicts(manifest)
                )
                if not matched:
                    errors.append(
                        f"manifest does not bind raw_result to result_sha256: {rel}: "
                        f"{raw_path_str} / {source_sha}"
                    )

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
    command = [sys.executable, str(script), "--check"] if script_name == "render_results_dashboard.py" else [sys.executable, str(script)]
    proc = subprocess.run(
        command,
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
    errors += validate_result_evidence_chain()
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
