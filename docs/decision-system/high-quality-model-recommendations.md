# 高质量大模型候选推荐与 GB10 / PRO6000 适配（2026-09-03）

> 这页回答：**现在有哪些质量高、经典或火爆的大模型值得进入本地 AI 测试池？1×GX10、2×GB10、4×GB10、RTX PRO 6000 96GB 分别最值得先测谁？**
>
> 这里是 **Candidate Recommendation / 测试优先级**，不是本仓 Production Recommendation。外部同型号硬件的公开实跑可以提高 Hardware Fit 的证据强度，但不能替代本仓自己的 Quality / Stability / Coding Production Qualification。

## 先看结论

| 优先级 | Model / Variant | 最值得关注的原因 | 1×GX10 | 2×GB10 | 4×GB10 | 当前角色 |
| --- | --- | --- | --- | --- | --- | --- |
| **P0** | **Qwen3.8-27B NVFP4 / FP8** | 本仓已有 Formal100 + Hardware Gate | **第一方已测 @32K** | OPEN | OPEN | 当前本地性能锚点 / Fast Worker |
| **P0** | **Qwen3.8-Flash-Next · RadixArk NVFP4** | 135GB；已有单 GB10 PLE streaming 与双 GB10 TP2 公开实跑；有 checkpoint-specific quality probes | **GOOD（外部同硬件）** | **GOOD（外部同硬件）** | OPEN | 当前最值得“不买新硬件先试”的大模型候选之一 |
| **P0** | **DeepSeek-V4-Flash-0731 official checkpoint** | Coding/Agent 官方指标强；官方 checkpoint 约 167GB；已有 **2×GB10 TP2 / 1M** 可复现实跑 | 不适合 full-resident | **GOOD（外部同硬件）** | OPEN | 2×GB10 Main Coding / Architect 首要候选 |
| **P1** | **GLM-5.3-Flash · LibertAI NVFP4** | ~181GiB；已有 **2×GB10 / 262K** 公开实跑；320B/18B-active、长上下文效率路线 | 不适合 full-resident | **GOOD（外部同硬件）** | OPEN | Coding / Repo / Long-context 候选 |
| **P1** | **GLM-5.3-Flash official FP8** | 已有 **4×GB10 / 1M** 公开实跑 | 不适合 | 不适合 full-resident | **GOOD（外部同硬件）** | 4×GB10 high-quality / 1M reference candidate |
| **P2** | **MiniMax-M3 official base** | 428B/23B-active、1M、MSA、多模态 Coding/Agent | 不适合 | 不适合 official base | 第三方 low-bit OPEN | 长上下文 / 多模态候选，暂无接受的同 GB10 证据 |
| **WATCH** | **Kimi-K3 native MXFP4** | 2.8T/104B-active、1M、frontier coding/agentic | 不适合 | 不适合 | 不适合 native full-weight | API / Future Large-cluster Quality Reference |

**当前最重要的变化：** 2×GB10 已经不是“理论上也许能跑大型模型”的状态。至少 DeepSeek-V4-Flash-0731 官方 checkpoint、Qwen3.8-Flash-Next NVFP4、GLM-5.3-Flash NVFP4 都已经存在公开的同硬件部署证据；但这些仍属于 **Reproducible External Evidence**，不是本仓第一方结果。

---

## 四级证据必须分开看

| 证据级别 | 含义 | 当前例子 |
| --- | --- | --- |
| **First-party measured** | 本仓自己在目标硬件、固定合同下跑过 | Qwen3.8-27B BF16 / FP8 / NVFP4 @ 1×GX10 |
| **Reproducible same-hardware external** | 有公开 recipe / config / measured result，且硬件就是 GB10 / DGX Spark / GX10 | DeepSeek V4 @2×GB10、Qwen Flash Next NVFP4 @1×/2×GB10、GLM NVFP4 @2×GB10 |
| **Official/vendor model evidence** | 原厂模型卡、benchmark、架构、上下文、部署框架 | DeepSeek / Qwen / GLM / MiniMax / Kimi 官方资料 |
| **Capacity arithmetic only** | 参数量/文件大小与内存的筛选计算 | “权重看起来放得下”但没实际启动的组合 |

