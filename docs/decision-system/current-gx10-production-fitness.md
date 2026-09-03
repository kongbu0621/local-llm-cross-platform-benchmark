# 当前实例：1×GX10 + Qwen3.8-27B NVFP4 — 高强度大型项目 Coding Production Fitness

> **这页是给人看的 L3。** 机器记录见：[`assessments/production/gx10-qwen38-nvfp4-large-coding-v1.json`](../../assessments/production/gx10-qwen38-nvfp4-large-coding-v1.json)。

## 当前总评

| 项目 | 当前结论 |
| --- | --- |
| Production Qualification | **OPEN** |
| Production Fitness | **暂不评分** |
| 当前最强已证角色 | **Local AI Inference / Fast Worker Node @32K** |
| Main Large-Project Coding Agent | **尚未资格化** |
| Monolithic Coding Node | **OPEN** |
| Split AI Node + Dev Host | **OPEN，但架构上更值得继续验证** |
| 推荐置信度 | OPEN |

### 人话结论

当前 1×GX10 + Qwen3.8-27B NVFP4 已经证明：**本地 32K inference 很快，适合作为 Fast AI Worker 候选。**

但“高强度大型 C++ / UE 类项目”需要的不只是模型生成速度，还包括大上下文、代码质量、repo 理解、search/edit/build/test 循环、长会话、恢复能力和执行位置。因此目前**没有资格把 GX10 宣称成已经验证的大项目主 Coding Agent 或完整 Coding Workstation**。

## 为什么现在还是 OPEN

| Blocking Gate | 状态 | 需要补什么 |
| --- | --- | --- |
| 384K / 512K Large Context | **OPEN** | 同合同 performance、memory/KV、稳定性 |
| Coding Production Quality | **OPEN** | correctness、repo understanding、patch minimality、regression avoidance、scope control |
| Real Coding Tool Loop | **OPEN** | search → edit → diff → build → test → diagnose → repair |
| Long Session / Recovery | **OPEN** | 长会话、restart、crash recovery、constraint retention |
| Execution Placement | **OPEN** | inference/workspace/build/test/repo/control 的最终主机分工 |

只要其中关键 Blocking Gate 仍 OPEN，就不能用 32K tok/s 直接给“生产适配度”打高分。

## 当前两种拓扑怎么看

### 方案 A：Monolithic Coding Node

```text
GX10
├─ Local Model Inference
├─ Workspace
├─ Search / Edit
├─ Build
├─ Test
└─ Agent Runtime
```

当前：**OPEN**。

原因：现有 benchmark 只证明 LLM inference，不足以证明 GX10 同时承担大型 C++/UE workspace、build/test 后仍有好的端到端生产效率。

### 方案 B：Split Coding Topology

```text
GX10 / AI Node
    │  Local model / Repo Agent / Worker
    ▼
Development Host
    │  Workspace / IDE / C++ / UE Build / Tests
    ▼
NAS / Git Authority / Knowledge
```

当前：**OPEN，但更符合角色分离思路。**

如果后续真实 Coding Task Suite 证明：AI inference 的瓶颈和 CPU/RAM/NVMe build/workspace 的瓶颈最好由不同机器承担，那么 Split Topology 可以比“把所有东西塞进一台机器”更合理。

## 当前实际已知的模型侧性能

| 指标 | NVFP4 @ 32K+256 |
| --- | ---: |
| Effective Prefill* | 1300.614 tok/s |
| TTFT | 25.194 s |
| TPOT | 110.122 ms/token |
| Decode | 9.081 tok/s |
| E2E | 53.275 s |
| Completion | 100/100 |

这些指标只证明本地 inference 基础；**Useful Engineering Work / Hour 不能从 9.081 tok/s 数学推出来。**

## L3 最终真正要看的指标

后续真实大型项目 Coding Suite 应逐步测：

- Task Success Rate；
- Accepted Patch Rate；
- Human Intervention / Task；
- Search/Edit/Tool-loop Count；
- Build/Test Failure Rate；
- Regression Rate；
- Recovery Success Rate；
- Wall-clock / Completed Task；
- Context Reload / Constraint Loss；
- 最终才允许形成 `Useful Engineering Work / Hour`。

## 当前主结论

1. **GX10 现在最有证据的定位是 AI Worker，不是“已经验证的完整开发主机”。**
2. **384K/512K 是大型项目主 Agent 的关键下一关。**
3. **质量 Gate 与速度 Gate 必须分开。** 模型快不能证明 patch 正确、架构一致、不会制造 regression。
4. **云端 Codex/Claude 的推理延迟不能算在本地 GX10 硬件收益上。** 如果模型推理在云端，本地硬件升级改善的是 workspace/build/local agent 等真正本地执行的部分。
5. **未来应该比较 Monolithic vs Split Topology，而不是先假定“更强的一台机器”一定最优。**

下一步路线见：[当前 GX10 改善/升级路线图](current-gx10-roadmap.md)。
