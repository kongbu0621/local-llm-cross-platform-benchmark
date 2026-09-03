#!/usr/bin/env python3
"""Validate Decision System v1 schemas and semantic hard rules."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

SCHEMAS = {
    "workload": ROOT / "schemas/workload-contract.schema.json",
    "model_intelligence": ROOT / "schemas/model-intelligence.schema.json",
    "agent": ROOT / "schemas/agent-fitness-assessment.schema.json",
    "production": ROOT / "schemas/production-fitness-assessment.schema.json",
    "recommendation": ROOT / "schemas/recommendation.schema.json",
}

FORBIDDEN_SCORE_KEYS = {"score", "overall_score", "ranking_score", "fitness_score"}
HARDWARE_KINDS = {
    "COMPONENT_UPGRADE",
    "ADD_HOMOGENEOUS_NODE",
    "SPLIT_REDESIGN_TOPOLOGY",
    "PLATFORM_REPLACEMENT",
}
POSITIVE_HARDWARE_FIT = {"EXCELLENT", "GOOD", "FAIR"}
POSITIVE_HARDWARE_EVIDENCE = {"FIRST_PARTY_MEASURED", "REPRODUCIBLE_EXTERNAL"}
MEASURED_CONTEXT_EVIDENCE = {"FIRST_PARTY_MEASURED", "REPRODUCIBLE_EXTERNAL"}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_schema_files() -> list[str]:
    errors: list[str] = []
    for name, path in SCHEMAS.items():
        if not path.exists():
            errors.append(f"missing decision schema: {path.relative_to(ROOT)}")
            continue
        try:
            Draft202012Validator.check_schema(load(path))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"invalid decision schema {name}: {exc}")
    return errors


def schema_errors(path: Path, schema_name: str) -> list[str]:
    schema = load(SCHEMAS[schema_name])
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    obj = load(path)
    out: list[str] = []
    for err in sorted(validator.iter_errors(obj), key=lambda e: list(e.path)):
        where = ".".join(str(p) for p in err.path) or "<root>"
        out.append(f"schema error: {path.relative_to(ROOT)}:{where}: {err.message}")
    return out


def walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def reject_aggregate_scores(path: Path, obj: Any) -> list[str]:
    errors: list[str] = []
    for node in walk(obj):
        bad = FORBIDDEN_SCORE_KEYS.intersection(node)
        for key in sorted(bad):
            errors.append(
                f"forbidden aggregate score field {key}: {path.relative_to(ROOT)}; "
                "use Hard Gates + Qualification + Fitness"
            )
    return errors


def validate_refs(path: Path, obj: Any) -> list[str]:
    errors: list[str] = []
    ref_keys = {"evidence_refs", "source_refs"}
    for node in walk(obj):
        for key in ref_keys:
            refs = node.get(key)
            if not isinstance(refs, list):
                continue
            for ref in refs:
                if not isinstance(ref, str) or not ref or ref.startswith(("http://", "https://")):
                    continue
                rel = ref.split("#", 1)[0]
                if rel and not (ROOT / rel).exists():
                    errors.append(f"broken local {key[:-1]}: {path.relative_to(ROOT)} -> {ref}")
    return errors


def validate_qualification(path: Path, obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    qualification = obj.get("qualification")
    fitness = obj.get("fitness")
    gates = obj.get("hard_gates", [])

    if qualification in {"OPEN", "NOT_QUALIFIED"} and fitness is not None:
        errors.append(
            f"{path.relative_to(ROOT)}: qualification={qualification} requires fitness=null; "
            "unknown/fail must not be averaged into a score"
        )

    blocking_fail = any(g.get("blocking") and g.get("status") == "FAIL" for g in gates)
    blocking_open = any(g.get("blocking") and g.get("status") == "OPEN" for g in gates)
    if blocking_fail and qualification != "NOT_QUALIFIED":
        errors.append(f"{path.relative_to(ROOT)}: blocking FAIL requires NOT_QUALIFIED")
    if blocking_open and qualification == "QUALIFIED":
        errors.append(f"{path.relative_to(ROOT)}: blocking OPEN cannot be QUALIFIED")
    return errors


def validate_topology_modes(path: Path, obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for mode in obj.get("topology_modes", []):
        if mode.get("qualification") in {"OPEN", "NOT_QUALIFIED"} and mode.get("fitness") is not None:
            errors.append(
                f"{path.relative_to(ROOT)} topology={mode.get('mode')}: "
                "OPEN/NOT_QUALIFIED requires fitness=null"
            )
    return errors


def validate_model_registry(path: Path, obj: dict[str, Any]) -> list[str]:
    """Enforce evidence, topology, context, and recommendation boundaries."""

    errors: list[str] = []
    seen: set[str] = set()

    for record in obj.get("records", []):
        rid = record.get("record_id")
        if rid in seen:
            errors.append(f"duplicate model-intelligence record_id: {rid}")
        seen.add(rid)

        # External quality evidence can make a model worth testing, but only this
        # repository's own Quality Gate may mark it QUALIFIED.
        quality_evidence = record.get("quality_evidence_confidence")
        quality_status = record.get("quality_status")
        if quality_evidence != "FIRST_PARTY_MEASURED" and quality_status != "OPEN":
            errors.append(
                f"model {rid}: non-first-party quality evidence requires quality_status=OPEN; "
                "external evidence is candidate evidence, not repo qualification"
            )

        fits = record.get("hardware_fit_summary", {})
        evidence_by_topology = record.get("hardware_evidence_by_topology", {})

        if set(fits) != set(evidence_by_topology):
            errors.append(
                f"model {rid}: hardware_fit_summary and hardware_evidence_by_topology "
                "must have identical topology keys"
            )

        # A positive topology-specific fit needs either first-party evidence or a
        # reproducible same-hardware external result. STRONG_EXTERNAL can support
        # CONDITIONAL, not GOOD/EXCELLENT/FAIR.
        for topology, fit in fits.items():
            evidence = evidence_by_topology.get(topology, "UNKNOWN")
            if fit in POSITIVE_HARDWARE_FIT and evidence not in POSITIVE_HARDWARE_EVIDENCE:
                errors.append(
                    f"model {rid} topology={topology}: fit={fit} requires "
                    "FIRST_PARTY_MEASURED or REPRODUCIBLE_EXTERNAL hardware evidence; "
                    f"got {evidence}"
                )

        if any(v == "REPRODUCIBLE_EXTERNAL" for v in evidence_by_topology.values()):
            refs = record.get("source_refs", [])
            if not any(
                isinstance(ref, str) and ref.startswith(("http://", "https://"))
                for ref in refs
            ):
                errors.append(
                    f"model {rid}: REPRODUCIBLE_EXTERNAL hardware evidence requires "
                    "at least one external source_ref"
                )

        # Context evidence is deliberately separate from hardware fit:
        # configured/model-length != actual deep prompt != retrieval quality.
        for topology, ctx in record.get("context_evidence_by_topology", {}).items():
            configured = ctx.get("configured_context_tokens")
            actual = ctx.get("actual_prompt_tokens")
            retrieval = ctx.get("retrieval_validated_tokens")
            evidence = ctx.get("evidence_confidence")

            if configured is not None and actual is not None and actual > configured:
                errors.append(
                    f"model {rid} context={topology}: actual_prompt_tokens={actual} "
                    f"exceeds configured_context_tokens={configured}"
                )
            if retrieval is not None:
                if actual is None:
                    errors.append(
                        f"model {rid} context={topology}: retrieval_validated_tokens "
                        "requires actual_prompt_tokens"
                    )
                elif retrieval > actual:
                    errors.append(
                        f"model {rid} context={topology}: retrieval_validated_tokens={retrieval} "
                        f"exceeds actual_prompt_tokens={actual}"
                    )
            if (actual is not None or retrieval is not None) and evidence not in MEASURED_CONTEXT_EVIDENCE:
                errors.append(
                    f"model {rid} context={topology}: actual/retrieval token evidence "
                    f"requires FIRST_PARTY_MEASURED or REPRODUCIBLE_EXTERNAL; got {evidence}"
                )

        if record.get("lifecycle") == "RECOMMENDED":
            if record.get("quality_status") != "QUALIFIED":
                errors.append(f"model {rid}: RECOMMENDED requires quality_status=QUALIFIED")
            if record.get("quality_evidence_confidence") != "FIRST_PARTY_MEASURED":
                errors.append(f"model {rid}: RECOMMENDED requires first-party quality evidence")
            if not record.get("production_qualification_ref"):
                errors.append(f"model {rid}: RECOMMENDED requires production_qualification_ref")
            if record.get("recommendation_confidence") not in {"HIGH", "MEDIUM"}:
                errors.append(
                    f"model {rid}: RECOMMENDED requires non-open recommendation confidence"
                )

    return errors


def validate_recommendation(path: Path, obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    options = obj.get("options", [])
    by_id = {item.get("option_id"): item for item in options}
    selected = obj.get("selected_option")
    if selected is not None and selected not in by_id:
        errors.append(f"{path.relative_to(ROOT)}: selected_option does not exist: {selected}")

    for option in options:
        if option.get("kind") in HARDWARE_KINDS and option.get("status") == "ACTION":
            cf = option.get("counterfactual_no_hardware", {}).get("result")
            if cf != "INSUFFICIENT":
                errors.append(
                    f"{path.relative_to(ROOT)} option={option.get('option_id')}: "
                    "hardware ACTION requires counterfactual_no_hardware=INSUFFICIENT"
                )
            for key in (
                "trigger",
                "expected_gain",
                "does_not_solve",
                "residual_bottleneck",
                "new_failure_domains",
            ):
                value = option.get(key)
                if value in (None, "", []):
                    errors.append(
                        f"{path.relative_to(ROOT)} option={option.get('option_id')}: "
                        f"hardware ACTION missing {key}"
                    )

    if selected is not None:
        choice = by_id[selected]
        if choice.get("status") != "ACTION":
            errors.append(f"{path.relative_to(ROOT)}: selected option must have status=ACTION")
    return errors


def validate_time_order(path: Path, obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    a, b = obj.get("evaluated_at"), obj.get("evidence_as_of")
    if isinstance(a, str) and isinstance(b, str):
        try:
            if datetime.fromisoformat(b) > datetime.fromisoformat(a):
                errors.append(
                    f"{path.relative_to(ROOT)}: evidence_as_of cannot be later than evaluated_at"
                )
        except ValueError:
            pass
    return errors


def validate_dir(root: Path, schema_name: str) -> list[str]:
    errors: list[str] = []
    if not root.exists():
        return [f"missing decision data directory: {root.relative_to(ROOT)}"]
    for path in sorted(root.rglob("*.json")):
        obj = load(path)
        errors += schema_errors(path, schema_name)
        errors += reject_aggregate_scores(path, obj)
        errors += validate_refs(path, obj)
        if schema_name in {"agent", "production"}:
            errors += validate_qualification(path, obj)
            errors += validate_time_order(path, obj)
        if schema_name == "production":
            errors += validate_topology_modes(path, obj)
        if schema_name == "recommendation":
            errors += validate_recommendation(path, obj)
            errors += validate_time_order(path, obj)
    return errors


def main() -> int:
    errors: list[str] = []
    errors += validate_schema_files()

    registry = ROOT / "model-intelligence/registry.json"
    if not registry.exists():
        errors.append("missing model-intelligence/registry.json")
    else:
        obj = load(registry)
        errors += schema_errors(registry, "model_intelligence")
        errors += reject_aggregate_scores(registry, obj)
        errors += validate_refs(registry, obj)
        errors += validate_model_registry(registry, obj)

    errors += validate_dir(ROOT / "assessments/agent", "agent")
    errors += validate_dir(ROOT / "assessments/production", "production")
    errors += validate_dir(ROOT / "recommendations", "recommendation")

    if errors:
        print("DECISION SYSTEM VALIDATION FAILED")
        for item in errors:
            print(f"- {item}")
        return 1

    print("DECISION SYSTEM VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
