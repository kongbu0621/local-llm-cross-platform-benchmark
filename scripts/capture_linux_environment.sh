#!/usr/bin/env bash
set -euo pipefail

# Human-readable raw capture. Review/redact before publishing.
# Usage: scripts/capture_linux_environment.sh > environment.txt

echo "===== DATE ====="
date --iso-8601=seconds

echo "===== OS ====="
cat /etc/os-release 2>/dev/null || true

echo "===== KERNEL ====="
uname -a

echo "===== ARCH ====="
uname -m

echo "===== CPU ====="
lscpu 2>/dev/null || true

echo "===== MEMORY ====="
free -h 2>/dev/null || true

echo "===== DISK ====="
lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINTS,MODEL 2>/dev/null || true
df -hT 2>/dev/null || true

echo "===== NVIDIA ====="
nvidia-smi 2>/dev/null || true

echo "===== CUDA TOOLKIT ====="
nvcc --version 2>/dev/null || true

echo "===== ROCM ====="
rocminfo 2>/dev/null | head -n 80 || true

echo "===== DOCKER ====="
docker --version 2>/dev/null || true

echo "===== PYTHON ====="
python3 --version 2>/dev/null || true

echo "===== IMPORTANT: REDACTION ====="
echo "Do not publish hostname, IP addresses, tokens, proxy credentials, usernames, or unrelated private paths without review."
