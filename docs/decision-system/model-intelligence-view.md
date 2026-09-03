# Model Intelligence — 高质量模型、Variant、Context 与硬件证据一页看懂

> **给人看的入口。** 机器 Registry 在 `model-intelligence/registry.json`。这页回答四件事：**谁值得测、在哪套硬件上测、Context 证据到底到哪一层、证据是一方实测还是外部线索。**

完整分析：[高质量大模型候选推荐与 GB10 / PRO6000 适配](high-quality-model-recommendations.md)。

## 当前 shortlist

| Priority | Model / Variant | 1×GX10 | 2×GB10 | 4×GB10 | Evidence | 本仓 Quality | 角色边界 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **P0** | Qwen3.8-27B BF16 / FP8 / NVFP4 | **FIRST-PARTY @32K** | OPEN | OPEN | **FIRST_PARTY_MEASURED** | OPEN | 当前一方性能锚点；不是长上下文主 Agent 结论 |
| **P0** | Qwen3.5-122B-A10B Hybrid INT4+FP8 | **GOOD @256K external** | OPEN | OPEN | **REPRODUCIBLE_EXTERNAL** | OPEN | Mature Classic / Coding / Agent baseline |
| **P0** | Qwen3.8-Flash-Next RadixArk NVFP4 | **GOOD PLE-streaming external** | **GOOD TP2 external** | OPEN | **REPRODUCIBLE_EXTERNAL** | OPEN | Fast Main Coding / Repo / Long Context candidate |
| **P0** | DeepSeek-V4-Flash-0731 official mixed checkpoint | single full-resident 不适配；量化 P1 | **GOOD TP2 external** | **GOOD TP4 external** | **REPRODUCIBLE_EXTERNAL** | OPEN | Main Coding / Architect / Repo-scale candidate |
| **P1 / Classic** | **openai/gpt-oss-120b MXFP4** | **GOOD external** | 通常没必要为了它加节点 | OPEN | **REPRODUCIBLE_EXTERNAL** | OPEN | 强 Agent/Tool/Reasoning reference；native 128K 限制 repo-scale 主 Agent |
| **P1** | GLM-5.3-Flash LibertAIDAI NVFP4 | 不适配 | **GOOD TP2 external** | **GOOD TP4 external** | **REPRODUCIBLE_EXTERNAL** | OPEN | Coding / Repo / Long Context candidate |
| **P1** | GLM-5.3-Flash exact official FP8 | 不适配 | 不适配 full-resident | **CONDITIONAL** | STRONG_EXTERNAL；exact variant 未锁定同合同实测 | OPEN | 4× high-quality reference candidate |
| **P1** | nvidia/MiniMax-M3-NVFP4 | 不适配 | 过紧/CONDITIONAL | **GOOD TP4 external** | **REPRODUCIBLE_EXTERNAL** | OPEN | Multimodal / Long-context / Coding Agent candidate |
| **P2 / NVIDIA Ref** | **Nemotron-3-Super-120B-A12B-NVFP4** | **GOOD external** | 不需要先扩节点 | OPEN | **REPRODUCIBLE_EXTERNAL** | OPEN | NVIDIA-native long-context/agent reference；独立 Coding 证据不足以升到 P0 |
| **P2** | MiniMax-M3 community W4A16/GPTQ | 不适配 | CONDITIONAL external | OPEN | REPRODUCIBLE_EXTERNAL hardware；quality UNKNOWN | OPEN | 2× MiniMax feasibility only |
| **WATCH** | Kimi-K3 native MXFP4 | native 不适配 | native 不适配 | native 不适配 | Vendor/capacity | OPEN | API / future large-cluster quality reference |

### 为什么补回 gpt-oss-120b 与 Nemotron 3 Super

`gpt-oss-120b` 是 117B total / 5.1B active、native 128K、Apache-2.0 的经典 open-weight Agent/Reasoning 模型。公开单 GB10 路线已经有约 27–40 tok/s 的不同 serving 结果，也有真实 Coding Agent/SWE-bench 类实验。它的价值是 **Agent/Tool-use Classic Reference**，但 native 128K 使它不适合作为你 384K/512K 主仓库 Agent 的最终答案。

`Nemotron-3-Super-120B-A12B-NVFP4` 则是 NVIDIA-native 的 120B/12B-active 长上下文 Agent 参考，单 GB10 已有稳定 23 tok/s 左右的可复现实跑，并有长期 Agent 使用记录。但独立 GB10 Coding 比较并没有给出足够证据把它排在 Qwen3.5 或当前 P0 路线之前，所以只保留 **P2 / NVIDIA Reference**，而不是为了“英伟达官方”抬高排名。

---

## Context Evidence Matrix — 配置 1M 不等于真正测过 1M

这是这轮审计新增的硬边界。以后必须至少区分：