固定边界：

```text
外部同硬件跑通
!= 本仓第一方 Qualification

同硬件跑得快
!= Coding Quality 已证明

不同 benchmark 的 tok/s
!= 可以直接横向排名

权重放得下
!= KV / 512K / 1M / 并发一定放得下
```

---

# 1×GX10：现在最值得先做什么

## P0-A：继续完成 Qwen3.8-27B 第一方闭环

当前已经有：

- BF16 / FP8 / NVFP4 Formal100；
- 32K+256 warm C=1；
- NVFP4 Runtime/Hardware Gate；
- NVFP4 在当前合同下性能最好。

下一步应该补：

1. BF16 / FP8 / NVFP4 **Quality Gate**；
2. 128K → 256K → 384K → 512K Actual Context；
3. Pure Prefill、Peak Memory / KV；
4. Real Coding Tool Loop。

这条线的价值是形成**完全属于本仓的一方基线**。

## P0-B：Qwen3.8-Flash-Next RadixArk NVFP4 — 不增加节点就值得立即验证

这是本轮深审后价值明显上升的一条路线。

第三方 RadixArk checkpoint：

- 约 **135GB**；
- routed experts 使用 NVFP4；PLE 使用 FP8；部分敏感路径保留高精度；
- checkpoint 页面给出了 GSM8K / AIME26 等量化后质量 probe 和完整性审计；
- 因总 checkpoint 大于单 GB10 可用统一内存，公开单-Spark recipe 使用 **PLE 从 NVMe streaming / mmap**，将 resident 部分压到可运行范围。

已经存在同硬件公开实测：

- 1× DGX Spark / GB10；
- 262K context；
- PLE 从 NVMe 流式读取；
- 公共 recipe 报告单流大约 21~31 tok/s（配置不同）；
- 另一个面向 coding 的 serving profile 报告五语言 mixed-code median 约 32.4 tok/s，并给出 HumanEval / HumanEval+ Mini 结果。

**解释：** 这些数字不能直接和本仓 Qwen3.8-27B 的 9.081 tok/s 比，因为 prompt/output/runtime/speculative-decoding 合同不同；但它们足以把这条路线从“理论候选”提升为 **1×GX10 高优先复现候选**。

公开来源：

- https://huggingface.co/RadixArk/Qwen3.8-Flash-Next-NVFP4
- https://github.com/maci0/qwen3.8-flash-next-spark
- https://huggingface.co/sayyidfareed/Qwen3.8-Flash-Next-Code-Turbo-Spark

### 对硬件升级决策的影响

如果单 GX10 通过 PLE streaming 就能在 256K 级工作上下文上达到可接受的 Coding Agent 质量与等待感，那么“必须先买第二节点”这一结论会被削弱。它应该先经过本仓复现，再决定是否需要 scale-out。

---

# 2×GB10：现在最值得测试的三条主线

## P0-1：DeepSeek-V4-Flash-0731 官方 checkpoint

这是本轮最大的修正。

### 之前的错误

之前用：

```text
304B × FP8 ≈ 304GB
```

推断 2×GB10 256GB 放不下官方 checkpoint。

这个推导对**实际发布 checkpoint**不成立。

### 官方 checkpoint 实际情况

官方 Hugging Face 仓库当前约 **167GB**。其 `config.json` 同时显示：

- `expert_dtype = fp4`；
- quantization config 使用 FP8 路径；
- max position embeddings = 1,048,576；
- 包含 DSpark speculative module。

因此应称它为**官方 mixed-precision checkpoint**，不能再简称“纯 FP8 304GB”。

