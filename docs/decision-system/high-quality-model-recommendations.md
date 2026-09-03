# 高质量大模型候选推荐与当前硬件适配（2026-09-03）

> 这页回答：**现在有哪些质量高、经典或火爆的大模型值得进入你的本地 AI 测试池？在 1×GX10 / 2×GB10 / 4×GB10 / RTX PRO 6000 96GB 上，谁值得优先测，谁暂时不值得为了它买硬件？**
>
> 这里是 **Candidate Recommendation / 测试优先级**，不是 Production Recommendation。没有第一方质量、目标 Context、稳定性和真实 Coding Loop 证据的模型，Lifecycle 只能停在 `WATCH / CANDIDATE`。

## 先看结论

| 优先级 | Model / Variant | 为什么值得关注 | 当前最适合进入的角色 | 当前本地结论 |
| --- | --- | --- | --- | --- |
| **P0** | **Qwen3.8-27B NVFP4 mixed** | 已有 1×GX10 第一方性能与 Hardware Gate；当前 32K+256 最快 | Fast Local Worker / Inference Backend | **1×GX10 已 PERFORMANCE_QUALIFIED；质量/384K+仍 OPEN** |
| **P0** | **DeepSeek-V4-Flash-0731** | 官方 304B；Coding/Agent benchmark 很强；1M-context 路线；vLLM/SGLang + DSpark | Main Coding / Architect / Long-context Agent 候选 | **最值得进入下一轮跨硬件测试池之一；本仓尚无第一方质量/硬件资格** |
| **P0/P1** | **GLM-5.3-Flash** | 官方 320B total / 18B active；面向 coding/agentic/长上下文效率重构 | Coding Worker / Repo Agent / Long-context Agent | **2×低比特、4×高精度优先候选；本地仍 OPEN** |
| **P1** | **MiniMax-M3** | 官方约 428B total / 23B active；1M context；MSA；coding/agentic + multimodal | Long-context / Multimodal Coding / Research Agent | **更适合 4×GB10 资格测试；2×MXFP4 容量较紧** |
| **P2 / Reference** | **Kimi-K3** | 官方 2.8T / 104B active；1M；native MXFP4；长时 coding/agentic 定位 | Quality Flagship / Large-cluster Reference | **当前 1×/2×/4×GB10 与 PRO6000 都不是 native-weight 本地适配目标** |

`P0/P1/P2` 只表示**测试优先级**：P0=最值得尽快验证，P1=有硬件/时间后验证，P2=观察/参考。它不是质量总分，也不是购买优先级。

## 你当前硬件怎么选

| 硬件 | 第一优先 | 第二优先 | 不建议当前为了它硬上 | 原因 |
| --- | --- | --- | --- | --- |
| **1×GX10 / 128GB** | Qwen3.8-27B NVFP4 / FP8 | DeepSeek/GLM 的**单独低比特 Variant 可行性测试** | MiniMax-M3 full / Kimi-K3 | 现有 Qwen 已有第一方性能；300B+ 高精度权重容量不匹配单节点 |
| **2×GB10 / 256GB** | DeepSeek-V4-Flash **低比特 Variant** | GLM-5.3-Flash **低比特 Variant**；MiniMax-M3 MXFP4 容量验证 | Kimi-K3 native MXFP4 | 2 节点开始能容纳约 150~220GB 级低比特权重，但 runtime/KV/长 context 会继续吃内存 |
| **4×GB10 / 512GB** | DeepSeek-V4-Flash FP8/高质量 Variant | GLM-5.3-Flash FP8/高质量 Variant | Kimi-K3 native MXFP4 | 4 节点首次成为 300B~400B 级高质量开放模型的现实测试平台；MiniMax-M3 MXFP4 也更从容 |
| **RTX PRO 6000 96GB** | Qwen3.8-27B BF16/FP8 等中型高质量模型 | DeepSeek-V4-Flash 的 aggressive low-bit Variant 只做独立质量 Gate | GLM/MiniMax/Kimi 高质量 full-resident | 96GB 对 300B+ 模型只能依赖很低比特/Offload；“能跑”不等于“高质量档值得作为主 Agent” |

