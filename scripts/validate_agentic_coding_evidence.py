#!/usr/bin/env python3
"""Validate external agentic-coding evidence without promoting it to first-party qualification."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas/agentic-coding-evidence.schema.json"
MODEL_SCHEMA = ROOT / "schemas/model-intelligence.schema.json"
LEDGER = ROOT / "model-intelligence/agentic-coding-evidence.json"
PRIMARY_REGISTRY = ROOT / "model-intelligence/registry.json"
NON_ACTIVE_LIFECYCLES = {"REJECTED", "DEPRECATED", "SUPERSEDED"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_primary_model_records(errors: list[str]) -> tuple[dict[str, dict], dict[str, list[dict]]]:
    """Load the single authoritative Model Intelligence registry."""
    records: dict[str, dict] = {}
    families: dict[str, list[dict]] = {}

    if not PRIMARY_REGISTRY.exists():
        errors.append("missing model-intelligence/registry.json")
        return records, families
    if not MODEL_SCHEMA.exists():
        errors.append("missing schemas/model-intelligence.schema.json")
        return records, families

    model_schema = load(MODEL_SCHEMA)
    Draft202012Validator.check_schema(model_schema)
    validator = Draft202012Validator(model_schema, format_checker=FormatChecker())
    obj = load(PRIMARY_REGISTRY)

    for err in sorted(validator.iter_errors(obj), key=lambda e: list(e.path)):
        where = ".".join(str(p) for p in err.path) or "<root>"
        errors.append(f"primary model registry schema error: model-intelligence/registry.json:{where}: {err.message}")

    for record in obj.get("records", []):
        rid = record.get("record_id")
        if not isinstance(rid, str) or not rid:
            errors.append("model-intelligence/registry.json contains record without record_id")
            continue
        if rid in records:
            errors.append(f"duplicate primary Model Intelligence record_id: {rid}")
            continue
        records[rid] = record
        family = record.get("model_family")
        if isinstance(family, str) and family:
            families.setdefault(family, []).append(record)

    return records, families


def main() -> int:
    errors: list[str] = []

    if not SCHEMA.exists():
        errors.append("missing schemas/agentic-coding-evidence.schema.json")
    if not LEDGER.exists():
        errors.append("missing model-intelligence/agentic-coding-evidence.json")
    model_records, model_families = load_primary_model_records(errors)
    if errors:
        print("AGENTIC CODING EVIDENCE VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    schema = load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    ledger = load(LEDGER)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    for err in sorted(validator.iter_errors(ledger), key=lambda e: list(e.path)):
        where = ".".join(str(p) for p in err.path) or "<root>"
        errors.append(f"schema error {where}: {err.message}")

    seen: set[str] = set()
    for record in ledger.get("records", []):
        eid = record.get("evidence_id")
        if eid in seen:
            errors.append(f"duplicate evidence_id: {eid}")
        seen.add(eid)

        scope = record.get("result_scope")
        registry_id = record.get("registry_record_id")
        registry_record = model_records.get(registry_id)
        family = record.get("model_family")

        if scope == "AGENTIC_CODING_TASKS":
            if registry_record is None:
                errors.append(
                    f"{eid}: AGENTIC_CODING_TASKS registry_record_id must resolve in primary "
                    f"model-intelligence/registry.json: {registry_id}"
                )
            else:
                if registry_record.get("model_family") != family:
                    errors.append(
                        f"{eid}: model_family differs from primary registry {registry_id}: "
                        f"{family} != {registry_record.get('model_family')}"
                    )
                if registry_record.get("lifecycle") in NON_ACTIVE_LIFECYCLES:
                    errors.append(
                        f"{eid}: positive agentic-coding evidence cannot resolve to non-active "
                        f"primary registry lifecycle={registry_record.get('lifecycle')}"
                    )
                if registry_record.get("lifecycle") == "RECOMMENDED":
                    errors.append(
                        f"{eid}: external agentic evidence may not point to a RECOMMENDED record; "
                        "first-party production qualification must remain separate"
                    )

        elif scope == "NEGATIVE_CONFIGURATION_EVIDENCE":
            if registry_record is not None:
                if registry_record.get("model_family") != family:
                    errors.append(
                        f"{eid}: negative exact-variant record has different model_family: "
                        f"{family} != {registry_record.get('model_family')}"
                    )
                if registry_record.get("lifecycle") not in NON_ACTIVE_LIFECYCLES:
                    errors.append(
                        f"{eid}: negative configuration evidence exact record must use an explicitly "
                        f"non-active lifecycle; got {registry_record.get('lifecycle')}"
                    )
            elif not model_families.get(family):
                errors.append(
                    f"{eid}: negative configuration evidence must resolve either to an explicit "
                    f"negative primary Variant or to a documented primary Model Family; "
                    f"no primary family found for {family}"
                )

        passed = record.get("hidden_tests_passed")
        total = record.get("hidden_tests_total")
        if isinstance(passed, int) and isinstance(total, int) and passed > total:
            errors.append(f"{eid}: hidden_tests_passed cannot exceed hidden_tests_total")

        run_count = record.get("run_count")
        repeat_min = record.get("observed_repeat_min_hidden_tests")
        repeat_max = record.get("observed_repeat_max_hidden_tests")
        if isinstance(repeat_min, int) and isinstance(repeat_max, int) and repeat_min > repeat_max:
            errors.append(f"{eid}: observed repeat min cannot exceed max")
        if isinstance(repeat_min, int) and isinstance(total, int) and repeat_min > total:
            errors.append(f"{eid}: observed repeat min cannot exceed hidden_tests_total")
        if isinstance(repeat_max, int) and isinstance(total, int) and repeat_max > total:
            errors.append(f"{eid}: observed repeat max cannot exceed hidden_tests_total")
        if run_count == 1 and (repeat_min is not None or repeat_max is not None):
            errors.append(f"{eid}: single-run evidence cannot claim a repeat range")
        if isinstance(run_count, int) and run_count > 1 and (repeat_min is None or repeat_max is None):
            errors.append(f"{eid}: repeated evidence requires observed repeat min/max")
        if isinstance(repeat_min, int) and isinstance(passed, int) and passed < repeat_min:
            errors.append(f"{eid}: representative hidden_tests_passed cannot be below observed repeat min")
        if isinstance(repeat_max, int) and isinstance(passed, int) and passed > repeat_max:
            errors.append(f"{eid}: representative hidden_tests_passed cannot exceed observed repeat max")

        context = record.get("configured_context_tokens")
        if context is not None and context < 1024:
            errors.append(f"{eid}: suspicious configured_context_tokens < 1024")

        sources = record.get("source_refs", [])
        if not any(isinstance(src, str) and src.startswith("https://github.com/") for src in sources):
            errors.append(f"{eid}: reproducible coding evidence requires at least one GitHub source")

        notes = (record.get("notes") or "").lower()
        caveats = " ".join(record.get("caveats", [])).lower()
        if scope == "NEGATIVE_CONFIGURATION_EVIDENCE" and not any(
            token in (notes + " " + caveats) for token in ("configuration", "config", "not a verdict", "not a model")
        ):
            errors.append(f"{eid}: negative configuration evidence must explicitly prevent family-level overgeneralization")

        # This ledger is external-only by design. It may influence test priority, never repo qualification.
        forbidden_keys = {
            "production_qualified",
            "quality_qualified",
            "recommendation_status",
            "fitness",
            "overall_score",
        }
        bad = sorted(forbidden_keys.intersection(record))
        if bad:
            errors.append(f"{eid}: external evidence ledger contains forbidden qualification fields: {bad}")

    if errors:
        print("AGENTIC CODING EVIDENCE VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("AGENTIC CODING EVIDENCE VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
