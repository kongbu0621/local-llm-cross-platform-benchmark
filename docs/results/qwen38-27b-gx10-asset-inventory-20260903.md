# GX10 / Qwen3.8-27B — 结果资产清单与最终审计（2026-09-03）

本页用于回答一个问题：**2026-08-29 ～ 2026-09-03 这轮 GX10 测试到底产生了什么资产，哪些已经进入正式结果链，哪些只是过程证据，哪些仍然没有测。**

审计原则：原始证据不丢、结构化结果不靠手抄、Measured/Derived/Unmeasured 分开、失败保留、语义冲突先修复、没有实测不补洞。

## 1. 原始 Evidence 资产

| 资产 | 状态 | 说明 |
| --- | --- | --- |
| Evidence manifest | ✅ | 90 个原始对象的 normalized path / mtime / size / SHA256 / archive decision |
| 可公开文本 evidence | ✅ | 68 个文本文件经去敏后进入 Git |
| `.nsys-rep` / `.ncu-rep` / SQLite profiler | ✅ hash-only | 二进制 bytes 不直接公开；manifest 保留 SHA256/size/path |
| GX10 repository/environment snapshot | ✅ | Git remotes、Python、kernel、GPU/driver 基础快照 |
| Model freeze SHA256 | ✅ | FP8 / NVFP4 模型文件清单与 hash |
| 历史过程说明 | ✅ | 从 benchmark 准备到 Formal100 / Hardware Gate 的过程与边界 |

入口：[manifest](../../evidence/qwen38-27b-v1.0/gx10-01-xxj/20260902-20260903/manifest.json) · [history](../history/2026-08-29-to-2026-09-03-gx10-qwen38-27b.md) · [environment snapshot](../../evidence/qwen38-27b-v1.0/gx10-01-xxj/20260902-20260903/gx10-repository-snapshot.txt)

## 2. Performance 资产

### Formal5

| 内容 | BF16 | FP8 | NVFP4 | 状态 |
| --- | --- | --- | --- | --- |
| 标准 5-request 32K+256 | ✅ | ✅ | ✅ | 阶段 gate evidence |
| Mean TTFT / TPOT / E2E | ✅ | ✅ | ✅ | Measured |
| Decode / Effective Prefill | ✅ | ✅ | ✅ | Derived |
| Std / P99 / CV | ✅ | ✅ | ✅ | Measured + Derived |
| BF16 多轮阶段 run | ✅ 4 组 | — | — | 保留状态变化证据 |

BF16 多轮：`formal5` / `formal5-steady` / `formal5-immediate2` / `formal5-immediate3`。

### Formal100

| 内容 | BF16 | FP8 | NVFP4 | 状态 |
| --- | --- | --- | --- | --- |
| 100 requests, 32K+256 | 100/100 | 100/100 | 100/100 | ✅ |
| TTFT / TPOT / E2E | ✅ | ✅ | ✅ | Measured |
| Decode / Effective Prefill | ✅ | ✅ | ✅ | Derived |
| TTFT/TPOT/E2E Std + P50/P90/P95/P99 | ✅ | ✅ | ✅ | Measured/statistical |
| ITL mean/std/P50/P90/P95/P99 | ✅ | ✅ | ✅ | Measured/statistical |
| Request / Output / Total-token throughput | ✅ | ✅ | ✅ | Measured |
| Peak output throughput | 5 | 7 | 10 tok/s | Measured runner metric |
| Formal5→Formal100 drift | ✅ | ✅ | ✅ | Derived |
| 100-request duration | 2h45m36.6s | 1h52m38.3s | 1h28m47.5s | Measured |

**实际 runner 范围：** `seed=20260831`、`dataset=random`、固定 32768 input / 256 output、`max_concurrency=1`、`num_warmups=1`、`temperature=0.0`、`request_rate=inf`。因此 Formal100 主批次是 **warm batch**，不是 frozen suite 的 cold-cache isolation。

