# 高质量大模型候选推荐与 GB10 / PRO6000 适配（2026-09-03）

> **目标：** 不做“最新模型新闻榜”，而是回答：在 **1×GX10、2×GB10、4×GB10、RTX PRO 6000 96GB** 上，哪些高质量 Coding / Agent / Long-context 模型最值得投入第一方测试时间。
>
> **P0/P1/P2/WATCH 是验证优先级，不是质量总分、速度排行榜或购买顺序。** 外部同型号 GB10 的实跑用于降低试错成本，仍不能替代本仓自己的 Quality / Stability / Coding Production Qualification。

相关入口：

- [Model Intelligence 一页总览](model-intelligence-view.md)
- [Agentic Coding Evidence：真实编码循环外部证据](agentic-coding-evidence.md)
- [当前 GX10 Agent Fitness](current-gx10-agent-fitness.md)
- [当前大型 Coding Production Fitness](current-gx10-production-fitness.md)

---

# 一页结论

| Priority | Model / Variant | 1×GX10 | 2×GB10 | 4×GB10 | 为什么现在值得测 |
| --- | --- | --- | --- | --- | --- |
| **P0** | **Qwen3.8-27B BF16 / FP8 / NVFP4** | **FIRST-PARTY @32K** | OPEN | OPEN | 当前唯一已有本仓 Formal100 + Hardware Gate 的性能锚点；先补 Quality / 128K→512K / Coding Loop |
| **P0** | **Laguna-S-2.1 NVFP4** | **GOOD external** | 通常不需要先扩节点 | OPEN | 单 GB10 serving 成熟；外部真实 Agent Coding 86/86；官方定位就是 agentic coding / long-horizon work |
| **P0** | **Qwen3.8-Flash-Next RadixArk NVFP4** | **GOOD external，PLE streaming** | **GOOD external，TP2** | OPEN | 单/双 GB10 都已有实跑；适合大 Context + Fast Main Coding 候选 |
| **P0** | **Qwen3.8-Flash-Next UD-Q3_K_XL GGUF** | **GOOD external** | 未作为首要 TP2 Variant | OPEN | 同 GB10 Agent Coding **连续两次 86/86**；这是独立 Variant，不与 RadixArk/official FP8 串证据 |
| **P0** | **Qwen3.5-122B-A10B Hybrid INT4+FP8** | **GOOD external @256K** | 无需先扩节点 | OPEN | 成熟单 GB10 Classic/Sweet Spot；公开约 52–59 tok/s，不因“旧一代”自动淘汰 |
| **P0** | **DeepSeek-V4-Flash-0731 official mixed checkpoint** | full-resident 不适配；压缩 Variant另算 | **GOOD external，TP2** | **GOOD external，TP4** | 官方 Coding/Agent 信号强；2×GB10 已有 1M-serving 和接近 900K actual-prompt 外部证据 |
| **P1 / Classic** | **openai/gpt-oss-120b MXFP4** | **GOOD external** | 不需为了它扩节点 | OPEN | Agent / Tool-use / Reasoning 参考强；native 128K 限制 384K/512K 主 Repo 角色 |
| **P1** | **GLM-5.3-Flash LibertAIDAI NVFP4** | full-resident 不适配 | **GOOD external，512K profile** | **GOOD external，large-KV** | 2× 已有 440K needle byte-exact；对 384K/512K Repo Agent 很直接 |
| **P1** | **KAT-Coder-V2.5-Dev** | **GOOD external** | 不需要先扩节点 | OPEN | 35B/3B-active Coding Specialist；同 GB10 外部 Agent Coding 84/86 |
| **P1** | **nvidia/MiniMax-M3-NVFP4** | 不适配 | 250GB 对 2×过紧 | **GOOD external** | 4×已有 262K benchmark + 1M KV/serving；多模态/长上下文价值高 |
| **P1/P2** | **GLM-5.3-Flash exact official FP8** | 不适配 | full-resident 不适配 | **CONDITIONAL** | exact official Variant 不能继承 LibertAI/derived checkpoint 的数字 |
| **P2 / Classic Coder** | **Qwen3-Coder-30B-A3B-Instruct** | 容量轻松；外部高吞吐路线 | 不需扩节点 | OPEN | 30.5B/3.3B-active、native 256K、Apache-2.0、明确面向 Agentic Coding / Repo-scale |
| **P2 / NVIDIA Ref** | **Nemotron-3-Super-120B-A12B-NVFP4** | **GOOD external** | 不需扩节点 | OPEN | NVIDIA-native Agent/Long-context 参考；独立 GB10 Coding 证据不足以升 P0 |
| **P2** | **MiniMax-M3 community W4A16/GPTQ** | 不适配 | CONDITIONAL external | OPEN | 2×可行路线存在，但 aggressive quant 必须独立 Quality Gate |
| **WATCH** | **Kimi-K3 native MXFP4** | native 不适配 | native 不适配 | native 不适配 | Frontier/API/未来大集群参考；当前不构成 GX10 采购触发器 |

