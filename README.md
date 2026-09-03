# Local LLM Cross-Platform Benchmark

一个长期维护、可复现、以真实硬件实测为核心的本地大模型（Local LLM）跨平台能力数据库。

本仓库不只比较 `tokens/s`。目标是记录同一模型在不同真实硬件、操作系统、推理栈、量化、上下文长度和工作负载下的 **质量、性能、内存、稳定性、效率与可复现证据**。

## 当前已验证实测结果

> 当前首页展示的是已进入 `results/` canonical result 的 GX10 Formal100 **部分 suite 数据**：32,768 input + 256 output、Concurrency=1、1 次 warmup 后主批次。它不是 frozen suite 的 cold-cache 完整 isolation，也不是仓库固定定义的 `E2E@32K`（32,768 input + 32,768 output）。

<!-- BEGIN AUTO:FORMAL100_DASHBOARD -->
| Hardware | Model | Precision | Workload | Cache | Mode | Evidence | Effective Prefill* (tok/s) | Pure Prefill (tok/s) | TTFT (ms) | TPOT (ms/token) | Decode (tok/s) | E2E (ms) | Completion | 详情 |
| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1× GX10 / GB10 | Qwen3.8-27B | BF16 | 32K + 256 | warm (1 warmup) | platform_optimized | B | 936.453 | 未单独测 | 34991.596 | 252.447 | 3.961 | 99365.625 | 100/100 | [完整详情](docs/results/qwen38-27b-gx10-20260903.md#formal100-performance) |
| 1× GX10 / GB10 | Qwen3.8-27B | FP8 | 32K + 256 | warm (1 warmup) | platform_optimized | B | 1187.130 | 未单独测 | 27602.710 | 156.783 | 6.378 | 67582.360 | 100/100 | [完整详情](docs/results/qwen38-27b-gx10-20260903.md#formal100-performance) |
| 1× GX10 / GB10 | Qwen3.8-27B | NVFP4 | 32K + 256 | warm (1 warmup) | platform_optimized | B | 1300.614 | 未单独测 | 25194.249 | 110.122 | 9.081 | 53275.252 | 100/100 | [完整详情](docs/results/qwen38-27b-gx10-20260903.md#formal100-performance) |
<!-- END AUTO:FORMAL100_DASHBOARD -->

\* `Effective Prefill* = 32768 / TTFT(s)`，是 Derived 的实际首 token 链路有效输入速度，**不是 Pure Prefill `pp_tps`**。Pure Prefill 本轮没有独立测量，因此保持“未单独测”。

这张首页表由 `results/qwen38-27b-v1.0/gb10-01/*.json` 的 canonical Formal100 结果生成/校验；CI 会阻止 README 数字与结构化结果静默漂移。

**看不懂 Prefill / TTFT / TPOT / Decode / E2E / Std / P99 / CV？** 统一看：[Benchmark 指标统一解释](docs/metrics/benchmark-metrics-glossary.md)。

### 这一轮的数据资产

- **Canonical Results**：[BF16 / FP8 / NVFP4 Formal100 + NVFP4 failed B0](results/qwen38-27b-v1.0/gb10-01/)
- **指标统一解释**：[Measured / Derived / Unmeasured、Prefill、TTFT、TPOT、Decode、E2E、ITL、Std、CV、P50-P99、Peak output、throughput、drift](docs/metrics/benchmark-metrics-glossary.md)
- **衍生数据与决策结论**：[相对收益、单请求节省时间、100 请求成本、requests/hour、E2E 阶段占比、瓶颈迁移、tail、可重复性](docs/results/qwen38-27b-gx10-derived-analysis-20260903.md)
- **Formal5（5 次）阶段数据**：[三档横向表 + BF16 多轮 Formal5](docs/results/qwen38-27b-gx10-20260903.md#formal5-performance)
- **Formal100（100 次）正式 warm-batch 性能**：[runner 参数、均值、duration、Completion、Effective Prefill / Decode / E2E](docs/results/qwen38-27b-gx10-20260903.md#formal100-performance)
- **Formal100 批次稳定性**：[Std / CV / P50 / P90 / P95 / P99 / ITL / Formal5→100 drift](docs/results/qwen38-27b-gx10-20260903.md#formal100-stability)
- **FP8 / NVFP4 Runtime + Hardware Gate**：[checkpoint → runtime → inference → Nsys → NCU → Tensor Pipe](docs/results/qwen38-27b-gx10-20260903.md#runtime-gates)
- **失败与诊断过程**：[NVFP4 B0 Bad Gateway、BF16 diagnostics、kernel trace](docs/results/qwen38-27b-gx10-20260903.md#failure-evidence)
- **最终结论与边界**：[哪些成立、哪些仍必须新增实测](docs/results/qwen38-27b-gx10-20260903.md#conclusions)
- **原始证据入口**：[Formal/B0/Diagnostics/Gates/Manifest/History](docs/results/qwen38-27b-gx10-20260903.md#raw-evidence-index)
- **结果资产审计清单**：[本轮测试、证据、结构化结果、修复项与缺口](docs/results/qwen38-27b-gx10-asset-inventory-20260903.md)

后续 128K / 256K / 384K / 512K / 768K / 1M、32K-output E2E、Pure Prefill、Peak Memory/KV、cold-cache isolation、质量、24h soak、PRO 6000、2×/4× GB10、Apple / AMD 等完成后，继续追加；没有可靠实测的数据保持“未测 / 不可计算”。

## 核心原则

1. **主结果只来自真实拥有并实际运行过的硬件。** `planned` 仅表示未来可能接入，不进入正式结果或排名。
2. **同一把尺子跨平台复用。** NVIDIA、Apple，以及未来实际购入的 AMD / Intel / 其他平台，尽可能使用同一测试母本、同一结果合同与同一证据等级。
3. **不把“配置上限”当“实测能力”。** `Actual Context` 必须是实际完成测试的上下文长度。
4. **失败也是结果。** OOM、崩溃、early-EOS、乱码、重复输出、长上下文失效都应保留证据。
5. **历史结果不静默覆盖。** 测试方法变化通过新 suite/version 发布；旧数据可标记 `superseded` / `invalidated`，但不篡改历史。
6. **平台公平层与平台最优层分开。** 前者尽量控制变量，后者允许各平台使用自身最优 runtime/kernel/量化。
7. **模型权重、Token、代理配置、私有数据和受限制 benchmark 原题不进入公共仓库。**

## 实验维度

至少记录：Hardware、Node Topology、OS、Driver/Compute Stack、Model Revision、Weight Precision、KV Precision、Runtime、Optimization Stack、Actual Context、Output Length、Reasoning/Sampling、Cache State、Concurrency、Workload、Test Date。

## 核心指标

- Prefill / PP tok/s
- TTFT (Time To First Token)
- Decode / TG tok/s
- E2E@32K
- Peak Memory / KV Cache / Host Memory
- Quality（Reasoning / Coding / Instruction / Long Context / Agent）
- Stability / Reliability
- Power / Thermals（可测时）
- Scaling Efficiency（多节点时）

`E2E@32K` 固定定义：**32,768 input tokens + 32,768 output tokens、Concurrency=1、Cold Cache**，从请求发出到最后一个 token 完整接收。未生成满 32,768 tokens 不得填写成功值。

## 第一套正式 Suite

`suites/qwen38-27b/v1.0/`

第一阶段比较：

- Qwen3.8-27B BF16
- Qwen3.8-27B FP8
- Qwen3.8-27B NVFP4
- 1× GB10
- RTX PRO 6000 96GB
- 后续实际到手的 Mac / 2×GB10 / 其他硬件按同一合同追加

Context 轴：`32K / 128K / 256K / 384K / 512K / 768K / 1M`。

质量与工作测试核心包含：GPQA Diamond、IFBench、HumanEval+、LiveCodeBench、LongBench v2、Needle-in-a-Haystack、NoLiMa，以及固定 exact-token 性能与 32K 长输出稳定性工作负载。

## 仓库结构

```text
docs/        方法论、指标、比较规则、证据等级
hardware/    硬件 registry 与已实测设备 profile
suites/      每个模型/版本的冻结测试套件
datasets/    数据集 manifest 与获取规则（不保存受限原题）
runners/     vLLM / SGLang / llama.cpp / MLX 等 runner
schemas/     结构化结果与环境合同
results/     通过 schema 的正式结构化结果
evidence/    可公开的原始日志、环境快照与校验信息
scripts/     下载、校验、采集、汇总与 README dashboard 生成工具
```

## Evidence Levels

- **A — Fully Reproducible**：完整参数、版本、环境快照、测试数据 hash、原始日志、结构化结果均存在。
- **B — Verified**：关键条件可验证，但少量 A 级要求仍缺失；必须展示证据缺口。
- **C — Community Reference**：第三方论坛/GitHub/社区数据，仅作为外部参考，不与本仓库主实测等权。

详见 `docs/evidence-levels.md`。

## License 与第三方数据

本仓库自有代码和文档按仓库 License 发布；第三方模型、数据集、benchmark 与其题目内容仍受各自许可证/访问条款约束。仓库中的 manifest、下载说明或 hash 不代表重新授权第三方内容。
