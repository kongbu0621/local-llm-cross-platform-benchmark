# Model Intelligence — 经典 / 旗舰 / 甜点 / 专家 / 热门模型人类可读视图

> 这页回答两个问题：**哪些模型值得关注？哪些高质量模型和你当前/计划中的硬件真正值得进入测试池？**
>
> 这里区分“推荐测试”和“生产推荐”。外部模型即使很强，只要没有第一方 Runtime / Performance / Quality / Agent / Production 证据，就只能是 `WATCH / CANDIDATE`。

## 先看真正的高质量候选推荐

**完整推荐、硬件适配和测试优先级：** [高质量大模型候选推荐与当前硬件适配](high-quality-model-recommendations.md)

当前 shortlist：

| Test Priority | Model | 主要角色 | 1×GX10 | 2×GB10 | 4×GB10 | PRO6000 96GB | 当前结论 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **P0** | **Qwen3.8-27B NVFP4 / FP8** | Fast Worker / Local Agent | **已有32K性能实测** | OPEN | OPEN | OPEN | 当前唯一已有本仓第一方性能锚点；Quality/384K+仍 OPEN |
| **P0** | **DeepSeek-V4-Flash-0731** | Main Coding / Architect / Long-context Agent | 低比特 OPEN；官方FP8容量不适配 | **低比特 P0 Candidate** | **FP8/高质量 P0 Candidate** | aggressive low-bit OPEN | Coding/Agent 官方外部证据很强；本地资格尚未完成 |
| **P0/P1** | **GLM-5.3-Flash** | Coding / Repo / Long-context Agent | 低比特 OPEN | **低比特 P0/P1** | **FP8/高质量 P0** | 低比特 OPEN | 320B/18B active，长上下文效率路线值得重点验证 |
| **P1** | **MiniMax-M3** | Long-context / Multimodal Coding | 不适合作为 full-resident 目标 | MXFP4 capacity OPEN | **MXFP4 P1** | full-resident 不适配 | 428B/23B active、1M、MSA；更适合4×路线 |
| **P2 / Reference** | **Kimi-K3** | Quality Flagship / Large-cluster Reference | 不适配 native full-weight | 不适配 | 不适配 | 不适配 | 2.8T native MXFP4 远超当前本地 fleet；只做 API/未来大集群参考 |

`P0/P1/P2` 是**测试优先级**，不是质量总分，也不是购买顺序。

---

## 模型候选固定 6 类

| 类别 | 含义 | 典型用途 |
| --- | --- | --- |
| **Quality Flagship** | 当前质量上限候选 | Main Agent / Architect / 高难 reasoning |
| **Production Sweet Spot** | 质量 × 速度 × 内存 × 稳定性的综合甜点 | 日常生产主力 / Fast Worker |
| **Coding Specialist** | 编码、补丁、代码理解表现特别强 | Coding Worker / Reviewer / Bug Fix Agent |
| **Long-Context Specialist** | 长上下文、Repo-scale 理解能力突出 | Repo Analyst / Knowledge Agent / 大型项目主 Agent 候选 |
| **Classic Reference** | 经典、成熟、生态广、历史数据丰富 | Benchmark 锚点 / 长期对照尺 |
| **Emerging / Hot** | 新发布、爆火、有潜力，但尚未完成本地资格验证 | WATCH / CANDIDATE / 高优先测试池 |

这些是**角色标签，可以多选**。一个模型可以同时是 `Quality Flagship + Coding Specialist + Emerging/Hot`；几年后又可能成为 `Classic Reference`。

## 当前 Registry 状态

| Model / Variant | Role Tags | Lifecycle | Quality Status | 当前硬件含义 |
| --- | --- | --- | --- | --- |
| Qwen3.8-27B BF16 | Classic Reference | PERFORMANCE_QUALIFIED | OPEN | 1×GX10 参考基线；Quality仍待测 |
| Qwen3.8-27B FP8 | Production Sweet Spot | PERFORMANCE_QUALIFIED | OPEN | 1×GX10 性能 GOOD；Quality仍待测 |
| Qwen3.8-27B NVFP4 mixed | Production Sweet Spot | PERFORMANCE_QUALIFIED | OPEN | 1×GX10 32K性能 EXCELLENT；当前 Fast Worker P0 |
| DeepSeek-V4-Flash-0731 | Flagship / Sweet Spot / Coding / Long Context / Hot | CANDIDATE | CONDITIONAL | 2×低比特、4×高质量重点测试候选 |
| GLM-5.3-Flash | Flagship / Sweet Spot / Coding / Long Context / Hot | CANDIDATE | CONDITIONAL | 2×低比特、4×高质量重点测试候选 |
| MiniMax-M3 | Flagship / Coding / Long Context / Hot | CANDIDATE | CONDITIONAL | 4×GB10 长上下文 P1 候选 |
| Kimi-K3 | Flagship / Coding / Long Context / Hot | WATCH | CONDITIONAL | 当前本地 fleet 不适配 native full-weight；参考/API |

这里的 `CONDITIONAL` 只表示**存在较强外部质量/capability 信号**，不代表本仓完成 Quality Qualification。

---

## 为什么不能把“火爆”直接写成“生产推荐”

固定保持：

```text
Popularity != Quality
Quality != Workload Fit
Workload Fit != Hardware Fit
Hardware Fit != Production Fit
```

外部新模型可以立即进入 `WATCH / CANDIDATE`，但必须经过：

```text
Runtime
→ Performance
→ Quality
→ Context-band
→ Agent Fitness
→ Coding Production Fitness
```

才允许升级为 `RECOMMENDED`。

## 真正推荐模型时看三轴

1. **Model Quality Fit**：coding / reasoning / instruction / agent / long-context 质量；
2. **Workload Fit**：是否适合 Coding Worker、Repo Analyst、Architect、RAG、Resident 等目标负载；
3. **Hardware Fit**：1×GX10 / 2×GB10 / 4×GB10 / PRO6000 等能否以目标精度、Context、速度和稳定性运行。

最终推荐单位不是模型名，而是：

```text
Model Family
+ Model Variant
+ Serving Profile
+ Hardware Topology
+ Workload Contract
```

## 当前推荐阅读顺序

1. [高质量模型候选与硬件适配](high-quality-model-recommendations.md) — 看“应该测谁”；
2. [当前 GX10 Agent Fitness](current-gx10-agent-fitness.md) — 看“现在已经能承担什么”；
3. [当前大型 Coding Production Fitness](current-gx10-production-fitness.md) — 看“离主编码生产系统还缺什么”；
4. [当前改善/升级路线](current-gx10-roadmap.md) — 看“下一步怎么补”。

机器可读 Registry：[`model-intelligence/registry.json`](../../model-intelligence/registry.json)。