---

# 现在必须看 5 条证据轴

过去只看“模型质量 + tok/s”是不够的。当前正式按下面五层理解：

```text
1. Hardware Evidence
   exact Variant × exact topology 是否真的能 serve

2. Context Evidence
   configured / KV / actual prompt / retrieval depth

3. Quality Evidence
   coding / reasoning / instruction / tool-use 模型能力

4. Agentic Coding Evidence
   search / edit / tool / test / hidden-test / task completion

5. Production Qualification
   本仓真实大型项目 Coding Production Suite
```

固定边界：

```text
vendor benchmark != first-party Quality
same-GB10 serve PASS != first-party Hardware Qualification
configured 1M != 1M actual prompt
actual 1M prompt != 1M retrieval quality
agentic coding external PASS != Production Qualification
headline tok/s across different contracts != ranking
```

机器记录：

- Model / Variant / Hardware / Context：[`model-intelligence/registry.json`](../../model-intelligence/registry.json)
- Agentic Coding：[`model-intelligence/agentic-coding-evidence.json`](../../model-intelligence/agentic-coding-evidence.json)

---

# Context Evidence Matrix

对你最重要的是 **384K / 512K / 1M 到底实际证明到哪一步**。

| Model / Variant | Topology | Configured / serving envelope | Actual prompt / retrieval evidence | 当前能成立的结论 |
| --- | --- | --- | --- | --- |
| Qwen3.8-27B NVFP4 | 1×GX10 | 本仓当前正式结果 32K+256 | **32,768 input Formal100 first-party** | 32K 已测；128K+ OPEN |
| Laguna-S-2.1 NVFP4 | 1×GB10 | 公共稳定 profile 128K；non-spec / safer profile 可到约 250K/256K | 当前审计不把 full-256K deep prompt 当确定事实 | 高价值 128K/256K candidate；384K/512K 未证明 |
| Qwen3.5-122B Hybrid | 1×GB10 | 256K public serving | 未把 full-256K deep prompt 当本仓事实 | Mature 256K external candidate |
| Qwen3.8-Flash-Next RadixArk NVFP4 | 1×GB10 | 262K serving | headline speed 多为短 prompt | 262K capability 有证据，不等于 262K 性能曲线 |
| Qwen3.8-Flash-Next UD-Q3_K_XL | 1×GB10 | **65,536 in agentic runs** | 两次真实 Coding Loop 86/86 | Coding repeat signal 强，但只能覆盖 65K 级任务 |
| Qwen3.8-Flash-Next RadixArk NVFP4 | 2×GB10 | 262K soak；另有 1M serving profile | 深 prompt / retrieval 仍需统一合同 | 2× serving 成熟；1M Coding PASS 未成立 |
| **DeepSeek-V4-Flash-0731 official** | **2×GB10** | **1M model length / KV** | **公开 sweep 接受 899,994-token prompt**；另有 131K 详细 prefill/decode | 当前 2×GB10 最强 deep-input 外部证据之一；仍缺本仓 Quality / Coding Production |
| **GLM-5.3-Flash LibertAI NVFP4** | **2×GB10** | **512K standing profile** | **440K-token needle byte-exact** | 对 384K/512K Repo Agent 很直接 |
| nvidia/MiniMax-M3-NVFP4 | 4×GB10 | 262K benchmark + 1M KV/serving | 1M deep-prompt quality 未统一确认 | 4×大 KV/1M 平台候选，不等于 1M Coding PASS |
| gpt-oss-120b | 1×GB10 | **native 128K** | 公开 Agent / coding work，但不是 384K+ | Classic Agent reference；不满足主 Repo Context 目标 |
| Nemotron 3 Super NVFP4 | 1×GB10 | external 131K profile；vendor up to 1M | 外部报告至少约 100K depth 稳定 | Long-context reference；vendor 1M 不能写成 1M PASS |
| Kimi-K3 native | 当前 fleet | 官方 1M | native checkpoint 无法当前 1×/2×/4× full-resident | WATCH / API / future cluster |

