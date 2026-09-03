# Model Intelligence — Registry Set / 模型情报输入面

本目录负责**候选发现、Variant 身份、外部证据与第一方测试优先级**。它不是 Production Recommendation 榜单。

## 机器文件怎么分

Model Intelligence 现在是一个逻辑 Registry Set，而不是要求把所有模型塞进一个巨大 JSON：

```text
registry.json
  核心模型 / 第一方 benchmark 主线 / 大型硬件候选

registry.agentic*.json
  因真实 Agentic Coding 证据进入候选池的 exact Variants / references

agentic-coding-evidence.json
  外部真实 search/edit/tool/test/hidden-test/task-completion 证据
```

所有 `registry*.json` 都必须通过同一个 `schemas/model-intelligence.schema.json`；`agentic-coding-evidence.json` 使用独立的 `schemas/agentic-coding-evidence.schema.json`，并且每条 evidence 必须通过 `registry_record_id` 回指 Registry Set 中的模型记录。

这避免两种错误：

1. 人类 Dashboard 已经推荐某个模型，但自动推荐器的机器 Registry 看不到它；
2. Agentic Coding benchmark 使用了某个具体 GGUF/NVFP4/INT4 Variant，却错误回指同模型家族的另一个 Variant。

## 五条证据轴

必须区分：

```text
Hardware Evidence
Context Evidence
Quality Evidence
Agentic Coding Evidence
First-party Coding Production Qualification
```

其中 Context 还要继续拆：

```text
Configured / Model Length
!= KV Allocated
!= Actual Prompt Processed
!= Retrieval / Needle Validated
!= Coding Production Qualified
```

外部同 GB10 证据可以显著提高复制优先级，但不能跳过本仓资格链。

## 角色标签

一个模型/变体可以同时拥有多个标签：

- `quality_flagship`：质量上限候选；
- `production_sweet_spot`：质量 × 速度 × 内存综合候选；
- `coding_specialist`：编码专项候选；
- `long_context_specialist`：长上下文候选；
- `classic_reference`：成熟、适合作为长期比较锚；
- `emerging_hot`：新发布/热度高、值得优先验证。

标签不是排名，也不是 Production Qualification。

## 生命周期

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

旁路状态：`REFERENCE / REJECTED / DEPRECATED / SUPERSEDED`。

`REJECTED` 可以用于**exact Variant / exact configuration** 的明确负例，但不得自动升级为同 Model Family 的否定结论。

## 固定证据边界

```text
Popularity / Momentum → 只影响发现与测试优先级
Popularity != Quality
Quality != Hardware Fit
Hardware Fit != Context Fit
Context Fit != Agentic Coding Fit
Agentic Coding Fit != Coding Production Qualification
```

此外：

```text
Model Family != Model Variant
```

Official FP8、NVFP4、INT4、W4A16、GGUF、streaming、expert-pruned 等必须独立记录；某个 Variant 的速度、Context、质量或 Agent Loop 证据不得自动转移给另一个 Variant。

## Recommendation Unit

生产推荐的最小单位不是模型名，而是：

```text
Model Family
+ Model Variant
+ Serving Profile
+ Hardware Topology
+ Workload Contract
```

到了 L3 还要继续绑定：Coding Tool / Agent Harness / Workspace / Build-Test Placement / Recovery / Project Profile。

## Agentic Coding Evidence 的权限

外部 Agentic Coding ledger 可以记录：

- exact Variant；
- GB10 topology；
- runtime；
- Agent harness；
- task suite；
- hidden tests；
- run count / repeat range；
- wall-clock / tool calls；
- named failure mode；
- source / caveat。

它可以：

```text
提高 Candidate Test Priority
暴露 Runtime / Harness failure mode
选择值得第一方复现的 Variant
```

它不能：

```text
external hidden-test PASS
→ quality_status = QUALIFIED        ❌

external Agent Loop PASS
→ PRODUCTION_QUALIFIED              ❌
```

## 当前人类入口

- [`docs/decision-system/model-intelligence-view.md`](../docs/decision-system/model-intelligence-view.md) — compact dashboard；
- [`docs/decision-system/high-quality-model-recommendations.md`](../docs/decision-system/high-quality-model-recommendations.md) — 模型 × 1×/2×/4×GB10/PRO6000 shortlist 与 Context Evidence；
- [`docs/decision-system/agentic-coding-evidence.md`](../docs/decision-system/agentic-coding-evidence.md) — 真实 Agent Coding Loop、重复性与 Harness 影响。

## 当前机器验证

CI 会：

1. 校验全部 `registry*.json` 的 Model Intelligence Schema；
2. 检查跨 shard `record_id` 唯一；
3. 校验 Agentic Coding ledger Schema；
4. 要求每条 Agentic evidence 的 `registry_record_id` 可解析；
5. 阻止外部证据产生 first-party Quality / Production Qualification；
6. 检查 repeat range、hidden-test 计数、负配置生命周期与基础语义。

最终 Production Recommendation 仍必须回到本仓自己的：

```text
Runtime
→ Performance
→ Context
→ Quality
→ Agentic Coding Repeatability
→ Long Session / Recovery
→ L2 Agent Workload Fitness
→ L3 Coding Production Fitness
→ Production Recommendation
```