```text
Configured / Model Length
!= KV Pool Allocated
!= Prompt Actually Processed
!= Retrieval / Needle Validated
!= Coding Production Qualified
```

| Model / Variant | Topology | Configured / serving envelope | 已明确看到的 prompt-depth / retrieval 证据 | 现在能说什么 |
| --- | --- | --- | --- | --- |
| Qwen3.8-27B NVFP4 | 1×GX10 | 本仓当前正式结果 32K+256 | **32,768 input Formal100 first-party** | 32K 已测；128K+ 仍 OPEN |
| Qwen3.5-122B Hybrid | 1×GB10 | 256K public serving support | 公开路线证明 256K 支持，但本仓尚未复现实测 256K 大项目负载 | Mature 256K external candidate，不等于本仓 256K PASS |
| Qwen3.8-Flash-Next RadixArk NVFP4 | 1×GB10 | 262K native serving | 单节点公开 benchmark 多数是短 prompt；262K 是 server capability | 262K capability 有外部证据，不能把短 prompt tok/s 当 262K 性能 |
| Qwen3.8-Flash-Next RadixArk NVFP4 | 2×GB10 | 262K 已 soak；另有 1M serving profile | 30-minute soak/并发实跑；1M serving 已有公开 recipe，但深 prompt 质量合同仍需单独核 | 2×路线非常成熟，1M 不能直接视作 Coding PASS |
| DeepSeek-V4-Flash-0731 official | 2×GB10 | **1M model length / large KV pool** | 一个严格 recipe 明确测到 cold **131K prefill**；另一路说明 500K+ decode depth 仍需补 | 1M serving capability 很强，但“1M 深输入性能/质量”仍不能偷换 |
| GLM-5.3-Flash LibertAIDAI NVFP4 | 2×GB10 | 512K standing profile 已公开 | **440K-token needle byte-exact** 的公开验证；512K decode 约 24–30 tok/s 属该外部合同 | 目前 2×GB10 中对 384K/512K 最直接的外部长上下文证据之一 |
| nvidia/MiniMax-M3-NVFP4 / M3 low-bit lanes | 4×GB10 | 262K benchmark + 1M KV/serving profiles | 1M serving/KV 已公开；不同 checkpoint/KV variant 的深 prompt 合同必须分别看 | 4×大 KV/1M 很有价值，但 Variant 不得串证据 |
| gpt-oss-120b | 1×GB10 | **native 128K** | 公开 benchmark 有 16K 深度与 Agent tasks；不是 384K+ 模型 | 很好的 Classic Agent reference，不是大仓库 384K/512K 主模型 |
| Nemotron-3-Super NVFP4 | 1×GB10 | 官方/variant 宣称 up to 1M | 外部同硬件性能报告至少稳定到约 100K depth；没有在此审计中确认 512K/1M 深 prompt PASS | Long-context candidate/reference，不能因“up to 1M”直接写 1M GOOD |
| Kimi-K3 native MXFP4 | 当前 fleet | native checkpoint 远超 4×GB10 内存 | 高度压缩/streaming derivative 有实验，但不代表 native | WATCH / API / future cluster reference |

### 对你的 384K / 512K 主编码目标，当前真正值得注意的外部信号

- **2×GB10 + GLM-5.3-Flash NVFP4**：已经出现 512K standing profile 与 440K needle，长上下文证据非常直接；
- **2×GB10 + DeepSeek-V4 official**：1M serving/KV 平台能力成熟，官方 Coding/Agent 信号强，但仍应补同合同 384K/512K/1M deep-prompt；
- **2×GB10 + Qwen3.8-Flash-Next NVFP4**：速度、并发、262K/1M serving 都很吸引人，尤其适合做 Fast Main Coding / Repo Agent 对照；
- **1×GX10**：Qwen3.5-122B Hybrid 与 Qwen3.8-Flash-Next PLE-streaming 证明“不买第二台也有很强的升级空间”；
- **4×GB10**：MiniMax / GLM / DeepSeek 的价值主要是更大 KV、1M、并发和角色放置，不应该简单理解成“Decode 翻倍”。

---

## 这一轮真正改变判断的地方

- **Qwen3.5-122B-A10B 没有因为“旧一代”失去价值。** 单 GB10 成熟度、256K、外部 52–59 tok/s 路线和官方 Coding/Long-context 信号，使它成为非常重要的 Classic/Sweet-Spot P0 对照。
- **DeepSeek-V4 official 不是 304GB 纯 FP8。** 实际 release 约 167GB mixed checkpoint，2×GB10 已有 1M serving 实跑，因此它是 2× P0，而不是“必须 4 台”。
- **GLM 2×长上下文证据比旧版更强。** 公开路线已经推进到 512K standing config，并给出 440K-token needle 验证；不能继续只写“262K candidate”。
- **MiniMax-M3 不能写成“没有 GB10 证据”。** `nvidia/MiniMax-M3-NVFP4` 250GB 已有 4×GB10 的 262K/1M 路线；但这是 NVIDIA NVFP4 Variant，不等于 MiniMax official base。
- **gpt-oss-120b / Nemotron 3 Super 必须保留为经典参考，但不能挤掉更符合 384K/512K 目标的路线。**
- **GLM 4×证据必须分 Variant。** 最强的可审计实跑主要是 LibertAIDAI NVFP4 / derived FP8；不能把其数字自动转给 `zai-org official FP8` exact checkpoint。

