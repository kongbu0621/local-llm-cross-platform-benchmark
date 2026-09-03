# Decision System v1 — L1 Fact / L2 Agent Decision / L3 Production Decision

状态：**FROZEN DESIGN v1**

本目录把 benchmark 仓库从“测速度”扩展为可审计的模型/硬件/工作负载决策系统。主体只保留三层；`Model Intelligence` 是候选发现输入面，`Decision Governance / Provenance` 是横向控制面，不新增第四层。

## 总体结构

```text
Model Intelligence ───────────────┐
                                  ▼
L1 — FACT: Benchmark / Evidence
  “真实发生了什么？”
        │
        ├──────────────┐
        ▼              │
L2 — AGENT DECISION    │
  “哪个 Model Variant × Serving Profile × Hardware Topology
   适合哪个 Agent Workload Contract？”
        │              │
        └──────┬───────┘
               ▼
L3 — PRODUCTION DECISION
  “怎样组合 Coding Tool、模型、执行位置和机器拓扑，
   才能最高效率推进真实大型软件工程？”
               │
               ▼
Recommendation → Next Test Plan → 新 L1 Evidence
```

横向贯穿三层：Evidence provenance、assumptions、constraints、freshness、decision change reason、confidence。

## L1 — Benchmark / Evidence

L1 最小对象是一次具体 `Experiment Run`：

```text
Model Variant
+ Serving Profile
+ Hardware Topology
+ Workload
+ Runtime State
+ Test Conditions
```

L1 只保存事实：Raw Evidence、Canonical Result、Measured Metrics、Derived Metrics、Stability、Quality、Hardware Gate、Evidence Level。

硬边界：

- `Measured != Derived != Unmeasured`；
- `Capability PASS != Production Fitness GOOD`；
- 配置支持上限不得冒充 `Actual Context`；
- 32K+256 不得冒充 `E2E@32K`；
- Hardware Gate 不得冒充质量结论；
- 单节点/单并发结果不得外推多节点/多并发。

## Model Intelligence — 候选发现输入面

Model Intelligence 只回答“什么值得进入测试池”，不能直接产生 Production Recommendation。

固定语义：

```text
Popularity != Quality
Quality != Workload Fit
Workload Fit != Hardware Fit
Hardware Fit != Production Fit
```

模型角色标签可多选：

- `quality_flagship`
- `production_sweet_spot`
- `coding_specialist`
- `long_context_specialist`
- `classic_reference`
- `emerging_hot`

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

并允许 `REFERENCE / REJECTED / DEPRECATED / SUPERSEDED`。

热门度和 momentum 只能提高测试优先级，不能提升质量或生产适配等级。

## L2 — Agent Workload Fitness

L2 最小评价对象（Fitness Unit）：

```text
Model Variant
× Serving Profile
× Hardware Topology
× Agent Workload Contract
```

人类可读的 `Coding Worker / Repo Analyst / RAG / Research / Browser / Resident / Autonomous / Multi-Agent` 是 Archetype；底层判断必须依赖 `Agent Workload Contract`，至少包含：

- Context Band；
- Output Profile；
- Tool-call Frequency；
- Session Duration；
- Concurrency；
- Quality Requirement；
- Latency / Prefill / Decode / Memory-KV 敏感度；
- Recovery Requirement；
- Residency Requirement。

### Qualification 与 Fitness 必须分开

Qualification：

- `QUALIFIED`
- `CONDITIONAL`
- `NOT_QUALIFIED`
- `OPEN`

Fitness：

- `EXCELLENT`
- `GOOD`
- `FAIR`
- `WEAK`
- `UNSUITABLE`

规则：

- Blocking Gate `FAIL` → `NOT_QUALIFIED`；
- Blocking Gate `OPEN` → 不得 `QUALIFIED`；
- `OPEN / NOT_QUALIFIED` 时 Fitness 必须为空，禁止用平均分掩盖未知或硬失败；
- 不维护一个跨目标函数的“总榜总分”。

L2 标准输出链：

```text
Qualification
→ Fitness
→ Blocking Gate
→ Dominant Bottleneck
→ Evidence
→ No-cost / Software / Workload / Model 改善
→ Hardware Upgrade Trigger
→ Expected Benefit
→ Residual Bottleneck
→ Next Required Test
→ Confidence
```