### 容量推理边界

下面只用于**筛选是否值得测**，不是运行实测：

- 304B 参数模型仅权重在 FP8 理论下限约 304GB；
- 320B 参数模型 FP8 理论下限约 320GB；4-bit 理论下限约 160GB；
- 428B 参数模型 4-bit 理论下限约 214GB；
- Kimi-K3 2.8T 参数 native MXFP4 仅权重理论量级约 1.4TB。

这些数值**不包含 runtime、KV cache、激活、通信 buffer、视觉模块、allocator 碎片等**，因此“权重算术上能放下”只能进入 `OPEN/CANDIDATE`，不能标成 Hardware QUALIFIED。

---

## P0 — Qwen3.8-27B：当前单 GX10 已有第一方性能锚点

官方 Qwen3.8 系列定位包含 coding、professional work、research 和 long-horizon agentic 增强；仓库当前真正已经测过的是 Qwen3.8-27B BF16 / FP8 / NVFP4 在 1×GX10 的 32K+256 warm Formal100。

当前 1×GX10 性能排序：

```text
NVFP4 > FP8 > BF16
```

但**第一方 Quality 仍 OPEN**。因此：

- `NVFP4`：当前 Fast Worker / Local Inference Backend **P0**；
- `FP8`：更值得作为“性能与质量平衡”候选进入 Quality Gate；
- `BF16`：继续保留 Classic / Quality Reference 角色；
- 下一步不是宣布 Qwen3.8 NVFP4 为“最佳 Coding 模型”，而是补 `Quality + 384K/512K + Real Tool Loop`。

官方入口：https://github.com/QwenLM/Qwen3.8

---

## P0 — DeepSeek-V4-Flash-0731：当前最值得补进大项目 Coding 候选池之一

官方模型页显示：

- 304B 参数；
- 0731 是正式 Flash release；
- 官方给出的 Terminal Bench、NL2Repo、DeepSWE、Toolathlon 等 Coding/Agent 指标很强；
- 支持 vLLM / SGLang；
- 有 DSpark speculative decoding；
- DeepSeek-V4 的技术路线明确面向 million-token context intelligence。

### 对当前硬件的建议

| Hardware | 当前判断 | 建议 |
| --- | --- | --- |
| 1×GX10 | 官方 FP8/BF16 full-resident **不适配容量**；低比特 Variant OPEN | 不把单 GX10 当官方高精度目标；只测明确量化 Variant |
| 2×GB10 | 官方 FP8 仍不够从容；低比特 Variant **P0 Candidate** | 优先测试 384K/512K、KV、TTFT、Decode、Quality |
| 4×GB10 | **P0 高质量本地候选** | 值得测试官方 FP8/高质量 Variant + DSpark + 长 context |
| PRO6000 96GB | 只能走 aggressive low-bit / offload 类路线 | 可以作为独立低比特实验；没有 Quality Gate 前不称“高质量主 Agent” |

**推荐角色：** Main Coding / Architect / Repo-scale Agent 候选。

官方来源：
- https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731
- https://arxiv.org/abs/2606.19348

---

## P0/P1 — GLM-5.3-Flash：非常值得看“高质量 + 高效率 + 长上下文”平衡

官方资料描述 GLM-5.3-Flash：

- 320B total / 18B active；
- 面向 coding / agentic / multimodal；
- 使用 sparse + linear attention 以降低长上下文 serving cost；
- 官方宣称在多项 benchmark/real-world workload 上超过 GLM-5.2，并逼近顶级闭源 coding/agentic 水平。

### 对当前硬件的建议