## 3. Canonical `results/` 资产

审计前发现 `results/` 只有说明文档，README 表格数字没有 canonical machine-readable source，这违反仓库自己“公开主表应由结构化结果生成”的规则。已修复：

| Result | Evidence | Coverage | 入口 |
| --- | --- | --- | --- |
| BF16 Formal100 32K+256 | B | `partial_suite_metrics` | [JSON](../../results/qwen38-27b-v1.0/gb10-01/20260901-bf16-formal100-32k256.json) |
| FP8 Formal100 32K+256 | B | `partial_suite_metrics` | [JSON](../../results/qwen38-27b-v1.0/gb10-01/20260901-fp8-formal100-32k256.json) |
| NVFP4 Formal100 32K+256 | B | `partial_suite_metrics` | [JSON](../../results/qwen38-27b-v1.0/gb10-01/20260831-nvfp4-formal100-32k256.json) |
| NVFP4 B0 gpu085 failed attempt | B | `failed_calibration_attempt` | [JSON](../../results/qwen38-27b-v1.0/gb10-01/20260831-nvfp4-b0-gpu085-failed.json) |

为什么是 Evidence B：raw log/result、model revision、runner 参数、环境和 hash 都可核验，但当前还缺 frozen suite 要求的 Pure Prefill、完整 Peak Memory/KV、cold-cache isolation 等，因此保守不标 A。

## 4. 稳定性资产

| 分析 | 状态 | 结论范围 |
| --- | --- | --- |
| Completion / Failed | ✅ | 当前 100-request warm 32K+256 批次 |
| Std / CV | ✅ | 批次内相对波动 |
| P50/P90/P95/P99 | ✅ | 当前延迟尾部 |
| P99 tail amplification | ✅ Derived | 尾部相对 mean 放大 |
| Formal5→Formal100 drift | ✅ Derived | 阶段均值可重复性/状态变化 |
| 24h soak | ❌ 未测 | 不能外推 |
| reboot/crash recovery | ❌ 未测 | 不能外推 |
| 32K long-output stability | ❌ 未测 | 当前只有 256 output |
| 128K+ context stability | ❌ 未测 | 不能从 32K 外推 |

## 5. Runtime / Hardware Gate 资产

| Gate | 状态 | 关键证据 |
| --- | --- | --- |
| FP8 | FROZEN / PASS / Integrity PASS / Evidence COMPLETE | FP8 checkpoint/runtime、CUTLASS blockwise SM120、Nsys dominant 2048 calls / 84.6%、NCU same-kernel Tensor Pipe nonzero |
| NVFP4 | FROZEN / PASS / Integrity PASS / Evidence COMPLETE | mixed checkpoint、FlashInfer B12x、mixed CUTLASS、Nsys B12x 896 calls / 41.2%、generic SM120 1160 / 51.5%、NCU exact B12x Tensor Pipe nonzero |

边界保持：FP8 有 `modules_to_not_convert`；NVFP4 是 mixed precision compressed-tensors；PM cycles 不是 FLOPs/速度倍率；Hardware Gate 不是质量证明。

## 6. 失败 / Diagnostics 资产

| Evidence | 状态 | 处理 |
| --- | --- | --- |
| NVFP4 B0 gpu_memory_utilization=0.85, client Bad Gateway | ✅ | raw evidence + canonical failed result；不宣称已证明根因 |
| BF16 cold-fault / long-run shutdown EngineDeadError | ✅ | 作为诊断过程，不自动判定硬件故障 |
| BF16 immediate / idle / power-clock traces | ✅ | 解释阶段状态变化 |
| FP8/NVFP4 kernel traces | ✅ | 文本入 Git；二进制 hash-only |

## 7. 衍生决策资产

现有数据已经计算并保存：