## L3 — Coding Production Fitness

L3 评价的不是一台机器，也不是一个 Coding Tool，而是一套 `Coding Production Configuration`：

```text
Coding Tool
+ Model Backend / Model Portfolio / Model Routing
+ Inference Placement
+ AI Hardware
+ Workspace Host
+ Build/Test Host
+ Storage / Git Authority
+ Project Profile
+ Context Strategy
+ Network
+ Operating Mode
```

必须显式记录 Execution Placement：

- Model Inference Placement；
- Workspace Placement；
- Build Placement；
- Test Placement；
- Repo Placement；
- Knowledge/RAG Placement；
- Control Plane Placement。

因此“升级本地 AI GPU”不能被解释为能加速云端 Codex/Claude 模型推理；它只改善真正放置在本地节点上的能力。

L3 同时允许评价：

- Monolithic Coding Node；
- Split Coding Topology（AI Node + Dev Host + Storage/Authority + Control Host）。

真正的 Coding Production 指标逐步从 tok/s 上移到：Task Success Rate、Accepted Patch Rate、Human Intervention / Task、Tool-loop Count、Build/Test Failure、Regression Rate、Recovery Rate、Wall-clock / Completed Task，最终才允许形成 `Useful Engineering Work / Hour`。该指标必须来自真实 coding task suite，绝不能由 Decode tok/s 外推。

## Recommendation — L2/L3 统一输出合同

Recommendation 不是第四层。干预顺序固定为：

```text
0  No Change
1  Configuration Fix
2  Runtime / Kernel Optimization
3  Workload / Context Strategy
4  Model / Variant Substitution
5  Model Routing
6  Role Reassignment
7  Component Upgrade
8  Add Homogeneous Node
9  Split / Redesign Topology
10 Platform Replacement
```

硬件升级前必须做 Counterfactual No-Hardware Check：模型/量化/runtime/context strategy/routing/role 调整是否已经能解决问题。若能解决，硬件升级不得升级为 `ACTION`。

任何硬件 `ACTION` 必须包含：

- Upgrade Trigger；
- Expected Gain；
- Does Not Solve；
- Cost；
- Operational Complexity；
- Residual Bottleneck；
- New Failure Domains；
- Next Required Test；
- Recommendation Confidence。

例如 `1× → 2× GB10` 只能在目标 context 的 memory/KV hard gate、或目标 Agent concurrency 的 QoS gate 被真实触发后，从 `OPTION` 升级为 `ACTION`；不能因为“2 台理论更强”直接推荐购买。

## Pareto Frontier

仓库不维护无目标函数的单一总榜。允许分别形成：

`Best Quality / Best Coding / Best Reasoning / Best Long Context / Best Fast Worker / Best Architect / Best 1×GX10 / Best 2×GB10 / Best PRO6000 / Best Low-TTFT / Best Multi-Agent / Best Overall Production`。

“第一名”只有在目标、约束和 workload contract 固定后才有意义。

## Confidence 双轴

Evidence Confidence：

- `FIRST_PARTY_MEASURED`
- `REPRODUCIBLE_EXTERNAL`
- `STRONG_EXTERNAL`
- `COMMUNITY`
- `VENDOR_CLAIM`
- `UNKNOWN`

Recommendation Confidence：`HIGH / MEDIUM / LOW / OPEN`。

外部模型 benchmark 即使证据很强，只要目标硬件尚未实测，其本地 Recommendation Confidence 仍可为 `OPEN`。

## Freshness / Assumption / Decision Change

每个 assessment/recommendation 必须带：`evaluated_at`、`evidence_as_of`、版本/修订信息。Recommendation 还必须保存 Optimization Objective、Assumptions、Constraints。

推荐发生变化时应能回答：

```text
Previous Recommendation
→ New Recommendation
→ Changed Because
→ Evidence Added / Assumption Changed / Constraint Changed
```

## 闭环

```text
Observe
→ L1 Evidence
→ L2/L3 Assessment
→ Blocking Gate / Bottleneck
→ Options
→ Counterfactual Check
→ Recommendation
→ Next Test Plan
→ New Experiment
→ New L1 Evidence
→ Re-evaluate
```

本设计的目标不是“给硬件打分”，而是建立可追溯、可反驳、可随新证据更新的决策控制系统。
