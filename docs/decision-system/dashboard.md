# Decision Dashboard — 三层结果一眼看懂

> **这是给人看的入口。** `results/*.json`、`assessments/*.json`、`recommendations/*.json` 是给程序、CI 和自动推荐器使用的机器记录；日常查看请优先从本页进入。

## 三层现在分别回答什么

| 层 | 人话 | 当前 GX10 状态 | 先看这里 | 机器记录 |
| --- | --- | --- | --- | --- |
| **L1 — FACT** | 这台机器真实测出了什么？ | 32K+256 Formal100 已有 BF16 / FP8 / NVFP4 实测 | [完整性能/稳定性详情](../results/qwen38-27b-gx10-20260903.md) | [`results/`](../../results/qwen38-27b-v1.0/gb10-01/) |
| **L2 — Agent Workload Fitness** | 适合承担哪些 Agent 工作？ | 32K Local Inference Worker 已验证；大型上下文/多 Agent/长时 Agent 仍 OPEN | [当前 GX10 Agent 适配表](current-gx10-agent-fitness.md) | [L2 JSON](../../assessments/agent/gx10-qwen38-nvfp4-32k-v1.json) |
| **L3 — Coding Production Fitness** | 能不能承担高强度大型项目编码生产？整套机器该怎么配？ | **OPEN**；当前只证明快速本地推理 worker 候选，还没有资格宣称“大项目主 Coding Agent” | [当前大型编码生产适配](current-gx10-production-fitness.md) | [L3 JSON](../../assessments/production/gx10-qwen38-nvfp4-large-coding-v1.json) |

横向输入与输出：

- **Model Intelligence**：哪些经典/旗舰/甜点/编码/长上下文/热门模型值得进入测试池；[人类可读模型视图](model-intelligence-view.md)。
- **Recommendation / Upgrade Roadmap**：现在该优化软件、补测试、换模型、加节点还是不买硬件；[当前路线图](current-gx10-roadmap.md)。

---

## L1 — 当前真实测到了什么

当前共同合同：**1× GX10 / GB10，Qwen3.8-27B，32,768 input + 256 output，Concurrency=1，1 warmup 后主批次。**

| Precision | Effective Prefill* | TTFT | TPOT | Decode | E2E | Completion |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BF16 | 936.453 tok/s | 34.992 s | 252.447 ms/token | 3.961 tok/s | 99.366 s | 100/100 |
| FP8 | 1187.130 tok/s | 27.603 s | 156.783 ms/token | 6.378 tok/s | 67.582 s | 100/100 |
| **NVFP4** | **1300.614 tok/s** | **25.194 s** | **110.122 ms/token** | **9.081 tok/s** | **53.275 s** | **100/100** |

\* Effective Prefill 是 `input_tokens / TTFT` 的派生值，不是 Pure Prefill `pp_tps`。Pure Prefill 当前仍未单独测量。

**能成立：** 当前 warm 32K+256 workload 下，NVFP4 综合执行效率最好；三档 Formal100 都完成 100/100。

**不能外推：** 384K/512K 是否好用、Coding 质量是否够高、能否同时跑多个 Agent、能否 7×24、能否承担完整大型项目 Coding Production。

---

## L2 — 当前 GX10 对各种 Agent 到底适不适合

| Agent Workload | Qualification | 当前适配度 | 一句话结论 |
| --- | --- | --- | --- |
| Local Inference Worker @32K | **QUALIFIED** | **EXCELLENT** | 当前证据最强的角色 |
| Interactive Assistant @32K | CONDITIONAL | EXCELLENT | 性能很好，但真实回答质量未测 |
| Coding Worker @32K | CONDITIONAL | GOOD | 快速 Coding Worker 候选；真实 repo tool-loop/质量未闭环 |
| RAG Agent @32K | CONDITIONAL | GOOD | 有基础；retrieval/cache/并发/质量仍未测 |
| Planner / Reasoner @32K | CONDITIONAL | GOOD | 性能合适，但 reasoning quality 不能用速度代替 |
| Repo Analyst @384K+ | **OPEN** | — | 384K/512K、memory/KV 尚未实测 |
| Research / Browser Agent | **OPEN** | — | tool/browser/长任务/质量证据不足 |
| Multi-Agent Worker Node | **OPEN** | — | C=2/4/N 尚未测 |
| Long-running Autonomous | **OPEN** | — | 长时、context drift、crash/recovery 尚未测 |
| 7×24 Resident Agent | **OPEN** | — | watchdog、重启/断电恢复、常驻稳定性尚未测 |

`OPEN` 不是“差”，而是**证据不足，暂时禁止评分**。

---

## L3 — 高强度大型项目编码目前的结论

> **Qualification = OPEN；Fitness = 未评分。**
>
> 当前 1×GX10 + Qwen3.8-27B NVFP4 已证明它可以是一个很快的本地 AI inference / worker 节点，但还没有证据把它升级成“高强度大型项目主 Coding Agent / 完整 Coding Production System”。

| Blocking Gate | 当前 | 为什么重要 |
| --- | --- | --- |
| 384K / 512K Large Context | **OPEN** | 大型仓库主 Agent 的实际工作上下文尚未验证 |
| Coding Production Quality | **OPEN** | correctness、repo understanding、patch minimality、regression avoidance、scope control 未测 |
| Real Tool Loop | **OPEN** | search → edit → diff → build → test → repair 没跑真实任务套件 |
| Long Session / Recovery | **OPEN** | 长会话、重启、crash recovery、constraint retention 未测 |
| Execution Placement | **OPEN** | inference / workspace / build / test / repo / control 最终放在哪里还需绑定并实测 |

当前最合理的角色分工是：**GX10 先作为本地 AI worker / inference node 候选，而不是先假定它必须成为所有开发工作都在本机完成的 monolithic coding workstation。**

---

## 当前一句话路线

**现在不把“买第二台 GX10”升级成行动。** 先补 Pure Prefill、384K/512K、Coding Quality、真实 Tool Loop、C=2/4、长时/恢复；只有真实证据触发 memory/KV 或并发 QoS Hard Gate，且模型/runtime/context strategy 无法替代时，2×同构节点才从 OPTION 升级为 ACTION。
