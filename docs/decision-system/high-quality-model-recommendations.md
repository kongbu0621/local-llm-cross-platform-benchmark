# 高质量大模型候选推荐与 GB10 / PRO6000 适配（2026-09-03）

> **目标：** 不做“最新模型新闻榜”，而是回答：在 **1×GX10、2×GB10、4×GB10、RTX PRO 6000 96GB** 上，哪些高质量 Coding / Agent / Long-context 模型最值得投入第一方测试时间。
>
> **P0/P1/P2/WATCH 是验证优先级，不是质量总分、速度排行榜或购买顺序。** 外部同型号 GB10 的公开实跑用于降低试错成本，仍不能替代本仓自己的 Quality / Stability / Coding Production Qualification。

## 一页结论

| Priority | Model / Variant | 1×GX10 | 2×GB10 | 4×GB10 | 为什么保留 |
| --- | --- | --- | --- | --- | --- |
| **P0** | **Qwen3.8-27B BF16 / FP8 / NVFP4** | **FIRST-PARTY @32K** | OPEN | OPEN | 当前唯一已有本仓 Formal100 + Hardware Gate 的性能锚点 |
| **P0** | **Qwen3.5-122B-A10B Hybrid INT4+FP8** | **GOOD external @256K** | 无需先扩节点 | OPEN | 单 GB10 成熟、速度高、Coding/Long-context 仍有参考价值 |
| **P0** | **Qwen3.8-Flash-Next RadixArk NVFP4** | **GOOD external，PLE streaming** | **GOOD external，TP2** | OPEN | 单/双 GB10 都已有实跑，是“不买硬件先升级能力”的强候选 |
| **P0** | **DeepSeek-V4-Flash-0731 official mixed checkpoint** | full-resident 不适配；极低比特 P1 | **GOOD external，TP2** | **GOOD external，TP4** | 官方 Coding/Agent 信号强；双 GB10 已实跑到接近 900K prompt |
| **P1 / Classic** | **openai/gpt-oss-120b MXFP4** | **GOOD external** | 通常不需要为了它加节点 | OPEN | 117B/5.1B active、Agent/Tool-use 强、Apache-2.0；但 native 128K |
| **P1** | **GLM-5.3-Flash LibertAIDAI NVFP4** | full-resident 不适配 | **GOOD external，512K profile** | **GOOD external，large-KV** | 2× 已有 440K needle；长上下文证据很直接 |
| **P1** | **GLM-5.3-Flash exact official FP8** | 不适配 | 不适配 full-resident | **CONDITIONAL** | official/derived Variant 必须拆开；不能继承其他 checkpoint 的数字 |
| **P1** | **nvidia/MiniMax-M3-NVFP4** | 不适配 | 250GB 对 2×过紧 | **GOOD external** | 4×已有 262K benchmark + 1M KV/serving；多模态/长上下文价值高 |
| **P2 / NVIDIA Ref** | **Nemotron-3-Super-120B-A12B-NVFP4** | **GOOD external** | 无需先扩节点 | OPEN | NVIDIA-native Agent/Long-context 参考；单 GB10 成熟，但独立 Coding 证据不足以升 P0 |
| **P2** | **MiniMax-M3 community W4A16/GPTQ** | 不适配 | **CONDITIONAL external** | OPEN | 2×可行性路线存在，但激进量化必须单独 Quality Gate |
| **WATCH** | **Kimi-K3 native MXFP4** | native 不适配 | native 不适配 | native 不适配 | Frontier/API/未来大集群参考；当前不构成 GX10 采购触发器 |

## 先冻结 6 条结论

1. **现有 1×GX10 仍有很大的软件/模型升级空间。** Qwen3.5-122B Hybrid、Qwen3.8-Flash-Next NVFP4、gpt-oss-120b、Nemotron 3 Super 都已有单 GB10 公开路线，所以“第二台很有价值”不等于“现在必须买第二台”。
2. **2×GB10 已经是现实的大模型平台，不再只是容量推理。** DeepSeek V4 official、Qwen Flash Next NVFP4、GLM NVFP4 都有同硬件可复现实跑。
3. **4×GB10 的理由应是更大的 KV / Context / 并发 / 模型放置，而不是幻想 Decode 线性翻倍。** MiniMax NVFP4、GLM large-KV、DeepSeek TP4 的价值都更接近“平台 envelope”。
4. **Classic 不能因为不是最新就自动淘汰。** Qwen3.5-122B 和 gpt-oss-120b 都应继续充当成熟参考；前者更符合 256K+ Coding，后者是很好的 Agent/Tool-use 128K reference。
5. **Variant 是基本推荐单位。** official FP8、NVFP4、INT4、W4A16、streaming/expert-pruned 不能共享速度、质量或 Context 证据。
6. **Context 必须拆证据层。** `configured/model length != KV allocated != actual prompt processed != retrieval/needle validated != coding production qualified`。