更重要的是，已经有公开可复现的：

- exact official HF revision；
- **2× DGX Spark / GB10**；
- TP=2 / RoCE；
- 1M model length；
- DSpark speculative decoding；
- realistic sampled/max coding、C=1、forced 8K output；
- 报告 median decode 约 **52 tok/s**。

公开来源：

- https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731
- https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731/tree/main
- https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731/blob/main/config.json
- https://github.com/m9e/deepseek-v4-flash-0731-2x-dgx-spark

**当前判断：2×GB10 的 DeepSeek-V4-Flash-0731 不再是“low-bit capacity guess”，而是有 same-hardware reproducible evidence 的 P0 官方 checkpoint 候选。**

但本仓仍要重新跑：Runtime Gate → Formal5 → Formal100 → Quality → 384K/512K/1M → Coding Tool Loop。

---

## P0-2：Qwen3.8-Flash-Next RadixArk NVFP4

公开同硬件证据比之前预计成熟得多。

RadixArk NVFP4：约 **135GB**。公开 2×Spark recipe 报告：

- 2×GB10；
- TP=2 over RoCE；
- 262,144 context；
- 30-minute soak；
- 单流约 **41~42 tok/s**；
- 8 并发 aggregate 约 **153 tok/s**；
- MTP/NEXTN speculative decoding。

另有公开研究仓库报告 2×Spark 路线上已经把 NVFP4 profile 推到更长 context，包括 1M-context serving experiments。

来源：

- https://huggingface.co/pocharlies/Qwen3.8-Flash-Next
- https://github.com/maci0/qwen3.8-flash-next-spark
- https://github.com/x00byte/Qwen3.8-Flash-Dual-Spark-Recipe

**当前判断：** 这是 2×GB10 上“高效率 Coding / Repo Agent”非常强的 P0 测试候选，尤其值得和 DeepSeek-V4-Flash 做同合同比较。

---

## P1：GLM-5.3-Flash LibertAIDAI NVFP4

官方 GLM-5.3-Flash 是 320B total / 18B active，采用 sparse + linear attention，面向 coding、agentic、multimodal 和长上下文效率。

LibertAIDAI 的 third-party NVFP4-A16 checkpoint：

- 约 **181GiB / 195GB repo**；
- 97% 参数所在的 routed-expert FFN 量化为 NVFP4；
- attention、vision、shared expert、MTP、embedding 等敏感部分继续高精度；
- 发布量化 provenance / partition verification / round-trip cosine。

公开 2×GB10 recipe 已报告：

- TP=2；
- 262K context；
- MTP；
- TTFT 约 0.29s（其测试合同）；
- Decode 约 **21.8 tok/s**（FP8 KV + MTP-4）。

来源：

- https://huggingface.co/LibertAIDAI/GLM-5.3-Flash-NVFP4
- https://github.com/tonyd2wild/GLM-5.3-Flash-NVFP4-262K-2x-DGX-Spark
- https://forums.developer.nvidia.com/t/glm-5-3-flash-nvfp4-on-2x-dgx-spark-vllm-tp-2-docker-compose/381541

这使 GLM-5.3-Flash NVFP4 从“2×容量推测”升级为 **same-hardware reproducible candidate**。但量化后的 Coding Quality 仍必须单独测。

---

# 4×GB10：什么时候真正有意义

4× 不应该因为“更多就是更好”自动推荐。

目前最清晰的外部证据之一是 **GLM-5.3-Flash native/official FP8 on 4× DGX Spark**：公开 recipe 报告 TP=4、1M context、约 30~43 tok/s 区间（不同 workload/config）。

这说明 4×GB10 的确可以进入“300B 级高精度 + 1M context”平台能力，但它仍不能证明：

- 对你的 Coding Task Suite 比 2×DeepSeek/Qwen 更高生产率；
- 4×的边际收益值得额外成本；
- 多节点复杂度、恢复、网络、维护成本可接受。

