# 高质量大模型候选推荐与 GB10 / PRO6000 适配（2026-09-03）

> **目标：** 不是列“最火模型名字”，而是回答：在你真正拥有/考虑的 **1×GX10、2×GB10、4×GB10、RTX PRO 6000 96GB** 上，哪些高质量 Coding / Agent / Long-context 模型最值得先投入测试时间。
>
> **重要：** 这里的 P0/P1/P2 是“第一方验证优先级”，不是质量总分、速度排行榜或购买顺序。外部同型号 GB10 的公开实跑用于降低试错成本，仍不能代替本仓自己的 Quality / Stability / Coding Production Qualification。

## 一页结论

| Priority | Model / Variant | 为什么现在值得测 | 1×GX10 | 2×GB10 | 4×GB10 | 最适合的候选角色 |
| --- | --- | --- | --- | --- | --- | --- |
| **P0** | **Qwen3.8-27B NVFP4 / FP8 / BF16** | 本仓已有 Formal100 + Hardware Gate，是唯一第一方性能锚点 | **FIRST-PARTY** | OPEN | OPEN | Quality reference / Fast Worker baseline |
| **P0** | **Qwen3.5-122B-A10B Hybrid INT4+FP8** | 成熟单-GB10 路线；256K；公开同硬件约 52–59 tok/s；官方 Coding/Long-context 能力仍强 | **GOOD external** | 不需要先加节点 | OPEN | Mature single-node Coding / Agent baseline |
| **P0** | **Qwen3.8-Flash-Next · RadixArk NVFP4** | 135GB；单 GB10 PLE streaming + 双 GB10 TP2 已实跑；有 checkpoint-specific quality probes | **GOOD external** | **GOOD external** | OPEN | Fast Main Coding / Repo / Long-context |
| **P0** | **DeepSeek-V4-Flash-0731 official mixed checkpoint** | 官方 checkpoint ~167GB；Coding/Agent 信号强；2×GB10 TP2 / 1M 已有实跑 | full-resident 不适合 | **GOOD external** | **GOOD external** | Main Coding / Architect / Repo-scale |
| **P1** | **GLM-5.3-Flash · LibertAIDAI NVFP4** | ~181GiB；2×GB10 / 262K 已实跑；320B/18B-active、长上下文效率路线 | 不适合 full-resident | **GOOD external** | **GOOD external** | Coding / Repo / Long-context |
| **P1** | **nvidia/MiniMax-M3-NVFP4** | NVIDIA ModelOpt 250GB checkpoint；4×GB10 已有 262K/1M 与完整 serving 验证 | 不适合 | 过紧，不作为首选 | **GOOD external** | Multimodal / Long-context / Coding Agent |
| **P2** | **MiniMax-M3 W4A16 / other third-party low-bit** | 2×GB10 已存在约 36 tok/s 路线，但量化质量必须单独 Gate | 不适合 | **CONDITIONAL external** | OPEN | 2× MiniMax feasibility |
| **WATCH** | **Kimi-K3 native MXFP4** | Frontier 2.8T/104B-active、1M；质量参考价值高 | native 不适配 | native 不适配 | native 不适配 | API / future large-cluster reference |

### 当前真正应该记住的 4 个结论

1. **已有 1×GX10 并不等于必须马上买第二台。** 单节点现在至少有 Qwen3.8-27B、Qwen3.5-122B Hybrid、Qwen3.8-Flash-Next NVFP4，甚至 DeepSeek V4 的更激进流式/超低比特路线可先验证。
2. **2×GB10 已经从“理论容量”升级为真实平台。** DeepSeek V4 official、Qwen Flash Next NVFP4、GLM NVFP4 都已有同 GB10 可复现部署；下一步应该做同合同第一方横比，而不是再讨论“能不能启动”。
3. **4×GB10 的真正价值是更高质量/更大 KV/更大并发/1M，而不是简单把 2× 的 tok/s 乘二。** MiniMax-M3 NVFP4、GLM 1M、DeepSeek TP4 都已有外部先例，但是否值得你购买仍要靠 L3 Coding Production 数据。
4. **模型新不等于更适合。** Qwen3.5-122B-A10B 不是最新一代，却因为单 GB10 成熟度、256K 与 Coding 质量信号，依然是非常高价值的 Classic/Sweet-Spot 对照。

---

# 证据分四级

