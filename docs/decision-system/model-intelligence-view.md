# Model Intelligence — 经典 / 旗舰 / 甜点 / 专家 / 热门模型人类可读视图

> 这页回答两个问题：**哪些模型值得关注？哪些高质量模型和你当前/计划中的硬件真正值得进入测试池？**
>
> 这里区分“推荐测试”和“生产推荐”。外部模型即使很强，只要没有本仓第一方 Runtime / Performance / Quality / Context / Agent / Production 证据，就只能是 `WATCH / CANDIDATE`。

## 先看真正的高质量候选推荐

**完整推荐、硬件适配、证据强度和测试顺序：** [高质量大模型候选推荐与当前硬件适配](high-quality-model-recommendations.md)

| Priority | Model | 主要角色 | 1×GX10 | 2×GB10 | 4×GB10 | PRO6000 96GB | 证据边界 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **P0** | **Qwen3.8-27B NVFP4 / FP8** | Fast Worker / Local Agent | **已有32K第一方性能** | OPEN | OPEN | OPEN | Hardware=FIRST_PARTY；Quality仍 OPEN |
| **P0** | **Qwen3.8-Flash-Next** | Fast Main Coding / Repo / Long Context | low-bit/offload OPEN | **official FP8 P0 candidate** | FP8 P0 | aggressive low-bit OPEN | Vendor quality signal；target-hardware runtime OPEN |
| **P0** | **DeepSeek-V4-Flash-0731** | Main Coding / Architect / Repo-scale | low-bit OPEN | low-bit P0 | **official FP8 capacity candidate** | aggressive low-bit OPEN | Official agent/coding evidence strong；GB10 distributed fit OPEN |
| **P1** | **GLM-5.3-Flash** | Coding / Repo / Long Context | low-bit OPEN | low-bit P1 | FP8 capacity P1 | low-bit OPEN | Official efficiency/coding evidence；GB10 fit OPEN |
| **P1** | **MiniMax-M3** | Long-context / Multimodal Coding | official base 不适配 | third-party low-bit OPEN | third-party low-bit P1 | official base 不适配 | **不再把 MXFP4 写成官方 checkpoint** |
| **P2 / Ref** | **Kimi-K3** | Quality Flagship / Large-cluster Ref | native 不适配 | native 不适配 | native 不适配 | native 不适配 | 2.8T native MXFP4；当前 fleet 只做 API/未来集群参考 |

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

这些是**角色标签，可以多选**，不是排名。

## 当前 Registry 状态

| Model / Variant | Lifecycle | Test Priority | Quality Status | Quality Evidence | Hardware Evidence | License | 当前硬件含义 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Qwen3.8-27B BF16 | PERFORMANCE_QUALIFIED | P0 | OPEN | Vendor claim | **First-party measured** | Apache-2.0 | 1×GX10 reference；补 Quality |
| Qwen3.8-27B FP8 | PERFORMANCE_QUALIFIED | P0 | OPEN | Vendor claim | **First-party measured** | Apache-2.0 | 1×GX10 GOOD；补 Quality |
| Qwen3.8-27B NVFP4 mixed | PERFORMANCE_QUALIFIED | P0 | OPEN | UNKNOWN for this quant | **First-party measured** | variant terms | 1×GX10 32K perf EXCELLENT；Fast Worker candidate |
| Qwen3.8-Flash-Next | CANDIDATE | **P0** | CONDITIONAL | Vendor claim | UNKNOWN on fleet | qwen-community-1.0 | **2×GB10 当前最现实的新模型候选之一** |
| DeepSeek-V4-Flash-0731 | CANDIDATE | **P0** | CONDITIONAL | Vendor claim | UNKNOWN on fleet | MIT | 2×low-bit / 4×FP8 candidate |
| GLM-5.3-Flash | CANDIDATE | P1 | CONDITIONAL | Vendor claim | UNKNOWN on fleet | MIT | 2×low-bit / 4×FP8 candidate |
| MiniMax-M3 | CANDIDATE | P1 | CONDITIONAL | Vendor claim | UNKNOWN on fleet | minimax-community | 4× third-party low-bit candidate；官方 base 太大 |
| Kimi-K3 | WATCH | P2 | CONDITIONAL | Vendor claim | UNKNOWN on fleet | kimi-k3 | 当前 local native 不适配；API/reference |

这里的 `CONDITIONAL` 只表示**存在较强外部 capability/quality 信号**，不代表本仓已经完成 Quality Qualification。

---

## 为什么不能把“火爆”直接写成“生产推荐”

```text
Popularity != Quality
Quality != Workload Fit
Workload Fit != Hardware Fit
Hardware Fit != Production Fit
```

外部候选必须经过：

```text
Runtime
→ Performance
→ Quality
→ Context-band
→ Agent Fitness
→ Coding Production Fitness
```

才允许升级为 `RECOMMENDED`。

## 推荐模型至少看五件事

1. **Model Quality Fit**：coding / reasoning / instruction / agent / long-context；
2. **Workload Fit**：Coding Worker、Repo Analyst、Architect、RAG、Resident 等；
3. **Hardware Fit**：目标精度、Actual Context、KV、速度、稳定性；
4. **Evidence Confidence**：第一方实测、可复现外部、厂商 benchmark 还是社区信号；
5. **License / Deployment Terms**：能否用于真实交付和长期部署。

最终推荐单位仍然是：

```text
Model Family
+ Model Variant
+ Serving Profile
+ Hardware Topology
+ Workload Contract
```

## 当前推荐阅读顺序

1. [高质量模型候选与硬件适配](high-quality-model-recommendations.md) — 看“应该测谁、在哪套硬件上测”；
2. [当前 GX10 Agent Fitness](current-gx10-agent-fitness.md) — 看“现在已经能承担什么”；
3. [当前大型 Coding Production Fitness](current-gx10-production-fitness.md) — 看“离主编码生产系统还缺什么”；
4. [当前改善/升级路线](current-gx10-roadmap.md) — 看“下一步怎么补”。

机器可读 Registry：[`model-intelligence/registry.json`](../../model-intelligence/registry.json)。