- **1×GX10**：高精度 full-resident 不现实；低比特 Variant 只做 OPEN 候选；
- **2×GB10**：4-bit/低比特版本非常值得进入 P0/P1 测试；
- **4×GB10**：更适合尝试 FP8/高质量 Variant，属于重点候选；
- **PRO6000 96GB**：高质量 full-resident 不现实；若压到很低比特，必须单独做 Quality Gate。

**推荐角色：** Fast Main Coding、Repo Agent、Long-context Coding Agent 候选。

官方来源：
- https://huggingface.co/zai-org/GLM-5.3-Flash
- https://huggingface.co/docs/transformers/main/en/model_doc/glm5_next

---

## P1 — MiniMax-M3：长上下文 / 多模态 Coding 值得进入 4×GB10 路线

官方资料显示 MiniMax-M3：

- 约 428B total / 23B active；
- 1M context；
- MiniMax Sparse Attention；
- Coding / agentic / cowork 是核心能力；
- 官方提供 vLLM、SGLang、Transformers、KTransformers，以及 MXFP4/MXFP8 本地部署路径。

对你当前硬件：

- 1×GX10：不作为 full-resident 目标；
- 2×GB10：MXFP4 权重容量算术上可能接近可行，但留给 runtime/KV 的空间很紧，尤其不适合先假定 1M；
- **4×GB10：P1 高价值测试候选**，更适合做 384K/512K/1M 长 context qualification；
- PRO6000 96GB：不作为 high-quality full-resident 候选。

**推荐角色：** Repo Analyst、Long-context Agent、Multimodal Coding/Research Agent。

官方来源：
- https://huggingface.co/MiniMaxAI/MiniMax-M3
- https://github.com/MiniMax-AI/MiniMax-M3
- https://www.minimax.io/blog/minimax-m3

---

## P2 / Reference — Kimi-K3：质量旗舰值得跟踪，但不是当前本地硬件适配模型

官方 Kimi-K3：

- 2.8T total / 104B active；
- 1M context；
- native vision；
- native MXFP4 weights / MXFP8 activations；
- 明确定位 long-horizon coding、knowledge work、reasoning。

但 2.8T 的 native MXFP4 权重，仅权重规模就远高于 4×GB10 的 512GB 聚合内存。因此当前判断是：

```text
Quality / Capability Reference: HIGH PRIORITY TO WATCH
Current Local Fleet Fit: UNSUITABLE for native full-weight deployment
```

不要因为它质量强就反推“为了 Kimi-K3 买 4 台 GX10”。这正是 Decision System 要阻止的错误购买链。

**推荐角色：** Cloud/API Quality Flagship、未来大型服务器/集群 Reference；不是当前本地采购 Trigger。

官方来源：
- https://huggingface.co/moonshotai/Kimi-K3
- https://github.com/MoonshotAI/Kimi-K3

---

## 当前建议的测试顺序

```text
1×GX10
  Qwen3.8-27B: Quality + 128K/256K/384K/512K

PRO6000 96GB
  Qwen3.8 high-quality reference
  DeepSeek-V4-Flash low-bit: separate Quality Gate

2×GB10
  DeepSeek-V4-Flash low-bit       P0
  GLM-5.3-Flash low-bit           P0/P1
  MiniMax-M3 MXFP4 capacity gate  P1

4×GB10
  DeepSeek-V4-Flash FP8/high-quality  P0
  GLM-5.3-Flash FP8/high-quality      P0
  MiniMax-M3 MXFP4 long-context       P1

Kimi-K3
  Watch/API/reference; current local fleet does not qualify
```

### 每个候选都必须走同一条资格链

```text
CANDIDATE
→ Runtime Gate
→ Formal5
→ Formal100
→ Quality Gate
→ Context-band Gate
→ Agent Workload Fitness
→ Coding Production Fitness
→ Production Recommendation
```

没有完成前，页面可以明确说“**推荐测试**”，但不能说“**生产推荐**”。

机器可读候选 Registry：[`model-intelligence/registry.json`](../../model-intelligence/registry.json)。