| Evidence tier | 能证明什么 | 不能证明什么 |
| --- | --- | --- |
| **First-party measured** | 本仓目标硬件、固定合同真实测过 | 没测的 Context / Quality / Production 仍不能外推 |
| **Reproducible same-hardware external** | 同 GB10 / Spark / GX10 有公开 recipe、版本和 measured result | 不能直接成为本仓 Qualification；不同 workload 的 tok/s 不能直接排名 |
| **Official/vendor model evidence** | 架构、官方 benchmark、context claim、runtime support | 不能证明你的 GB10 已适配 |
| **Capacity arithmetic only** | 排除明显放不下、筛选值得尝试的组合 | 不能证明 Runtime / KV / TTFT / Decode / Quality / Stability |

固定边界：

```text
external same-hardware PASS != first-party PASS
runtime PASS != quality PASS
quality PASS != production PASS
weight fits != target context fits
headline tok/s across different contracts != ranking
```

---

# 1×GX10：优先把现有机器榨透

## P0-A — Qwen3.8-27B：完成本仓第一方基线

已有：BF16 / FP8 / NVFP4 Formal100、32K+256 warm C=1、NVFP4 Hardware Gate。

下一步：

```text
Quality Gate
→ 128K
→ 256K
→ 384K
→ 512K
→ Pure Prefill / Memory / KV
→ Real Coding Tool Loop
```

这条线的价值不是“最炫”，而是得到一条完全属于自己的可复现基准。

## P0-B — Qwen3.5-122B-A10B Hybrid INT4+FP8：成熟 Classic/Sweet Spot

这是本轮深审后补回来的**经典但仍很能打**的路线。

官方 Qwen3.5-122B-A10B：122B total / 10B active，native 262K，可扩到约 1M；官方公开 Coding / Long-context benchmark 仍很强。

公开单 DGX Spark/GX10 Hybrid INT4+FP8 路线已经做到：

- 256K context；
- 公开复现实测 cross-prompt decode 约 **52 tok/s**；
- 后续 DFlash 路线约 **59 tok/s e2e decode**；
- 长期版本演进、benchmark harness、失败项、质量保护策略都比较成熟。

公开来源：

- https://huggingface.co/Qwen/Qwen3.5-122B-A10B
- https://github.com/albond/DGX_Spark_Qwen3.5-122B-A10B-AR-INT4
- https://github.com/Entrpi/qwen3.5-122B-A10B-on-spark

**意义：** 它应该作为“单 GX10 成熟 Coding Agent 能做到什么”的外部参考锚，而不是因为 Qwen3.8 已发布就自动淘汰。

## P0-C — Qwen3.8-Flash-Next RadixArk NVFP4：单节点能力跃迁候选

RadixArk checkpoint 约 135GB：routed experts NVFP4、PLE FP8、敏感路径高精度。公开单 GB10 recipe 通过 PLE 从 NVMe streaming/mmap 把 resident footprint 控制到单节点可运行范围。

公开同硬件证据包括：

- 262K context；
- 单流大约 21–31 tok/s（不同 serving profile）；
- 另一个面向 coding 的单 GX10 profile 报告 mixed-code median ~32.4 tok/s，并给出 HumanEval / HumanEval+ Mini probe。

来源：

- https://huggingface.co/RadixArk/Qwen3.8-Flash-Next-NVFP4
- https://github.com/maci0/qwen3.8-flash-next-spark
- https://huggingface.co/sayyidfareed/Qwen3.8-Flash-Next-Code-Turbo-Spark

这些数字和本仓 9.081 tok/s **不能直接比较**，因为 prompt/output/speculative-decoding/runtime 合同不同；其价值是证明“现有单 GX10 有一条值得复现的大模型路线”。

## P1 — DeepSeek V4 single-node ultra-low-bit / streaming

公开单 GB10 路线也已经存在，例如：

- vLLM-Moet 2-bit expert planes + FP4 quality recovery：约 9.8 tok/s、256K；
- Colibri MXFP4 streaming-expert：完整 1M KV 能力但只有约 4–5 tok/s；
- 一些 agent-serving 复现报告显示普通任务接近云端，但 harder reasoning 会出现可见质量损失。

来源：

- https://github.com/lrozewicz/vLLM-Moet-GB10
- https://huggingface.co/Kanposer/DeepSeek-V4-Flash-0731-speedy-colibri-mxfp4
- https://github.com/kandotrun/dgx-spark-deepseek-v4-flash

**所以单节点 DeepSeek 是 P1 实验候选，不是当前首选生产路线：速度/量化质量代价比 Qwen 单节点路线更明显。**

---

# 2×GB10：已经进入真正的大模型平台区间

## P0-1 — DeepSeek-V4-Flash-0731 official mixed checkpoint

