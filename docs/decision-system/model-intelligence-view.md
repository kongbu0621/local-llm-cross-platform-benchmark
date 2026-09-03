# Model Intelligence — 高质量模型、Variant 与硬件证据一页看懂

> **给人看的入口。** 机器 Registry 在 `model-intelligence/registry.json`。这页只回答三件事：**谁值得测、在哪套硬件上测、证据到底是一方实测还是外部线索。**

完整分析：[高质量大模型候选推荐与 GB10 / PRO6000 适配](high-quality-model-recommendations.md)。

## 当前 shortlist

| Priority | Model / Variant | 1×GX10 | 2×GB10 | 4×GB10 | Evidence | 本仓 Quality |
| --- | --- | --- | --- | --- | --- | --- |
| **P0** | Qwen3.8-27B BF16 / FP8 / NVFP4 | **FIRST-PARTY @32K** | OPEN | OPEN | **FIRST_PARTY_MEASURED** | OPEN |
| **P0** | Qwen3.5-122B-A10B Hybrid INT4+FP8 | **GOOD @256K external** | OPEN | OPEN | **REPRODUCIBLE_EXTERNAL** | OPEN |
| **P0** | Qwen3.8-Flash-Next RadixArk NVFP4 | **GOOD PLE-streaming external** | **GOOD TP2 external** | OPEN | **REPRODUCIBLE_EXTERNAL** | OPEN |
| **P0** | DeepSeek-V4-Flash-0731 official mixed checkpoint | single full-resident 不适配；量化 P1 | **GOOD TP2/1M external** | **GOOD TP4 external** | **REPRODUCIBLE_EXTERNAL** | OPEN |
| **P1** | GLM-5.3-Flash LibertAIDAI NVFP4 | 不适配 | **GOOD TP2/262K external** | **GOOD TP4/large-KV external** | **REPRODUCIBLE_EXTERNAL** | OPEN |
| **P1** | GLM-5.3-Flash exact official FP8 | 不适配 | 不适配 full-resident | **CONDITIONAL** | STRONG_EXTERNAL；exact variant 未锁定实测 | OPEN |
| **P1** | nvidia/MiniMax-M3-NVFP4 | 不适配 | 过紧/CONDITIONAL | **GOOD TP4 external** | **REPRODUCIBLE_EXTERNAL** | OPEN |
| **P2** | MiniMax-M3 community W4A16/GPTQ | 不适配 | CONDITIONAL external | OPEN | REPRODUCIBLE_EXTERNAL hardware；quality UNKNOWN | OPEN |
| **WATCH** | Kimi-K3 native MXFP4 | native 不适配 | native 不适配 | native 不适配 | Vendor/capacity | OPEN |

### 这一轮真正改变判断的地方

- **Qwen3.5-122B-A10B 没有因为“旧一代”失去价值。** 单 GB10 成熟度、256K、外部 52–59 tok/s 路线和官方 Coding/Long-context 信号，使它成为非常重要的 Classic/Sweet-Spot P0 对照。
- **DeepSeek-V4 official 不是 304GB 纯 FP8。** 实际 release 约 167GB mixed checkpoint，2×GB10 已有 1M 实跑，因此它是 2× P0，而不是“必须 4 台”。
- **MiniMax-M3 不能再写成“没有 GB10 证据”。** `nvidia/MiniMax-M3-NVFP4` 250GB 已有 4×GB10 的 262K/1M 路线；但这是 NVIDIA NVFP4 Variant，不等于 MiniMax official base。
- **GLM 4×证据必须分 Variant。** 最强的可审计实跑主要是 LibertAIDAI NVFP4 / derived FP8；不能把其数字自动转给 `zai-org official FP8` exact checkpoint。

---

## 现有 1×GX10：先不买硬件的顺序

```text
P0  Qwen3.8-27B：完成 first-party Quality + 128K→512K
P0  Qwen3.5-122B-A10B Hybrid：复现成熟 256K Coding baseline
P0  Qwen3.8-Flash-Next RadixArk NVFP4：复现 PLE streaming / 262K
P1  DeepSeek-V4 single-node ultra-low-bit/streaming：评估质量-速度代价
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

**某 Variant 的速度/质量/内存证据不得自动转移给同家族其他 Variant。**

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