---

# Agentic Coding Evidence Matrix

这层是本轮最终审计新增的关键。

同一外部 GB10 benchmark（4 个 Python coding tasks / 86 hidden tests）中：

| Model / Variant | Harness | Hidden tests | 重复情况 | 当前解释 |
| --- | --- | ---: | --- | --- |
| **DeepSeek-V4-Flash 压缩单机 Variant** | opencode | **86/86** | 1 run | 单 GB10 agent loop 能闭合；不是 official 2× checkpoint |
| **Laguna-S-2.1 NVFP4** | opencode | **86/86** | 1 run | P0 复现价值非常高；不能把单 run 当可靠性概率 |
| **Qwen3.8-Flash-Next UD-Q3_K_XL** | opencode | **86/86** | **连续 2 runs 都 86/86** | 当前找到的最有价值的单 GB10 重复 Agent Coding 信号之一 |
| Qwen3.8-27B NVFP4+MTP external | jaja | **86/86** | 1 run | 补充本仓性能链，但 harness 不同，wall-clock 不横比 |
| Qwen3.6-27B dense | opencode | **86/86** | 1 run | 做对但非常慢，说明 Capability != Production Fitness |
| **KAT-Coder-V2.5-Dev** | opencode | **84/86** | 1 run | Coding Specialist 候选 |
| Qwen3.6-35B-A3B NVFP4 | opencode | **最高 86/86** | 重复约 **64→67→86** | 非常快，但稳定性警告很强 |
| GLM-5.3-Flash UD-IQ1_S | opencode | 9/86 | 1 run | 9 分是 seed 自带；只证明这个 exact config 失败，不是 GLM 家族 verdict |

来源与机器明细见：[Agentic Coding Evidence](agentic-coding-evidence.md)。

## 这张表最重要的不是冠军

它证明：

```text
one run != reliability
```

并且：

```text
Agent harness
也是 Coding Production Configuration 的组成部分
```

同一模型更换 harness 后，任务是否成功都可能改变；甚至 context compaction、tool parser、turn budget 都能让本来有能力的模型失败。

所以本仓未来 L3 必须逐步记录：

- hidden-test pass；
- completed tasks；
- wall-clock / completed task；
- tool calls；
- retry count；
- human intervention；
- context compaction；
- regression；
- self-stop；
- run-to-run variance。

---

# 1×GX10：当前第一方复现顺序

## P0-1 — Qwen3.8-27B

原因：已经有本仓 Performance + Hardware Gate，边际成本最低。

下一步：

```text
Quality Gate
→ 128K
→ 256K
→ 384K
→ 512K
→ Pure Prefill / Memory / KV
→ Agentic Coding repeated suite
```

## P0-2 — Laguna-S-2.1 NVFP4

原因：

```text
118B/8B-active MoE
+ 官方 agentic-coding / long-horizon 定位
+ 单 GB10 runtime 成熟
+ external 86/86 real coding loop
```

它现在应进入**单 GX10 主 Coding Agent 第一方候选池**。