来源：

- https://github.com/Wpnx330/GLM-5.3-Flash-FP8-4x-DGX-Spark
- https://forums.developer.nvidia.com/t/glm-5-3-flash-on-4x-dgx-spark-30-43-tok-s-1m-context-uncensored-multimodal-cuda-graphs-on/381543

因此 4×仍然应该经过：

```text
2× workload bottleneck
→ 证明瓶颈不可由模型/runtime/context strategy解决
→ 4×同合同对照
→ Scaling Efficiency / Useful Engineering Work per Hour
→ 才决定是否值得升级
```

---

# RTX PRO 6000 96GB

当前最有价值的作用仍然是：

1. Qwen3.8-27B BF16 / FP8 / NVFP4 质量与性能对照；
2. 中等规模高质量模型 CUDA 主机；
3. 对超大模型只做明确的 aggressive low-bit / offload 实验。

DeepSeek official 167GB、Qwen Flash Next NVFP4 135GB、GLM NVFP4 ~181GiB 都超过 96GB full-resident 容量。即使 offload 能启动，也必须单独评价等待成本，不能因为“能跑”就作为主 Agent 推荐。

---

# MiniMax-M3 与 Kimi-K3

## MiniMax-M3 — P2 Candidate

官方支持：约 428B total / 23B active、1M context、MSA、native multimodality、Coding / Agentic / Cowork。

本轮没有接受到足够强的 same-GB10 evidence，因此对当前 fleet 仍保持：

- official base：1×/2×/PRO6000 不适合 full-resident；
- 4×GB10：只允许独立 third-party low-bit candidate；
- 不继承官方 base 的 Quality Qualification。

来源：

- https://huggingface.co/MiniMaxAI/MiniMax-M3
- https://www.minimax.io/models/text/m3
- https://www.minimax.io/blog/minimax-m3

## Kimi-K3 — WATCH / Quality Reference

官方：2.8T total / 104B active、1M context、native MXFP4 weights / MXFP8 activations。

当前 native full-weight 远超 4×GB10 聚合内存，所以继续作为 API / future large-cluster quality reference，不作为当前采购 trigger。

来源：

- https://huggingface.co/moonshotai/Kimi-K3
- https://arxiv.org/abs/2607.24653

---

# 当前建议的真实测试顺序

## 已有 1×GX10

```text
A. Qwen3.8-27B
   Quality Gate
   128K → 256K → 384K → 512K

B. Qwen3.8-Flash-Next RadixArk NVFP4
   先复现单 GX10 PLE streaming / 262K
   再做本仓 Formal5 / Formal100 / Quality / Coding Loop
```

**B 是本轮新增加的“先不买硬件也能获得明显能力跃迁”的候选。**

## 2×GB10

```text
P0-1 DeepSeek-V4-Flash-0731 official checkpoint
P0-2 Qwen3.8-Flash-Next RadixArk NVFP4
P1   GLM-5.3-Flash LibertAIDAI NVFP4
```

这三条都已经有 same-hardware external evidence，所以第一方测试应该优先做**同合同横向对照**，而不是再证明“它们能不能启动”。

## 4×GB10

优先回答“2×已经哪里不够”，再决定是否测试：

- GLM-5.3-Flash official FP8 @1M；
- DeepSeek / Qwen 更高并发、更大 KV 或模型路由；
- 4× scaling efficiency。

---

# 统一资格链

无论外部证据多强，进入本仓仍按：

```text
CANDIDATE
→ Runtime Gate
→ Formal5
→ Formal100
→ Quality Gate
→ Context-band Gate
→ Agent Workload Fitness
→ Real Coding Tool Loop
→ Coding Production Fitness
→ Production Recommendation
```

**External evidence 用来节省试错时间，不用来跳过第一方资格链。**

机器可读候选：[`model-intelligence/registry.json`](../../model-intelligence/registry.json)。