- FP8/NVFP4 相对 BF16 的 Effective Prefill、TTFT、TPOT、Decode、E2E gain/reduction/speedup；
- NVFP4 相对 FP8 的同类收益；
- 单请求 TTFT/E2E 绝对节省秒数；
- 100 requests 实际节省 wall-clock；
- measured-equivalent requests/hour；
- TTFT 占 E2E 比例与 post-first-token tail；
- “Decode 加速后瓶颈向 TTFT/Prefill 迁移”的工程结论；
- CV、P99 tail、Formal5→Formal100 drift；
- runner aggregate throughput 与 single-request Decode 的区别。

入口：[衍生数据与决策结论](qwen38-27b-gx10-derived-analysis-20260903.md)。

## 8. 本次最终审计抓出的语义/架构问题

| 问题 | 风险 | 修复 |
| --- | --- | --- |
| `max_output_tokens_per_s` 被误读为“输出速度 cap” | 错误判定 Formal5 合同差异 | ✅ 修正为 vLLM measured Peak output throughput |
| README 手抄数字，`results/` 为空 | 页面可能与机器数据漂移 | ✅ Canonical results + renderer + CI sync check |
| Formal100 有 1 warmup，却容易被当 cold-cache suite 结果 | comparison semantics 错位 | ✅ 标记 `warm` / `platform_optimized` / partial coverage |
| `gb10-01` registry 仍写 owned/pending | 元数据与已发布结果冲突 | ✅ registry/profile 改 `tested` |
| evidence host alias=`gx10-01-xxj`，hardware node=`gb10-01` | 身份映射容易混乱 | ✅ profile/result 显式记录 alias |
| Failed vLLM JSON 里的 0 latency | 可能被误当“0ms 超快” | ✅ canonical failed result 使用 `null` |
| Effective Prefill 可能被误叫 Pure Prefill | 指标语义污染 | ✅ 统一 glossary + `pp_tps=null` |
| 32K+256 可能被误叫 `E2E@32K` | 跨仓库比较失真 | ✅ 页面/result/CI semantic boundary 明确 |

## 9. 自动化与一致性

- `scripts/render_results_dashboard.py`：从 canonical Formal100 JSON 生成/校验 README 首页结果表；
- `scripts/validate_repo.py`：除 schema/public safety/suite freeze 外，增加 result semantic、hardware/result coherence、README dashboard sync 检查；
- canonical result 保留 raw evidence path + result SHA256，形成 `README → result → raw evidence → manifest/hash` 链。

## 10. 仍然缺失、必须以后真实测的资产

| 缺口 | 当前状态 | 为什么不能推导 |
| --- | --- | --- |
| Pure Prefill `pp_tps` | ❌ | TTFT 混有调度/首 token/API 开销 |
| Frozen cold-cache isolation | ❌ | 当前 Formal100 主批次已有 1 warmup |
| `E2E@32K` 32K output | ❌ | 当前 output 只有 256 |
| 128K/256K/384K/512K/768K/1M | ❌ | 32K 结果不能外推 |
| Target-context Peak Device/Host/KV | ❌ | 没有 canonical 同合同采集 |
| Quality | ❌ | Hardware/performance gate 不等于质量 |
| 24h soak / recovery | ❌ | 100-request batch 不等于长期稳定 |
| Multi-GX10 scaling | ❌ | 单节点结果不能外推 |

## 11. Merge Gate

最终 Merge 前必须同时满足：

- [x] 原始 evidence 与 manifest 已归档；
- [x] Formal5 / Formal100 / stability / conclusions 可读；
- [x] 指标统一解释；
- [x] Derived analysis；
- [x] Canonical Formal100 results；
- [x] Canonical failed B0 result；
- [x] Hardware registry/profile 与结果状态一致；
- [x] `max_output_tokens_per_s` 语义修复；
- [x] warm/cold 与 comparison mode 边界修复；
- [x] README dashboard 由 canonical result 自动校验；
- [ ] **PR 最终 head CI SUCCESS**；
- [ ] PR diff/链接/语义最终回查 PASS。

在最后两项完成前，PR #2 保持不合并。
