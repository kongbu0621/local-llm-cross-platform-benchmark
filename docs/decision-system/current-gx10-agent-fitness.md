# 当前实例：1×GX10 + Qwen3.8-27B NVFP4 — Agent Workload Fitness

本页把 L2 设计真正实例化。基线只使用当前已归档的一方性能证据：1× ASUS GX10 / NVIDIA GB10、Qwen3.8-27B NVFP4 mixed、vLLM 0.28.0、32,768 input + 256 output、Concurrency=1、1 warmup 后主批次。

当前 Formal100：Effective Prefill≈1300.614 tok/s、TTFT≈25.194s、TPOT≈110.122ms/token、Decode≈9.081 tok/s、E2E≈53.275s、100/100 completed。质量、128K+ context、多并发、24h soak 等仍未完成，因此下表严格区分“性能已测”和“生产适配仍开放”。

## 当前适配度

| Agent Workload | Qualification | Current Fitness | Recommendation Confidence | 主要依据 | Blocking Gate / Open Gate |
| --- | --- | --- | --- | --- | --- |
| Interactive Assistant @32K short-output | CONDITIONAL | EXCELLENT | MEDIUM | 32K TTFT/Decode/E2E 与 100/100 批次稳定性已测 | 回答质量/真实交互质量未测 |
| Coding Worker @32K short-output | CONDITIONAL | GOOD | MEDIUM | 性能与短输出批次稳定性足以支持快速 worker 候选 | Coding quality、真实 repo edit/tool loop 未测 |
| Repo Analyst @384K+ | OPEN | — | OPEN | 32K Effective Prefill 较好，只能说明低 context 基础 | 384K/512K context、memory/KV、长输入稳定性未测 |
| RAG Agent @32K | CONDITIONAL | GOOD | LOW | Prefill/TTFT 对检索后上下文注入有基础 | retrieval pipeline、prefix/cache、并发、质量未测 |
| Research Agent | OPEN | — | OPEN | 单次模型性能已知 | browser/tool loop、长任务、长上下文、质量未测 |
| Browser Agent | OPEN | — | OPEN | 本地模型性能可作为候选 backend | 浏览器工具、网页/视觉、任务恢复未测 |
| Planner / Reasoner @32K | CONDITIONAL | GOOD | LOW | NVFP4 Decode/E2E 在当前三档最好 | reasoning quality 未测；速度不能代替推理质量 |
| Knowledge / Local Memory Agent | OPEN | — | OPEN | 本地部署和 32K 输入处理具备基础 | RAG+DB+embedding、长 context、常驻内存未测 |
| Long-running Autonomous Agent | OPEN | — | OPEN | 当前只有 100-request warm batch | 24h soak、context drift、crash/recovery、service continuity 未测 |
| Multi-Agent Worker Node | OPEN | — | OPEN | 单 Agent C=1 已测 | C=2/4/N、KV/内存压力、QoS、调度公平性未测 |
| 7×24 Resident Agent | OPEN | — | OPEN | Linux AI node 形态适合进入候选 | 长稳、watchdog、断电/重启恢复、常驻服务未测 |
| Local Inference Worker Node @32K | QUALIFIED | EXCELLENT | HIGH | 32K NVFP4 performance + 100/100 + Runtime/Hardware Gate | 结论只限当前已测 workload，不外推 128K+ |

`OPEN` 不等于差；它表示当前证据不足以跨越关键 Hard Gate。`CONDITIONAL` 表示已有部分生产相关证据，但仍存在未关闭的重要条件。只有满足目标 workload 的 Blocking Gates 后才允许提升为 `QUALIFIED`。

## 当前主要瓶颈判断

在当前 32K+256 workload 中，NVFP4 Decode 已明显加速，TTFT 在 E2E 中占比约 47%。因此下一阶段单请求优化的优先观察方向从“只追 Decode”转向 `Pure Prefill / TTFT`。这只是一条当前 workload 下的瓶颈迁移结论，不代表更长 context 时瓶颈仍相同。

## 当前改善路线

1. **不买硬件先补证据**：Pure Prefill、128K/256K/384K/512K、Peak Device/Host/KV、long-output、quality；
2. **Runtime/Workload 优化**：Prefill/TTFT、context strategy、cache/prefix reuse（另开 comparison mode）；
3. **真实 Agent Gate**：Coding quality + repo tool loop；
4. **并发 Gate**：C=2/4/N 后再判断 Multi-Agent Worker Node；
5. **长期 Gate**：soak / restart / recovery 后再判断 Resident/Autonomous；
6. **硬件扩展只作为 Triggered Option**：若 384K/512K 出现 memory/KV blocking gate，或目标并发出现持续 QoS degradation，再评估 2×同构节点。

## 当前角色建议

目前证据最强的角色是：**Local Inference Worker / Fast Agent Backend @32K**。

`Main Large-Project Coding Agent @384K/512K`、`Multi-Agent Host`、`7×24 Autonomous Agent` 当前均不得标记为已验证生产角色。