---

# Evidence tiers

| Evidence | 可以证明什么 | 不能证明什么 |
| --- | --- | --- |
| **FIRST_PARTY_MEASURED** | 本仓目标硬件、固定合同真实测过 | 没测的 Context / Quality / Production 仍不能外推 |
| **REPRODUCIBLE_EXTERNAL** | 同 GB10/Spark/GX10 有公开版本、recipe、measured result | 不能自动成为本仓 Qualification；不同 workload 的 tok/s 不能直接排名 |
| **STRONG_EXTERNAL / VENDOR_CLAIM** | 模型质量、官方 benchmark、架构/平台信号 | 不能证明你的目标 topology 已适配 |
| **UNKNOWN / capacity only** | 只用于筛选、排除明显不可能组合 | 不能证明 Runtime / KV / TTFT / Decode / Quality / Stability |

固定边界：

```text
external same-hardware PASS != first-party PASS
runtime PASS != quality PASS
quality PASS != production PASS
weight fits != target context fits
headline tok/s across different contracts != ranking
```

---

# Context Evidence Matrix

这是大项目 Agent 最容易被误读的一层。下面专门把“服务器能开到多少”与“真正喂过多少”分开。

| Model / Variant | Topology | Configured / serving envelope | Actual prompt / retrieval evidence | 当前能成立的结论 |
| --- | --- | --- | --- | --- |
| Qwen3.8-27B NVFP4 | 1×GX10 | 本仓 32K+256 | **32,768 input first-party Formal100** | 32K 已测；128K+ OPEN |
| Qwen3.5-122B Hybrid | 1×GB10 | 256K public serving | 未把 full-256K deep prompt 当作本仓证据 | 成熟 256K external candidate |
| Qwen3.8-Flash-Next RadixArk NVFP4 | 1×GB10 | 262K | headline speed 多为短 prompt | 262K serving capability，不等于 262K 性能曲线 |
| Qwen3.8-Flash-Next RadixArk NVFP4 | 2×GB10 | 262K soak；另有 1M serving profile | 深 prompt / retrieval 仍需统一合同 | 2× serving 很成熟，1M Coding PASS 未成立 |
| **DeepSeek-V4-Flash-0731 official** | **2×GB10** | **1M model length / KV** | **公开 sweep 接受 899,994-token prompt**；另有 131K 详细 prefill/decode | 目前最强的 2×GB10 深输入外部证据之一；仍缺本仓 Quality/Coding Production |
| **GLM-5.3-Flash LibertAI NVFP4** | **2×GB10** | **512K standing profile** | **440K-token needle byte-exact** | 对 384K/512K Repo Agent 很有直接参考价值 |
| MiniMax-M3 NVIDIA NVFP4 | 4×GB10 | 262K benchmark + 1M KV/serving | 1M deep-prompt quality 未统一确认 | 4×大 KV/1M 平台候选，不等于 1M Coding PASS |
| gpt-oss-120b | 1×GB10 | **native 128K** | 公开长 prompt / coding-agent；本页只保留 16K measured-depth reference | Classic Agent reference；不满足 384K/512K 主目标 |
| Nemotron 3 Super NVFP4 | 1×GB10 | 131K external profile；官方 up to 1M | 外部报告稳定到约 100K depth | 长上下文参考，但不能把 vendor 1M claim 写成 1M deep-prompt PASS |
| Kimi-K3 native | 当前 fleet | 官方 1M | native checkpoint 无法在当前 1×/2×/4× full-resident | WATCH / API / future cluster |

机器 Registry 现在也保存 `hardware_evidence_by_topology` 和 `context_evidence_by_topology`，避免只靠 Markdown 记住这些边界。

---

# 1×GX10：先把现有机器榨透

## P0-A — Qwen3.8-27B：完成本仓第一方闭环

已有 BF16 / FP8 / NVFP4 Formal100、32K+256 warm C=1、NVFP4 Hardware Gate。下一步：

