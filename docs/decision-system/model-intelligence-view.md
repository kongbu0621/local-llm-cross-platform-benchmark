# Model Intelligence — 高质量模型、角色与硬件证据一页看懂

> **这是给人看的 Model Intelligence 入口。** 机器 Registry 在 `model-intelligence/registry.json`。本页区分“本仓第一方已测”“同 GB10 可复现外部实跑”“厂商质量信号”“纯容量推理”，避免把它们混成一个模糊的“适配度”。

## 先看真正值得测的模型

完整证据与部署边界：[高质量大模型候选推荐与 GB10 / PRO6000 适配](high-quality-model-recommendations.md)。

| Priority | Model / Variant | 主要角色 | 1×GX10 | 2×GB10 | 4×GB10 | 证据层 | 本仓 Quality |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **P0** | **Qwen3.8-27B NVFP4 / FP8** | Fast Worker / Local Agent | **第一方已测 @32K** | OPEN | OPEN | **FIRST_PARTY_MEASURED** | **OPEN** |
| **P0** | **Qwen3.8-Flash-Next · RadixArk NVFP4** | Fast Main Coding / Repo / Long Context | **GOOD：外部单 GB10 PLE-streaming** | **GOOD：外部 TP2** | OPEN | **REPRODUCIBLE_EXTERNAL** | **OPEN** |
| **P0** | **DeepSeek-V4-Flash-0731 official mixed checkpoint** | Main Coding / Architect / Repo-scale | full-resident 不适配 | **GOOD：外部 TP2 / 1M** | OPEN | **REPRODUCIBLE_EXTERNAL** | **OPEN** |
| **P1** | **GLM-5.3-Flash · LibertAIDAI NVFP4** | Coding / Repo / Long Context | full-resident 不适配 | **GOOD：外部 TP2 / 262K** | OPEN | **REPRODUCIBLE_EXTERNAL** | **OPEN** |
| **P1** | **GLM-5.3-Flash official FP8** | High-quality / 1M Reference | 不适配 | full-resident 不适配 | **GOOD：外部 TP4 / 1M** | **REPRODUCIBLE_EXTERNAL** | **OPEN** |
| **P2** | **MiniMax-M3 official base** | Long-context / Multimodal Coding | 不适配 | 不适配 official base | third-party low-bit OPEN | Vendor / capacity only | **OPEN** |
| **WATCH** | **Kimi-K3 native MXFP4** | Cloud/API Quality Flagship / Future Cluster | 不适配 | 不适配 | 不适配 native full-weight | Vendor / capacity only | **OPEN** |

**现在最值得注意的不是一个“排行榜第一名”，而是三条已经有同 GB10 实跑证据的路线：**

1. 现有 **1×GX10**：先复现 Qwen3.8-Flash-Next RadixArk NVFP4 的单节点 PLE-streaming 路线，同时完成 Qwen3.8-27B 第一方 Quality/长上下文闭环；
2. **2×GB10**：DeepSeek-V4-Flash-0731 official、Qwen3.8-Flash-Next RadixArk NVFP4 是 P0；GLM-5.3-Flash NVFP4 是 P1；
3. **4×GB10**：先证明 2× 的不可替代瓶颈，再看 GLM official FP8 / 1M、更多并发和 scaling efficiency，而不是因为 4 台理论更强就直接升级。

---

## 四种证据不要混

| Evidence | 可以证明什么 | 不能证明什么 |
| --- | --- | --- |
| **FIRST_PARTY_MEASURED** | 本仓目标硬件、固定合同确实跑过 | 未覆盖的 Context / Quality / Production 仍不能外推 |
| **REPRODUCIBLE_EXTERNAL** | 同 GB10 类硬件已有公开 recipe + measured results，可显著降低试错风险 | 不能自动成为本仓 Qualification，也不能拿不同 workload 的 tok/s 直接排名 |
| **VENDOR_CLAIM / official evidence** | 模型架构、官方 benchmark、context claim、支持框架值得进入候选池 | 不能证明你的 GX10 已适配 |
| **Capacity arithmetic** | 可以排除明显放不下的组合，或判断值得不值得试 | 不能证明 Runtime / KV / 速度 / 长上下文 / 稳定性 |

