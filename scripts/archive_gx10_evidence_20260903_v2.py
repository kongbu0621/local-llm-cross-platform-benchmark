#!/usr/bin/env python3
"""Corrected redaction wrapper for GX10 evidence archival.

This wrapper keeps the v1 collection/convergence logic but replaces IPv6 redaction
with parser-validated redaction so ordinary log timestamps such as 10:54:12 are
not destroyed. It is safe to rerun against the same evidence branch.
"""
from __future__ import annotations

import ipaddress
import re
from pathlib import Path

import archive_gx10_evidence_20260903 as base


IPV6_CANDIDATE = re.compile(
    r"(?<![0-9A-Fa-f:])(?:[0-9A-Fa-f:]{2,})(?:%[0-9A-Za-z_.-]+)?(?![0-9A-Fa-f:])"
)


def _replace_ipv6(match: re.Match[str]) -> str:
    token = match.group(0)
    if token.count(":") < 2:
        return token
    addr = token.split("%", 1)[0]
    try:
        parsed = ipaddress.ip_address(addr)
    except ValueError:
        return token
    return "<IPV6_REDACTED>" if parsed.version == 6 else token


def redact(text: str, home: Path) -> str:
    text = text.replace(str(home), "$HOME")
    text = re.sub(r"(?i)(authorization\s*:\s*bearer\s+)\S+", r"\1<REDACTED>", text)
    text = re.sub(
        r"(?i)\b(?:ghp_|github_pat_|hf_|sk-|xox[baprs]-)[A-Za-z0-9_\-]{12,}\b",
        "<REDACTED_TOKEN>",
        text,
    )
    text = re.sub(
        r"(?i)\b(password|passwd|token|cookie|api[_-]?key|access[_-]?key|secret[_-]?key|auth[_-]?token|bearer[_-]?token)\s*[=:]\s*[^\s,;]+",
        r"\1=<REDACTED>",
        text,
    )
    text = re.sub(r"(?i)(https?://)[^/@\s:]+:[^/@\s]+@", r"\1<REDACTED_CREDENTIALS>@", text)
    text = re.sub(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "<IP_REDACTED>", text)
    return IPV6_CANDIDATE.sub(_replace_ipv6, text)


def _self_test() -> None:
    home = Path("/home/example")
    sample = (
        "INFO 09-02 10:54:12 timestamp must survive; "
        "v4=192.168.1.20 v6=2001:db8::1 loopback=::1 "
        "path=/home/example/xxj"
    )
    got = redact(sample, home)
    assert "10:54:12" in got
    assert "192.168.1.20" not in got and "<IP_REDACTED>" in got
    assert "2001:db8::1" not in got and "::1" not in got
    assert got.count("<IPV6_REDACTED>") == 2
    assert "$HOME/xxj" in got


base.redact = redact


if __name__ == "__main__":
    _self_test()
    raise SystemExit(base.main())
