# 当前 GX10 — 改善 / 补测 / 升级路线图（人类可读）

> 这页把 Recommendation JSON 翻成人能直接看懂的决策路线。机器记录：[`recommendations/gx10-qwen38-nvfp4-roadmap-v1.json`](../../recommendations/gx10-qwen38-nvfp4-roadmap-v1.json)。

## 现在该做什么

**当前选择：保持硬件不变，先关闭关键 Gate。**

原因不是“第二台 GX10 没价值”，而是现在还没有真实证据证明：大型项目目标 workload 的瓶颈已经属于**无法通过模型 / 量化 / runtime / context strategy 解决的硬件瓶颈**。

## 干预优先级

| 顺序 | 动作 | 当前状态 | 为什么 |
| ---: | --- | --- | --- |
| 0 | No Change / 先补证据 | **ACTION** | 避免在未知瓶颈上提前花钱 |
| 1 | Pure Prefill / TTFT 测量与优化 | OPTION | 当前 32K 下 TTFT 已占 E2E 较大比例 |
| 2 | 128K → 256K → 384K → 512K 实测 | **NEXT TEST** | 决定大项目主 Agent 能否成立，以及是否撞 memory/KV gate |
| 3 | Coding Quality + Real Tool Loop | **NEXT TEST** | 决定“快”能否转成“生产有效” |
| 4 | C=2/4 Agent 并发 | **NEXT TEST** | 决定 Multi-Agent Worker Node 是否成立 |
| 5 | Long-session / Recovery | **NEXT TEST** | 决定 Resident / Autonomous 能否成立 |
| 6 | Split AI / Dev Roles | OPTION | 如果 inference 与 build/workspace 瓶颈适合分主机承担，再升级为正式拓扑建议 |
| 7 | 1× → 2× GX10 | **TRIGGERED OPTION** | 必须等真实 memory/KV 或并发 QoS Hard Gate 触发 |

## 什么时候第二台 GX10 才从 OPTION 变成 ACTION

至少满足下面一种真实触发条件：

1. **384K/512K 首方实测明确撞到 memory/KV Blocking Gate**；或者
2. **目标 C=2/4 Agent workload 出现持续 QoS degradation**；

并且还要通过反事实检查：

> 换模型 / 换 Variant / Runtime 优化 / Context Strategy / Routing / Role Reassignment 是否已经可以解决？

如果可以解决，硬件升级继续保持 OPTION，而不是 ACTION。

## 第二台 GX10 能解决什么 / 不能解决什么

| 可能改善 | 不会自动解决 |
| --- | --- |
| 更多模型/容量放置空间 | 云端 Codex / Claude 模型延迟 |
| 任务级并行吞吐 | CPU-bound UE/C++ 编译 |
| 部分 memory/KV / 并发瓶颈 | Workspace NVMe 瓶颈 |
| 多 Agent 角色隔离 | 模型本身质量不足 |
| 同构节点扩展实验 | 单请求 TTFT 必然下降（需实际验证） |

## 为什么“加机器”不是默认答案

增加节点也会新增：

- 网络与 inter-node dependency；
- 调度和角色分配；
- 配置漂移；
- 节点故障与恢复；
- 运维复杂度；
- 功耗与空间成本。

因此 Recommendation 必须同时写 `Expected Gain / Does Not Solve / Residual Bottleneck / New Failure Domains`，不能只写“更快”。

## 下一轮最有价值的测试

1. Pure Prefill / TTFT；
2. 128K、256K、384K、512K Actual Context 性能 + memory/KV + stability；
3. Coding Quality；
4. 真实 repo search/edit/build/test/repair task suite；
5. C=2 / C=4；
6. 长会话 / restart / crash recovery；
7. 有数据后重新判断 2×GX10 与 Split Topology。

只有这些新事实进入 L1，L2/L3 的 Qualification 和升级建议才允许改变。