固定语义：

```text
Popularity != Quality
Quality != Workload Fit
Workload Fit != Hardware Fit
Hardware Fit != Production Fit

External same-hardware evidence
!=
First-party Qualification
```

---

## 为什么 Variant 必须拆开

模型推荐的单位不是一个模糊的模型名。例如下面这些**必须是不同记录**：

```text
Qwen3.8-Flash-Next official FP8
!= RadixArk Qwen3.8-Flash-Next NVFP4

GLM-5.3-Flash official FP8
!= LibertAIDAI GLM-5.3-Flash NVFP4

DeepSeek-V4-Flash-0731 official mixed checkpoint
!= 任意第三方 MXFP4 / INT4 量化
```

原因是 Variant 会改变：权重驻留、Runtime backend、KV 余量、速度、质量损失和适用节点数。**外部某个 Variant 的实测证据不得自动转移给另一个 Variant。**

---

## 本轮三个重要纠错

### DeepSeek-V4-Flash-0731

之前按 `304B × FP8 ≈ 304GB` 判断官方 checkpoint 至少需要 4×GB10，这是错误的模型文件语义。实际发布 checkpoint 约 167GB，配置同时包含 `expert_dtype=fp4` 与 FP8 quantization path，属于 mixed-precision checkpoint；已经有公开 2×GB10 TP2 / 1M 实跑。因此当前应是 **2×GB10 P0 direct candidate**，不是“2×只能第三方低比特”。

### Qwen3.8-Flash-Next

官方 FP8 与 RadixArk NVFP4 必须拆开。RadixArk NVFP4 约 135GB，并已有 1×GB10 PLE 从 NVMe streaming、2×GB10 TP2 / 262K 的公开实跑。它使“**先不买第二节点也能尝试更大模型**”成为真正值得第一方复现的路线。

### GLM-5.3-Flash

2×GB10 的可复现路线是第三方 LibertAIDAI NVFP4；4×GB10 有 official/native FP8 的公开路线。两条证据不能混写。当前分别作为 2× P1 与 4× high-quality reference candidate。

---

## 模型候选固定 6 类

| 类别 | 典型用途 |
| --- | --- |
| **Quality Flagship** | Main Agent / Architect / 高难 reasoning |
| **Production Sweet Spot** | 日常生产主力 / Fast Worker |
| **Coding Specialist** | Coding Worker / Reviewer / Bug Fix |
| **Long-Context Specialist** | Repo Analyst / Knowledge Agent / 大型项目主 Agent |
| **Classic Reference** | 长期 benchmark 锚点 / 质量参考 |
| **Emerging / Hot** | WATCH / CANDIDATE / 高优先测试池 |

角色标签可以多选；**Hot 只提高发现/测试优先级，不提高 Production Qualification。**

---

## 当前 Registry 生命周期

- Qwen3.8-27B BF16 / FP8 / NVFP4：`PERFORMANCE_QUALIFIED`，但 Quality 仍 `OPEN`；
- Qwen3.8-Flash-Next official FP8 / RadixArk NVFP4：`CANDIDATE`；
- DeepSeek-V4-Flash-0731 official：`CANDIDATE`；
- GLM-5.3-Flash official FP8 / LibertAIDAI NVFP4：`CANDIDATE`；
- MiniMax-M3：`CANDIDATE / P2`；
- Kimi-K3：`WATCH`。

即使 `hardware_evidence_confidence=REPRODUCIBLE_EXTERNAL`，没有本仓 Quality Gate 时仍保持：

```text
quality_status = OPEN
recommendation_confidence = OPEN
```

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

外部同硬件证据的作用是**把第一方试错集中到最有价值的路线**，不是跳过资格链。

推荐阅读：

1. [高质量模型候选与 GB10 / PRO6000 适配](high-quality-model-recommendations.md)
2. [三层 Decision Dashboard](dashboard.md)
3. [当前 GX10 Agent Fitness](current-gx10-agent-fitness.md)
4. [当前大型 Coding Production Fitness](current-gx10-production-fitness.md)
5. [当前改善/升级路线](current-gx10-roadmap.md)

机器 Registry：[`model-intelligence/registry.json`](../../model-intelligence/registry.json)。
