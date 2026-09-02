# GX10 Evidence Ingestion — 2026-09-03

## 需求

把 2026-08-29 ～ 2026-09-03 GX10 / Qwen3.8-27B 实测形成的可公开数据、历史过程证据、运行参数、环境快照与校验信息归档进本仓库，并让 GX10 本地 Working Copy、NAS Git Authority 与 GitHub `main` 最终收敛到同一 commit。

## 架构

- GitHub：Publication / Collaboration。
- NAS：Git Authority，remote 名称 `origin`。
- GitHub remote 名称：`github`。
- GX10 Working Copy：`$HOME/xxj/works/projects/local-llm-cross-platform-benchmark`。
- 采集使用临时 worktree，不直接在用户当前 Working Copy 上组织 evidence commit。
- public-repo safety 优先：文本证据先去敏；无法安全去敏的 binary / oversize payload 只进入 manifest（normalized path / size / SHA256 / archive decision），不把模型权重、凭据或私密网络信息复制到 GitHub。

## 归档输入

1. `$HOME/xxj/data/evidence/qwen38-27b-v1.0/`：本轮 FP8 / NVFP4 runtime-hardware gate 等冻结证据；
2. `$HOME/xxj/benchmarks/raw/`：仅采集 2026-08-29 之后、路径命中 Qwen/GX10/Formal/FP8/NVFP4/BF16/NCU/Nsys 等关键词的相关条目；
3. GX10 当前仓库状态、remotes、Python / kernel / GPU 基础快照。

## 安全规则

- 禁止：模型权重、Token、Cookie、密码、密钥、代理订阅、私有 IP、受限 benchmark 原题、私有项目源码；
- `.log` 文本在归档后改为 `.log.txt`，避免被仓库的 runtime-output ignore 规则静默排除；
- IP、Authorization Bearer、常见 GitHub/OpenAI token 形式和显式 password/token/cookie 赋值会被 redact；
- binary profiler payload 默认 `manifest-only`，防止二进制文件内嵌 hostname/user/path/network metadata 后直接公开；
- 所有发现的对象仍记录 SHA256 与 size，从而保留可核对证据链。

## 收敛流程

```text
reconcile GitHub main -> NAS Authority (ff-only if Authority behind)
→ temporary evidence worktree
→ copy/redact/manifest
→ repository validation
→ push evidence branch to GitHub + NAS
→ PR review/merge on GitHub
→ wait/poll merge commit
→ GitHub main -> NAS Authority ff-only
→ GX10 local main ff-only
→ verify same final SHA
```

任何 diverged main、remote contract mismatch、dirty local main finalize、Authority ahead of GitHub main 等情况都 fail closed，不自动 force/rebase/merge。

## 验收

- GitHub / NAS / GX10 local `main` 同一 SHA；
- GitHub 仅一个长期 `main` + 必要的证据 PR branch（合并后可清理）；
- 本轮 GX10 history summary、Formal100 指标、FP8/NVFP4 profiler gate 结论入仓；
- 本地相关 evidence 形成 redacted text archive + complete manifest；
- `scripts/validate_repo.py` PASS；
- 不把 32K+256 Formal100 错记为仓库 `E2E@32K`。