```text
Quality Gate
→ 128K
→ 256K
→ 384K
→ 512K
→ Pure Prefill / Memory / KV
→ Real Coding Tool Loop
```

它的最大价值是成为完全属于本仓的一方标准尺。

## P0-B — Qwen3.5-122B-A10B Hybrid INT4+FP8

公开单 GB10 路线已做到 256K，并有约 52–59 tok/s 的不同 benchmark/profile。官方 122B/10B-active 模型 Coding / Long-context 信号仍强。

来源：
- https://huggingface.co/Qwen/Qwen3.5-122B-A10B
- https://github.com/albond/DGX_Spark_Qwen3.5-122B-A10B-AR-INT4
- https://github.com/Entrpi/qwen3.5-122B-A10B-on-spark

**定位：** Mature Classic + Production Sweet Spot；非常适合做“单 GX10 大模型 Coding baseline”。

## P0-C — Qwen3.8-Flash-Next RadixArk NVFP4

约 135GB；单 GB10 通过 PLE NVMe streaming/mmap 控制 resident footprint，公开 262K 服务与多套性能/quality probe；2×TP2 也已经成熟。

来源：
- https://huggingface.co/RadixArk/Qwen3.8-Flash-Next-NVFP4
- https://github.com/maci0/qwen3.8-flash-next-spark
- https://huggingface.co/sayyidfareed/Qwen3.8-Flash-Next-Code-Turbo-Spark

**定位：** 现有单机最值得复现的“大模型能力跃迁”候选之一。

## P1 — openai/gpt-oss-120b MXFP4

OpenAI 官方：117B total / 5.1B active、native 128K、Apache-2.0、MXFP4 MoE，强调 reasoning、tool use、agentic capabilities，并要求 Harmony 格式。公开单 Spark 路线已有约 37 tok/s E2E 的严谨测量，也有更高 decode-only profile；不能混为一个数字。

来源：
- https://openai.com/index/introducing-gpt-oss/
- https://huggingface.co/openai/gpt-oss-120b
- https://github.com/mani-mal/spark-coder-bench
- https://github.com/christopherowen/spark-vllm-mxfp4-docker

**定位：** Agent/Tool-use Classic Reference。因为 native 128K，它不是你 384K/512K 大仓库主 Agent 的最终候选，但仍值得作为质量/工具链参考。

## P1 — DeepSeek V4 single-node ultra-low-bit / streaming

公开 2-bit expert + FP4 recovery 等路线可以在单 GB10 上跑到 256K 左右，也有 1M KV streaming 试验，但速度和 harder-reasoning 质量折衷更明显。

来源：
- https://github.com/lrozewicz/vLLM-Moet-GB10
- https://github.com/kandotrun/dgx-spark-deepseek-v4-flash

**定位：** 实验候选，不是当前单节点 Main Coding 首选。

## P2 — Nemotron-3-Super-120B-A12B-NVFP4

NVIDIA 官方：120B total / 12B active、LatentMoE + Mamba/Attention + MTP、NVFP4，模型卡写 up to 1M，最适合 Agent/RAG/long-context；官方明确 1×DGX Spark 是最低目标之一。公开单 Spark benchmark 约 23–49 tok/s（不同 runtime/profile），一个公开 131K profile 报告性能稳定到约 100K context。

来源：
- https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-NVFP4
- https://research.nvidia.com/labs/nemotron/Nemotron-3-Super/
- https://github.com/airawatraj/dgx-spark-nemotron-super-agent
- https://github.com/rmagur1203/vllm-dgx-spark

**定位：** NVIDIA-native Agent/Long-context Reference。保留 P2，是因为目前独立 GB10 Coding 对照还不足以把它排在 Qwen3.5 / 当前 P0 路线之前。

---

# 2×GB10：真正的大模型平台

## P0-1 — DeepSeek-V4-Flash-0731 official mixed checkpoint

之前用 `304B × FP8 ≈ 304GB` 推断 2×放不下，是错误的 checkpoint 语义。实际官方 release 约 167GB，config 包含 FP4 experts + FP8 quantization path。

公开 2×GB10 证据已经包括：TP2/RoCE、DSpark、1M model length；MiaAI-Lab 的公开 sweep 甚至记录 **899,994 prompt tokens** 被接受，TTFT 约 1028.85s、有效 prefill 约 874.8 tok/s。另一路 131K 测试给出更完整的 TTFT/prefill/decode 曲线。