这是前面最大的一次纠错。

错误旧推导：

```text
304B × FP8 ≈ 304GB
→ 2×256GB 放不下 official checkpoint
```

实际官方 release 约 **167GB**；config 同时有 `expert_dtype=fp4` 和 FP8 quantization path，因此不是“纯 304GB FP8 image”。官方 max position embeddings = 1,048,576，并带 DSpark speculative module。

公开 2×GB10 复现实测已经包括：TP2 / RoCE、1M model length、DSpark、真实 coding workload。不同公开 recipe 报告的 decode 数值差异很大（约 30–80+ tok/s 区间，配置/版本/contract 不同），因此**本仓必须重跑统一合同，不能挑最高数字当结论。**

来源：

- https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731
- https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731/blob/main/config.json
- https://github.com/Deep-AI-Evo/deepseek-v4-flash-2x-dgx-spark
- https://github.com/Reederey87/dgx-spark-2x-deepseek-v4-flash

当前结论：**2×GB10 DeepSeek V4 official = P0 direct candidate。**

## P0-2 — Qwen3.8-Flash-Next RadixArk NVFP4

公开 2×Spark recipe：TP2 / RoCE、262K、30-minute soak、单流约 41–42 tok/s，8-stream aggregate ~153 tok/s，并使用 NEXTN/MTP speculative decoding。

来源：

- https://huggingface.co/pocharlies/Qwen3.8-Flash-Next
- https://github.com/maci0/qwen3.8-flash-next-spark

当前结论：**高效率 Coding / Repo Agent P0，值得和 DeepSeek 用同一 suite 比。**

## P1 — GLM-5.3-Flash LibertAIDAI NVFP4

官方 GLM：320B total / 18B active，sparse + linear attention，面向 coding / agentic / multimodal / long context。

LibertAIDAI NVFP4-A16 variant：约 181GiB，主要把 routed-expert FFN 压成 NVFP4，attention/vision/shared expert/MTP/embedding 保留高精度，并公开 quantization provenance / round-trip checks。

2×GB10 已有 TP2 / 262K / MTP 公开实跑，约 21.8 tok/s decode（其测试合同）。

来源：

- https://huggingface.co/LibertAIDAI/GLM-5.3-Flash-NVFP4
- https://github.com/tonyd2wild/GLM-5.3-Flash-NVFP4-2x-DGX-Spark
- https://forums.developer.nvidia.com/t/glm-5-3-flash-nvfp4-on-2x-dgx-spark-vllm-tp-2-docker-compose/381541

## P2/P1 — MiniMax-M3 W4A16/GPTQ 等 third-party 2×路线

2×GB10 已有 third-party W4A16/GPTQ + EAGLE3 / NVFP4-KV 路线，公开约 31–36 tok/s、~196K/262K 不同 profile。

来源：

- https://forums.developer.nvidia.com/t/minimax-m3-w4a16-gptq-2xgb10-deployment-36-t-s-fp8-nvfp4-kvarn-eagle-3/375595

因为量化层级更激进、当前缺本仓质量验证，它排在 DeepSeek/Qwen/GLM 后面。

---

# 4×GB10：更高质量 / 更大 KV / 更大并发，而非“2×速度翻倍”

## P1 — nvidia/MiniMax-M3-NVFP4

这也是本轮新抓到的重要遗漏。

NVIDIA 官方 ModelOpt checkpoint：`nvidia/MiniMax-M3-NVFP4`，约 **250GB**。公开 4×GB10 方案已经验证：

- native multi-node vLLM TP4；
- NVIDIA DSpark；
- 262K serving ceiling 的完整 benchmark；
- 702/702 benchmark requests、0 server/OOM/NVRM errors；
- C1 decode ~39 tok/s、100K depth C1 ~29.6 tok/s；
- 另一路公开实现把 4×GB10 推到 1M KV，并报告约 31 tok/s。

来源：

- https://huggingface.co/nvidia/MiniMax-M3-NVFP4
- https://github.com/mpfaffenberger/MiniMax-M3-NVFP4-DSpark-vLLM-4x-DGX-Spark
- https://forums.developer.nvidia.com/t/minimax-m3-nvfp4-1m-context-31-tok-s-native-vision-4x-dgx-spark-gb10/376979

**这使 MiniMax-M3 从“纯容量候选”升级为 4×GB10 P1 真实平台候选。** 但 NVIDIA NVFP4 variant 的 Coding Quality 仍要单独对官方 base 做质量差异 Gate。

