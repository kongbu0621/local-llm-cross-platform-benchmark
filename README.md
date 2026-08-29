# Local LLM Cross-Platform Benchmark

一个长期维护、可复现、以真实硬件实测为核心的本地大模型（Local LLM）跨平台能力数据库。

本仓库不只比较 `tokens/s`。目标是记录同一模型在不同真实硬件、操作系统、推理栈、量化、上下文长度和工作负载下的 **质量、性能、内存、稳定性、效率与可复现证据**。

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
results/     通过 schema 的正式结果
evidence/    可公开的原始日志、环境快照与校验信息
scripts/     下载、校验、采集与汇总工具
```

## Evidence Levels

- **A — Fully Reproducible**：完整参数、版本、环境快照、测试数据 hash、原始日志、结构化结果均存在。
- **B — Verified**：关键条件可验证，但少量原始证据缺失。
- **C — Community Reference**：第三方论坛/GitHub/社区数据，仅作为外部参考，不与本仓库主实测等权。

详见 `docs/evidence-levels.md`。

## License 与第三方数据

本仓库自有代码和文档按仓库 License 发布；第三方模型、数据集、benchmark 与其题目内容仍受各自许可证/访问条款约束。仓库中的 manifest、下载说明或 hash 不代表重新授权第三方内容。
