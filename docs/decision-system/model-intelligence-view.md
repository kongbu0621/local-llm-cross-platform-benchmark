# Model Intelligence — 经典 / 旗舰 / 甜点 / 专家 / 热门模型人类可读视图

> 这页回答的是：**哪些模型值得关注、为什么值得测、当前在什么阶段、和当前硬件的适配度证据到哪里。**
>
> Model Intelligence 只负责“候选发现”和“测试优先级”；模型很火、榜单很高，都不能直接升级成 Production Recommendation。

## 模型候选固定 6 类

| 类别 | 含义 | 典型用途 |
| --- | --- | --- |
| **Quality Flagship** | 当前质量上限候选 | Main Agent / Architect / 高难 reasoning |
| **Production Sweet Spot** | 质量 × 速度 × 内存 × 稳定性的综合甜点 | 日常生产主力 / Fast Worker |
| **Coding Specialist** | 编码、补丁、代码理解表现特别强 | Coding Worker / Reviewer / Bug Fix Agent |
| **Long-Context Specialist** | 长上下文、Repo-scale 理解能力突出 | Repo Analyst / Knowledge Agent / 大型项目主 Agent 候选 |
| **Classic Reference** | 经典、成熟、生态广、历史数据丰富 | Benchmark 锚点 / 长期对照尺 |
| **Emerging / Hot** | 新发布、爆火、有潜力，但尚未完成本地资格验证 | WATCH / CANDIDATE / 高优先测试池 |

这些是**角色标签，可以多选**。例如一个新模型可以同时是 `Quality Flagship + Coding Specialist + Emerging/Hot`；几年后又可能变成 `Classic Reference`。

## 当前已进入 Registry 的模型

| Model / Variant | 当前角色 | Lifecycle | Quality | 1×GX10 @32K 硬件适配 | Production Recommendation | 当前结论 |
| --- | --- | --- | --- | --- | --- | --- |
| Qwen3.8-27B BF16 | Classic Reference | PERFORMANCE_QUALIFIED | **OPEN** | CONDITIONAL | **未推荐** | 作为质量/精度参考基线有价值，但当前没有质量与 128K+ Production 资格 |
| Qwen3.8-27B FP8 | Production Sweet Spot Candidate | PERFORMANCE_QUALIFIED | **OPEN** | GOOD | **未推荐** | 当前性能明显优于 BF16；仍缺质量和大型项目生产验证 |
| Qwen3.8-27B NVFP4 mixed | Production Sweet Spot Candidate | PERFORMANCE_QUALIFIED | **OPEN** | **EXCELLENT @32K short-output** | **未推荐为 Main Coding Model** | 当前最快本地 inference/worker 候选；Coding quality、长 context、Production Qualification 均未闭环 |

### 为什么这里没有直接列一堆“全网最火模型并打五星”

因为必须保持：

```text
Popularity != Quality
Quality != Workload Fit
Workload Fit != Hardware Fit
Hardware Fit != Production Fit
```

外部新模型可以很快进入 WATCH / CANDIDATE，但只有经过 Runtime → Performance → Quality → Agent → Production qualification，才允许真正升级为 `RECOMMENDED`。

## 外部经典 / 旗舰 / 热门模型以后怎么进入

生命周期：

```text
WATCH
→ CANDIDATE
→ RUNTIME_QUALIFIED
→ PERFORMANCE_QUALIFIED
→ QUALITY_QUALIFIED
→ AGENT_QUALIFIED
→ PRODUCTION_QUALIFIED
→ RECOMMENDED
```

另外允许：`REFERENCE / REJECTED / DEPRECATED / SUPERSEDED`。

每个外部候选至少要记录：

| 字段 | 为什么需要 |
| --- | --- |
| Model Family / Variant / Revision | 防止只写一个模糊模型名 |
| Role Tags | Flagship / Sweet Spot / Coding / Long Context / Classic / Hot |
| Popularity / Momentum | 只用于发现和测试优先级 |
| External Quality Evidence | 区分第三方 benchmark、社区评价、厂商声称 |
| Context Claim | 只是声称，不等于 Actual Context |
| Quantization / Runtime Support | 决定是否值得进入本地 Runtime Gate |
| Hardware Memory Requirement | 判断 1×/2×/4× 节点可行性 |
| Source / Freshness | 防止旧结论永久有效 |
| Lifecycle | 当前在 WATCH 还是已经真正 Production Qualified |

## 真正推荐模型时看三轴，而不是看热度

未来每个模型至少同时看：

1. **Model Quality Fit**：coding / reasoning / instruction / agent / long-context 质量；
2. **Workload Fit**：它是否适合 Coding Worker、Repo Analyst、Architect、RAG、Resident 等目标工作负载；
3. **Hardware Fit**：目标 1×GX10 / 2×GB10 / PRO6000 / Apple 等平台能否高质量、稳定、足够快地跑。

最终推荐单位不是一个模型名，而是：

```text
Model Family
+ Model Variant
+ Serving Profile
+ Hardware Topology
+ Workload Contract
```

## 未来的人类可读推荐表

后续有更多真实模型数据后，本页会逐步形成这种矩阵：

| Model Variant | Role Tags | Quality Fit | Coding Fit | Long Context Fit | 1×GX10 | 2×GB10 | PRO6000 | 推荐角色 | Qualification / Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 当前 NVFP4 | Sweet Spot | OPEN | OPEN | OPEN | Excellent@32K perf | OPEN | OPEN | Fast local worker candidate | Performance measured / Production OPEN |
| 外部 Flagship X | Flagship / Coding | External evidence | External evidence | Claim / external | 未测 | 未测 | 未测 | Candidate only | WATCH/CANDIDATE |

**没有本地真实证据的格子继续写“未测 / OPEN”，不拿配置上限或社区口碑补洞。**

机器可读 Registry：[`model-intelligence/registry.json`](../../model-intelligence/registry.json)。