## GLM-5.3-Flash 的 4×路线：注意 Variant

公开 4×GB10 / 1M 证据很强，但大多数清晰可审计的运行数据落在：

- LibertAIDAI NVFP4；或
- derived/uncensored FP8 checkpoint。

因此不能把这些数字直接写成 `zai-org official FP8 exact checkpoint = GOOD`。

更准确的结论：

```text
GLM family @4xGB10 = strong reproducible external platform evidence
zai-org official FP8 exact variant = CONDITIONAL until exact-variant run is pinned
```

来源：

- https://github.com/tonyd2wild/GLM-5.3-Flash-NVFP4-1M-KV-4x-DGX-Spark
- https://github.com/alexellis/glm-5.3-flash-4x-dgx-spark-switchless
- https://github.com/Wpnx330/GLM-5.3-Flash-FP8-4x-DGX-Spark

## DeepSeek V4 4×

4×GB10 也已有 1M、C8、restart/retrieval 等更完整外部资格案例。它证明 4×可以提高 KV/concurrency/production envelope，但是否比 2×对你的实际项目更值钱，仍必须看同合同 scaling 和 Useful Engineering Work / Hour。

来源：

- https://forums.developer.nvidia.com/t/4x-gb10-deepseek-v4-flash-qualified-tp4-k5-c8-production-results/380041

---

# Kimi-K3：为什么仍是 WATCH

Native Kimi-K3：2.8T total / 104B active、1M、native MXFP4。当前 native checkpoint 远超 4×GB10 聚合内存。

确实已经出现：

- 单 GB10 expert-streaming（约 0.4 tok/s）；
- 4×GB10 IQ1/expert-pruned 路线（约 5–8 tok/s）；
- 512GB REAP expert-pruned builds。

这些证明“技术上可以压进来”，但压缩/专家裁剪和速度代价都很大，目前没有足够理由把它排在 DeepSeek/Qwen/GLM/MiniMax 之前作为你的本地生产候选。

来源：

- https://huggingface.co/Kanposer/Kimi-K3-speedy-colibri-mxfp4
- https://github.com/vcruz305/kimi-k3-neuron-tp4-vllm-recipe
- https://huggingface.co/hellohazime/Kimi-K3-REAP-512GB-GGUF

所以：**Kimi-K3 仍是 Quality/API/Future-cluster Reference，不是当前采购 Trigger。**

---

# PRO6000 96GB

当前更适合：

- Qwen3.8-27B BF16 / FP8 / NVFP4 第一方质量对照；
- 中等规模 CUDA 高质量模型；
- 超大模型的 aggressive low-bit/offload 独立实验。

Qwen Flash Next NVFP4 135GB、DeepSeek official ~167GB、GLM NVFP4 ~181GiB、MiniMax NVIDIA NVFP4 250GB 都超过 96GB full-resident。即使 offload 能启动，也必须评价 TTFT/等待成本，不得因为“能跑”就标成高质量 Main Agent。

---

# 现在真正建议的测试顺序

## 已有 1×GX10

```text
P0  Qwen3.8-27B：Quality + 128K→512K（第一方基线）
P0  Qwen3.5-122B-A10B Hybrid：成熟单节点 Coding baseline 复现
P0  Qwen3.8-Flash-Next RadixArk NVFP4：PLE streaming / 262K 复现
P1  DeepSeek-V4 single-node quantized/streaming：质量-速度 tradeoff 探索
```

## 2×GB10

```text
P0  DeepSeek-V4-Flash-0731 official mixed checkpoint
P0  Qwen3.8-Flash-Next RadixArk NVFP4
P1  GLM-5.3-Flash LibertAIDAI NVFP4
P2/P1 MiniMax-M3 third-party W4A16/GPTQ（先做质量 Gate）
```

## 4×GB10

```text
先回答：2×到底哪里不够？

P1  nvidia/MiniMax-M3-NVFP4
P1  GLM-5.3 family 1M / larger-KV routes
P1  DeepSeek-V4 TP4 concurrency / KV / production envelope
P2  Kimi-K3 heavily-pruned experiments only if there is a specific reason
```

---

# 统一资格链

```text
CANDIDATE
→ Runtime Gate
→ Formal5
→ Formal100
→ Quality Gate
→ Context-band Gate
→ Agent Workload Fitness
→ Real Coding Tool Loop
→ Coding Production Fitness
→ Production Recommendation
```

**外部证据的价值是少走弯路，不是替你完成第一方验收。**

机器 Registry：[`model-intelligence/registry.json`](../../model-intelligence/registry.json)。
