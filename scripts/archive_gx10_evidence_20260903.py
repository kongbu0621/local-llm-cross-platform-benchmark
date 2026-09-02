#!/usr/bin/env python3
"""GX10 evidence archival + Git Authority/GitHub convergence helper.

Designed for the 2026-08-29..2026-09-03 Qwen3.8-27B evidence closure.
It is safe to rerun after a router/network interruption: network operations use
bounded retry, evidence collection is rebuilt in a temporary worktree, and all
main-branch reconciliation remains fast-forward-only.

The script never copies model weights or credentials to the public repository.
Text evidence is redacted; binary/unsafe payloads are represented by SHA256
manifest entries.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO_NAME = "local-llm-cross-platform-benchmark"
BRANCH = "evidence/gx10-qwen38-20260903"
AUTHORITY = f"ssh://git-authority/repos/{REPO_NAME}.git"
GITHUB = f"git@github.com:kongbu0621/{REPO_NAME}.git"
DEST = Path("evidence/qwen38-27b-v1.0/gx10-01-xxj/20260902-20260903/raw")
MANIFEST = DEST.parent / "manifest.json"
CUTOFF = dt.datetime(2026, 8, 29, tzinfo=dt.timezone.utc).timestamp()
MAX_TEXT = 5 * 1024 * 1024
TEXT_EXT = {
    ".txt", ".log", ".json", ".jsonl", ".md", ".csv", ".tsv", ".yaml",
    ".yml", ".toml", ".ini", ".cfg", ".conf", ".out", ".err", ".section",
    ".py", ".sh",
}
FORBIDDEN_EXT = {
    ".safetensors", ".gguf", ".pt", ".pth", ".onnx", ".engine", ".plan",
    ".ckpt", ".key", ".pem", ".token",
}
STRONG_KEYWORDS = (
    "qwen", "gx10", "formal", "fp8", "nvfp4", "bf16", "ncu", "nsys",
    "pmsampling", "runtime-hardware-gate",
)
NETWORK_TRANSIENT = (
    "could not resolve hostname",
    "temporary failure in name resolution",
    "network is unreachable",
    "connection timed out",
    "connection timeout",
    "connection reset",
    "connection closed",
    "connection refused",
    "broken pipe",
    "kex_exchange_identification",
    "ssh_exchange_identification",
    "operation timed out",
)


def run(args: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = {
        **os.environ,
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_SSH_COMMAND": "ssh -o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=5 -o ServerAliveCountMax=2",
    }
    try:
        p = subprocess.run(
            args,
            cwd=str(cwd) if cwd else None,
            text=True,
            capture_output=True,
            env=env,
            timeout=90,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"command timeout: {' '.join(args)}") from exc
    if check and p.returncode != 0:
        raise RuntimeError(f"command failed ({p.returncode}): {' '.join(args)}\n{p.stdout}\n{p.stderr}")
    return p


def git(*args: str, cwd: Path, check: bool = True) -> str:
    return run(["git", *args], cwd=cwd, check=check).stdout.strip()


def is_transient_network_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return "command timeout:" in text or any(marker in text for marker in NETWORK_TRANSIENT)


def network_git(*args: str, cwd: Path, attempts: int = 6) -> str:
    """Retry only clear network/SSH transport failures; semantic Git failures fail closed."""
    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            return git(*args, cwd=cwd)
        except Exception as exc:  # noqa: BLE001
            last = exc
            if not is_transient_network_error(exc) or attempt == attempts:
                raise
            delay = min(30, 2 ** (attempt - 1))
            print(
                f"NETWORK_RETRY attempt={attempt}/{attempts} delay={delay}s cmd=git {' '.join(args)}",
                file=sys.stderr,
                flush=True,
            )
            time.sleep(delay)
    assert last is not None
    raise last


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


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
    # Conservative IPv6 forms that contain at least two colons. This intentionally
    # redacts loopback/link-local/public IPv6 alike; evidence does not need addresses.
    text = re.sub(r"(?<![A-Za-z0-9])(?:[0-9A-Fa-f]{0,4}:){2,7}[0-9A-Fa-f]{0,4}(?![A-Za-z0-9])", "<IPV6_REDACTED>", text)
    return text


def remote_url(repo: Path, name: str) -> str | None:
    p = run(["git", "remote", "get-url", name], cwd=repo, check=False)
    return p.stdout.strip() if p.returncode == 0 else None


def ensure_remote_contract(repo: Path) -> None:
    backup = repo / ".git" / "config.bak-before-git-authority-20260903"
    if not backup.exists():
        shutil.copy2(repo / ".git" / "config", backup)
    origin, github = remote_url(repo, "origin"), remote_url(repo, "github")
    if origin == GITHUB and github is None:
        git("remote", "rename", "origin", "github", cwd=repo)
        git("remote", "add", "origin", AUTHORITY, cwd=repo)
    elif origin == AUTHORITY and github is None:
        git("remote", "add", "github", GITHUB, cwd=repo)
    origin, github = remote_url(repo, "origin"), remote_url(repo, "github")
    if origin != AUTHORITY or github != GITHUB:
        raise RuntimeError(f"remote contract mismatch: origin={origin!r}, github={github!r}")


def is_ancestor(repo: Path, old: str, new: str) -> bool:
    return run(["git", "merge-base", "--is-ancestor", old, new], cwd=repo, check=False).returncode == 0


def reconcile_authority(repo: Path) -> str:
    network_git("fetch", "origin", "main", cwd=repo)
    network_git("fetch", "github", "main", cwd=repo)
    a = git("rev-parse", "origin/main", cwd=repo)
    g = git("rev-parse", "github/main", cwd=repo)
    if a == g:
        return g
    if is_ancestor(repo, a, g):
        network_git("push", "--dry-run", "origin", f"{g}:refs/heads/main", cwd=repo)
        network_git("push", "origin", f"{g}:refs/heads/main", cwd=repo)
        network_git("fetch", "origin", "main", cwd=repo)
        if git("rev-parse", "origin/main", cwd=repo) != g:
            raise RuntimeError("Authority did not converge to GitHub main")
        return g
    if is_ancestor(repo, g, a):
        raise RuntimeError("Authority main is ahead of GitHub main; refuse automatic publication to protected/public main")
    raise RuntimeError("Authority and GitHub main diverged; manual reconciliation required")


def candidate_files(home: Path):
    roots = [
        (home / "xxj/data/evidence/qwen38-27b-v1.0", "data-evidence", False),
        (home / "xxj/benchmarks/raw", "benchmarks-raw", True),
    ]
    for root, tag, filter_keywords in roots:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file() or ".git" in p.parts:
                continue
            try:
                st = p.stat()
            except OSError:
                continue
            if filter_keywords:
                low = p.as_posix().lower()
                related = any(k in low for k in STRONG_KEYWORDS) or ("32k" in low and "256" in low)
                if st.st_mtime < CUTOFF or not related:
                    continue
            yield root, tag, p


def collect(repo: Path, wait_for_merge: bool, wait_minutes: int) -> int:
    ensure_remote_contract(repo)
    base = reconcile_authority(repo)
    network_git("fetch", "github", BRANCH, cwd=repo)
    temp_root = Path.home() / "xxj/tmp/llm-evidence-import-20260903"
    run(["git", "worktree", "remove", "--force", str(temp_root)], cwd=repo, check=False)
    shutil.rmtree(temp_root, ignore_errors=True)
    git("worktree", "add", "-B", BRANCH, str(temp_root), f"github/{BRANCH}", cwd=repo)

    home = Path.home()
    manifest: list[dict[str, object]] = []
    copied = 0
    for root, tag, src in candidate_files(home):
        rel = src.relative_to(root)
        st = src.stat()
        entry: dict[str, object] = {
            "source": f"$HOME/{src.relative_to(home).as_posix()}",
            "source_group": tag,
            "size": st.st_size,
            "mtime_utc": dt.datetime.fromtimestamp(st.st_mtime, tz=dt.timezone.utc).isoformat(),
            "sha256": sha256(src),
        }
        ext = src.suffix.lower()
        low_name = src.name.lower()
        if ext in FORBIDDEN_EXT or any(x in low_name for x in ("secret", "credential", "cookie", "token", "password")):
            entry["archive"] = "manifest-only: forbidden-or-sensitive"
        elif ext in TEXT_EXT and st.st_size <= MAX_TEXT:
            try:
                text = src.read_text(encoding="utf-8", errors="replace")
                safe = redact(text, home)
                dst = temp_root / DEST / tag / rel
                if ext == ".log":
                    dst = dst.with_suffix(dst.suffix + ".txt")
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_text(safe, encoding="utf-8")
                entry["archive"] = "copied-redacted-text"
                entry["repo_path"] = dst.relative_to(temp_root).as_posix()
                copied += 1
            except Exception as exc:  # keep inventory even if decode/copy fails
                entry["archive"] = f"manifest-only: copy-error:{type(exc).__name__}"
        else:
            entry["archive"] = "manifest-only: binary-or-oversize"
        manifest.append(entry)

    manifest_path = temp_root / MANIFEST
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": "gx10-evidence-manifest/v1",
                "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                "node_id": "gx10-01-xxj",
                "canonical_base_before_collection": base,
                "copied_redacted_text_files": copied,
                "entries": manifest,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    snapshot = temp_root / DEST.parent / "gx10-repository-snapshot.txt"
    snapshot.write_text(
        redact(
            "\n".join(
                [
                    "# local repository snapshot",
                    git("status", "--short", "--branch", cwd=repo),
                    git("remote", "-v", cwd=repo),
                    run(["python3", "--version"], check=False).stdout.strip(),
                    run(["uname", "-a"], check=False).stdout.strip(),
                    run(
                        [
                            "nvidia-smi",
                            "--query-gpu=name,memory.total,driver_version",
                            "--format=csv,noheader",
                        ],
                        check=False,
                    ).stdout.strip(),
                ]
            )
            + "\n",
            home,
        ),
        encoding="utf-8",
    )

    git("add", "-f", "evidence/qwen38-27b-v1.0/gx10-01-xxj/20260902-20260903", cwd=temp_root)
    changed = run(["git", "diff", "--cached", "--quiet"], cwd=temp_root, check=False).returncode != 0
    if changed:
        git(
            "-c", "user.name=kongbu0621",
            "-c", "user.email=13556302+kongbu0621@users.noreply.github.com",
            "commit", "-m", "evidence: archive GX10 Qwen3.8-27B runtime history",
            cwd=temp_root,
        )
    if (temp_root / "scripts/validate_repo.py").exists():
        run([sys.executable, "scripts/validate_repo.py"], cwd=temp_root)
    head = git("rev-parse", "HEAD", cwd=temp_root)
    # GitHub first, NAS second. If the router drops between the two, rerunning collect
    # starts from the GitHub evidence head and therefore keeps the next commit FF-safe.
    network_git("push", "github", f"HEAD:refs/heads/{BRANCH}", cwd=temp_root)
    network_git("push", "origin", f"HEAD:refs/heads/{BRANCH}", cwd=temp_root)
    print(
        f"COLLECT_PASS branch={BRANCH} head={head} copied_text={copied} manifest_entries={len(manifest)}",
        flush=True,
    )
    print("Waiting for GitHub PR merge; router outages are retried. Ctrl+C is safe; rerun --mode finalize after merge.", flush=True)
    if not wait_for_merge:
        return 0

    deadline = time.time() + max(wait_minutes, 1) * 60
    while time.time() < deadline:
        time.sleep(10)
        try:
            network_git("fetch", "github", "main", cwd=repo)
        except Exception as exc:  # noqa: BLE001
            if is_transient_network_error(exc):
                print("WAIT_NETWORK_OUTAGE: GitHub still unreachable; continuing to wait.", file=sys.stderr, flush=True)
                continue
            raise
        if is_ancestor(repo, head, git("rev-parse", "github/main", cwd=repo)):
            return finalize(repo)
    print(
        f"WAIT_TIMEOUT: PR not merged within {wait_minutes} minutes; rerun with --mode finalize after merge.",
        flush=True,
    )
    return 2


def finalize(repo: Path) -> int:
    ensure_remote_contract(repo)
    final_sha = reconcile_authority(repo)
    branch = git("branch", "--show-current", cwd=repo)
    dirty = bool(git("status", "--porcelain=v1", cwd=repo))
    if branch == "main" and not dirty:
        network_git("fetch", "origin", "main", cwd=repo)
        local = git("rev-parse", "HEAD", cwd=repo)
        if local != final_sha:
            if not is_ancestor(repo, local, final_sha):
                raise RuntimeError(f"local main diverged: local={local} final={final_sha}")
            git("merge", "--ff-only", "origin/main", cwd=repo)
    local = git("rev-parse", "HEAD", cwd=repo)
    if branch == "main" and not dirty and local != final_sha:
        raise RuntimeError(f"local main did not converge: local={local} final={final_sha}")
    print(
        f"FINALIZE_PASS github_main={final_sha} authority_main={final_sha} local_head={local} branch={branch} dirty={dirty}",
        flush=True,
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("collect", "finalize"), default="collect")
    ap.add_argument("--wait-for-merge", action="store_true")
    ap.add_argument("--wait-minutes", type=int, default=120)
    ap.add_argument("--repo", type=Path, default=Path.home() / "xxj/works/projects" / REPO_NAME)
    args = ap.parse_args()
    repo = args.repo.expanduser().resolve()
    if not (repo / ".git").exists():
        raise SystemExit(f"not a Git working copy: {repo}")
    return collect(repo, args.wait_for_merge, args.wait_minutes) if args.mode == "collect" else finalize(repo)


if __name__ == "__main__":
    raise SystemExit(main())