来源：
- https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731
- https://github.com/Deep-AI-Evo/deepseek-v4-flash-2x-dgx-spark
- https://github.com/MiaAI-Lab/DeepSeek-v4-Flash-DSpark-2x-DGX-Spark
- https://github.com/Reederey87/dgx-spark-2x-deepseek-v4-flash

**当前判断：** 2×GB10 Main Coding / Architect / Repo-scale **P0 direct candidate**。但 900K actual prompt 仍不等于 900K Coding quality PASS。

## P0-2 — Qwen3.8-Flash-Next RadixArk NVFP4

2×公开 TP2 / RoCE、262K、30-minute soak、单流约 41–42 tok/s，8-stream aggregate 约 153 tok/s；另有 1M serving profile。不同合同不能和 DeepSeek 数字直接排名。

**当前判断：** Fast Main Coding / Repo Agent P0，值得和 DeepSeek 用本仓相同 Formal/Quality/Context/Coding Loop 横比。

## P1 — GLM-5.3-Flash LibertAIDAI NVFP4

2×路线已经从早期 262K 推进到 **512K standing config**：FP8 KV + MTP，约 24–30 tok/s decode（该外部合同），并给出 **440K-token needle byte-exact retrieval**。

来源：
- https://huggingface.co/LibertAIDAI/GLM-5.3-Flash-NVFP4
- https://github.com/tonyd2wild/GLM-5.3-Flash-NVFP4-2x-DGX-Spark
- https://forums.developer.nvidia.com/t/glm-5-3-flash-nvfp4-on-2x-dgx-spark-vllm-tp-2-docker-compose/381541

**当前判断：** 对你真正关心的 384K/512K Repo Agent，这是一条非常值得第一方复现的外部路线。

## P2 — MiniMax-M3 W4A16/GPTQ

2×已有 third-party W4A16/GPTQ + speculative serving 路线，但量化更激进，Quality 未证明，因此排在 DeepSeek/Qwen/GLM 后面。

---

# 4×GB10：平台 envelope，而不是简单加速器

## P1 — nvidia/MiniMax-M3-NVFP4

NVIDIA ModelOpt checkpoint 约 250GB。公开 4×GB10 TP4/DSpark 已有 262K benchmark、702/702 successes、0 server/OOM/NVRM errors，并有单独 1M KV/serving 路线。

来源：
- https://huggingface.co/nvidia/MiniMax-M3-NVFP4
- https://github.com/mpfaffenberger/MiniMax-M3-NVFP4-DSpark-vLLM-4x-DGX-Spark
- https://forums.developer.nvidia.com/t/minimax-m3-nvfp4-1m-context-31-tok-s-native-vision-4x-dgx-spark-gb10/376979

**当前判断：** 4×GB10 Long-context / Multimodal Coding P1；1M KV 仍不能冒充 1M deep-prompt quality。

## GLM / DeepSeek on 4×

GLM LibertAI NVFP4 已有 large-KV/1M 路线，DeepSeek official 也已有更大的 KV/concurrency/production envelope。`zai-org exact official FP8` 与 derived/uncensored/LibertAI variants 继续分开，不能串数字。

因此 4×升级必须由下面的 Trigger 驱动：

```text
2× 第一方 Coding Production workload
→ 证明出现不可由 model/runtime/context strategy 替代的容量/KV/并发/角色放置瓶颈
→ 4×同合同对照
→ Scaling Efficiency + Useful Engineering Work / Hour
→ 才决定购买
```

---

# RTX PRO 6000 96GB

当前最有价值的角色仍是：

1. Qwen3.8-27B BF16 / FP8 / NVFP4 的 CUDA 高质量对照；
2. 中等规模高质量模型的单卡 reference；
3. 大模型 aggressive low-bit/offload 的独立实验平台；
4. 不把“能靠极低比特塞进 96GB”自动解释为“适合主 Coding Agent”。

---

# 推荐与购买的最终规则

每个候选必须依次经过：

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

硬件购买额外要求：

```text
现有机器 / runtime / model / quant / context strategy / role reassignment
无法解决真实 Hard Gate
→ Upgrade Trigger 成立
→ 才允许 Hardware ACTION
```

所以当前模型情报给出的不是“买机器清单”，而是**把昂贵第一方测试集中到已经有外部证据、又真正匹配你 384K/512K 大项目目标的路线**。

机器可读 Registry：[`model-intelligence/registry.json`](../../model-intelligence/registry.json)。
