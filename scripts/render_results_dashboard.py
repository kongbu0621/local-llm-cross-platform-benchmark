#!/usr/bin/env python3
"""Render/verify the README Formal100 dashboard from canonical result JSONs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
BEGIN = "<!-- BEGIN AUTO:FORMAL100_DASHBOARD -->"
END = "<!-- END AUTO:FORMAL100_DASHBOARD -->"
DETAIL = "docs/results/qwen38-27b-gx10-20260903.md#formal100-performance"

RESULTS = [
    ("BF16", ROOT / "results/qwen38-27b-v1.0/gb10-01/20260901-bf16-formal100-32k256.json"),
    ("FP8", ROOT / "results/qwen38-27b-v1.0/gb10-01/20260901-fp8-formal100-32k256.json"),
    ("NVFP4", ROOT / "results/qwen38-27b-v1.0/gb10-01/20260831-nvfp4-formal100-32k256.json"),
]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def f(value: float | None, digits: int = 3) -> str:
    return "未测" if value is None else f"{value:.{digits}f}"


def render() -> str:
    rows = []
    for precision, path in RESULTS:
        obj = load(path)
        work = obj["workload"]
        meas = obj["measurements"]
        pure = f(meas.get("pp_tps")) if meas.get("pp_tps") is not None else "未单独测"
        cache = work["cache_state"]
        warmups = work.get("num_warmups", 0)
        if warmups:
            cache = f"{cache} ({warmups} warmup)"
        completion = f"{obj['stability'].get('completed_requests', 0)}/{work.get('prompt_count', 0)}"
        rows.append(
            "| 1× GX10 / GB10 | Qwen3.8-27B | "
            f"{precision} | 32K + 256 | {cache} | {obj['comparison_mode']} | {obj['evidence_level']} | "
            f"{f(meas.get('effective_prefill_tps_derived'))} | {pure} | {f(meas.get('ttft_ms'))} | "
            f"{f(meas.get('tpot_ms_per_token'))} | {f(meas.get('decode_tps'))} | "
            f"{f(meas.get('e2e_wall_ms'))} | {completion} | [完整详情]({DETAIL}) |"
        )

    lines = [
        BEGIN,
        "| Hardware | Model | Precision | Workload | Cache | Mode | Evidence | Effective Prefill* (tok/s) | Pure Prefill (tok/s) | TTFT (ms) | TPOT (ms/token) | Decode (tok/s) | E2E (ms) | Completion | 详情 |",
        "| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
        *rows,
        END,
    ]
    return "\n".join(lines)


def replace_block(text: str, block: str) -> str:
    if BEGIN not in text or END not in text:
        raise SystemExit("README dashboard markers are missing")
    before, rest = text.split(BEGIN, 1)
    _, after = rest.split(END, 1)
    return before + block + after


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args()

    expected_block = render()
    current = README.read_text(encoding="utf-8")
    expected = replace_block(current, expected_block)

    if args.check:
        if current != expected:
            print("README Formal100 dashboard is out of sync with canonical results")
            return 1
        print("README Formal100 dashboard matches canonical results")
        return 0

    README.write_text(expected, encoding="utf-8")
    print("README Formal100 dashboard updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