但公共 GB10 文档同时说明它有实际工程坑：旧 vLLM tool-call gibberish、DFlash/深 prefill 的 hard hang 风险、统一内存 OOM 可能拖死整机。因此 Stability / Recovery 反而很值得测。

来源：

- https://huggingface.co/poolside/Laguna-S-2.1
- https://huggingface.co/poolside/Laguna-S-2.1-NVFP4
- https://github.com/Reederey87/laguna-s-2.1-dgx-spark
- https://github.com/sudoingX/dgx-spark-laguna
- https://github.com/DG1001/local-agentic-coding-128gb

## P0-3 — Qwen3.8-Flash-Next 两条 Variant

### RadixArk NVFP4

适合验证：大 Context、PLE streaming、fast serving、2× scale-out。

### UD-Q3_K_XL GGUF

适合验证：真实 Agent Coding repeatability。外部相同四任务套件中两次连续 86/86，但配置只有 65K，所以不能代替 256K/512K 测试。

## P0-4 — Qwen3.5-122B-A10B Hybrid

成熟 256K Classic/Sweet Spot。模型新旧不是淘汰依据；**成熟度 + 同硬件证据 + 生产体验**本身是一条 Pareto 轴。

## P1 — DeepSeek V4 单机压缩 Variant

外部 Agent Coding 86/86 说明这条线不该只视为“能启动的奇技淫巧”；但 aggressive quant 的 harder-reasoning 质量代价仍需严格测，所以保持 P1，而不是直接抬到本地主 Agent 推荐。

## P1 — KAT-Coder-V2.5-Dev

35B/3B-active、Apache-2.0、明确 Agentic Coding 模型。外部单 GX10 84/86，值得作为 Coding Specialist 对照。

## P2 — Qwen3-Coder-30B-A3B-Instruct

30.5B/3.3B-active、native 262K、可扩展 1M、Apache-2.0，官方明确支持 Qwen Code / CLINE 等 agentic coding。它很适合保留为**轻量 Classic Coding Specialist**，但当前第一方测试优先级低于 Laguna / Qwen Flash Next / Qwen3.5。

---

# 2×GB10：第一批统一合同横比

```text
P0  DeepSeek-V4-Flash-0731 official mixed checkpoint
P0  Qwen3.8-Flash-Next RadixArk NVFP4
P1  GLM-5.3-Flash LibertAIDAI NVFP4
P2  MiniMax-M3 aggressive W4A16/GPTQ
```

真正要回答的不是“谁的社区 tok/s 最大”，而是同一母本下：

```text
256K / 384K / 512K / 1M
× Quality
× TTFT / Prefill / Decode / E2E
× Agent Coding repeated tasks
× Stability
× Memory/KV
```

---

# 4×GB10：必须由 2×的不可替代瓶颈触发

重点候选：

- `nvidia/MiniMax-M3-NVFP4`：4×已有 TP4 / 262K benchmark / 1M serving；
- GLM NVFP4：large-KV / 1M；
- DeepSeek official：更大的 KV / concurrency / model placement；
- Multi-Agent / 多模型常驻。

Upgrade Trigger 仍然是：

```text
2× first-party Coding Production workload
证明存在不可由 model / runtime / context strategy / routing 解决的
容量、KV、并发或角色放置瓶颈
```

否则 4×只是 OPTION，不是 ACTION。

---

# 最终固定语义

```text
Popularity != Quality
Quality != Hardware Fit
Hardware Fit != Context Fit
Context Fit != Agentic Coding Fit
Agentic Coding Fit != Coding Production Qualification
```

并继续坚持：

```text
Model Family != Model Variant
```

Official FP8、NVFP4、INT4、W4A16、GGUF、streaming、expert-pruned 都必须独立记录证据。

最终 Production Recommendation 仍只能来自：

```text
CANDIDATE
→ Runtime Gate
→ Formal5
→ Formal100
→ Quality Gate
→ Context-band Gate
→ Agentic Coding Repeatability
→ L2 Agent Workload Fitness
→ Long Session / Recovery
→ L3 Coding Production Fitness
→ Production Recommendation
```