---

## 现有 1×GX10：先不买硬件的顺序

```text
P0  Qwen3.8-27B：完成 first-party Quality + 128K→512K
P0  Qwen3.5-122B-A10B Hybrid：复现成熟 256K Coding baseline
P0  Qwen3.8-Flash-Next RadixArk NVFP4：复现 PLE streaming / 262K
P1  gpt-oss-120b：Classic Agent/Tool-use reference（128K ceiling）
P1  DeepSeek-V4 single-node ultra-low-bit/streaming：评估质量-速度代价
P2  Nemotron-3-Super：NVIDIA-native Agent/Long-context reference
```

这意味着“第二节点很有价值”与“第二节点现在必须买”仍然是两回事。

---

## 2×GB10：第一批应做同合同横比

```text
P0  DeepSeek-V4-Flash-0731 official mixed checkpoint
P0  Qwen3.8-Flash-Next RadixArk NVFP4
P1  GLM-5.3-Flash LibertAIDAI NVFP4
P2  MiniMax-M3 aggressive W4A16/GPTQ（必须先做 Quality Gate）
```

前三条已经有同 GB10 外部实跑，所以本仓第一方工作的重点应该是**统一 Formal5/Formal100/Quality/Context/Coding Loop 合同**，而不是重复证明“能不能启动”。

---

## 4×GB10：必须由 2×瓶颈触发

重点候选：

- `nvidia/MiniMax-M3-NVFP4`：4×GB10 已有完整 TP4/DSpark/262K benchmark 和 1M serving 实例；
- GLM-5.3 NVFP4：4× large-KV / 1M 路线成熟；
- DeepSeek V4 official：4×已有更大的 KV/concurrency/production envelope；
- Kimi K3：高度压缩/专家裁剪可以技术上塞进 4×，但当前速度/质量折衷仍不足以成为优先采购理由。

因此 4×的 Upgrade Trigger 应是：

```text
2× 已经被第一方 Coding Production workload 证明存在
不可由 model/runtime/context strategy 替代的容量、KV、并发或角色放置瓶颈
```

而不是“4 台 benchmark 看起来更爽”。

---

## 四级 Evidence

| Evidence | 含义 |
| --- | --- |
| **FIRST_PARTY_MEASURED** | 本仓自己在固定合同下跑过 |
| **REPRODUCIBLE_EXTERNAL** | 同 GB10 有公开版本、recipe、measured result，可显著降低复现风险 |
| **STRONG_EXTERNAL / VENDOR_CLAIM** | 模型质量、官方 benchmark、近似 Variant/平台信号 |
| **UNKNOWN / capacity only** | 只允许 OPEN / CONDITIONAL / UNSUITABLE，不允许冒充 GOOD/EXCELLENT |

外部证据不管多成熟，只要本仓没有 Quality Gate：

```text
quality_status = OPEN
recommendation_confidence = OPEN
```

---

## Variant 是推荐的基本单位

以下不能混：

```text
Qwen3.8-Flash-Next official FP8
!= RadixArk NVFP4

DeepSeek-V4 official mixed checkpoint
!= vLLM-Moet 2-bit/FP4 single-node route

GLM official FP8
!= LibertAIDAI NVFP4

MiniMax official base
!= nvidia/MiniMax-M3-NVFP4
!= community W4A16/GPTQ

Kimi native MXFP4
!= IQ1/REAP/expert-pruned derivative
```

**某 Variant 的速度/质量/内存/Context 证据不得自动转移给同家族其他 Variant。**

---

## 固定 6 类角色

`Quality Flagship / Production Sweet Spot / Coding Specialist / Long-Context Specialist / Classic Reference / Emerging-Hot`。

这些是多选标签，不是排行榜。Popularity 只决定“要不要进入候选池”，不决定生产适配。

---

## 统一资格链

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

推荐阅读：

1. [高质量模型候选与 GB10 / PRO6000 适配](high-quality-model-recommendations.md)
2. [三层 Decision Dashboard](dashboard.md)
3. [当前 GX10 Agent Fitness](current-gx10-agent-fitness.md)
4. [当前大型 Coding Production Fitness](current-gx10-production-fitness.md)
5. [当前改善/升级路线](current-gx10-roadmap.md)

机器 Registry：[`model-intelligence/registry.json`](../../model-intelligence/registry.json)。
