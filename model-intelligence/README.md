# Model Intelligence Registry

本目录是模型候选发现输入面，不是 Production Recommendation 榜单。

## 角色标签

一个模型/变体可以同时拥有多个标签：

- `quality_flagship`：质量上限候选；
- `production_sweet_spot`：质量×速度×内存综合候选；
- `coding_specialist`：编码专项候选；
- `long_context_specialist`：长上下文候选；
- `classic_reference`：生态成熟、适合作为长期比较锚；
- `emerging_hot`：新发布/热度高、值得优先验证。

标签不是排名，也不是 Production Qualification。

## 生命周期

`WATCH → CANDIDATE → RUNTIME_QUALIFIED → PERFORMANCE_QUALIFIED → QUALITY_QUALIFIED → AGENT_QUALIFIED → PRODUCTION_QUALIFIED → RECOMMENDED`

旁路状态：`REFERENCE / REJECTED / DEPRECATED / SUPERSEDED`。

## 证据边界

固定规则：

```text
Popularity / Momentum → 只影响测试优先级
Popularity != Quality
Quality != Hardware Fit
Hardware Fit != Agent Workload Fit
Agent Workload Fit != Coding Production Fit
```

外部 benchmark / 社区口碑 / Vendor Claim 必须保存 source、日期和 freshness；在目标本地硬件未实测前，Recommendation Confidence 可以且通常应该保持 `OPEN`。

## Recommendation Unit

生产推荐的最小单位不是模型名，而是：

`Model Family + Model Variant + Serving Profile + Hardware Topology + Workload Contract`。

同一基础模型的 BF16 / FP8 / NVFP4 / GGUF / MLX 等变体必须独立评价；不得把一个变体的性能或质量自动继承给另一个变体。

`registry.json` 当前只登记已有一方测试证据的 Qwen3.8-27B 三个变体作为种子。经典/旗舰/热门外部模型后续应按 source/freshness 规则进入候选池，再走 Runtime → Performance → Quality → Agent → Production 资格链。
