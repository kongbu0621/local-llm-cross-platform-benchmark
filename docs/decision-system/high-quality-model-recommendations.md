# 高质量大模型候选推荐与当前硬件适配（2026-09-03）

> 这页回答：**现在有哪些质量高、经典或火爆的大模型值得进入你的本地 AI 测试池？在 1×GX10 / 2×GB10 / 4×GB10 / RTX PRO 6000 96GB 上，谁最值得优先测？**
>
> 这里是 **Candidate Recommendation / 测试优先级**，不是 Production Recommendation。外部官方 benchmark 是重要候选证据，但不是本仓第一方 Quality / Runtime / Context / Agent / Production 资格。

## 先看结论

| 优先级 | Model / Variant | 为什么值得关注 | 当前最适合的候选角色 | 当前本地结论 |
| --- | --- | --- | --- | --- |
| **P0** | **Qwen3.8-27B NVFP4 / FP8** | 已有 1×GX10 第一方 Formal100 与 Hardware Gate | Fast Local Worker / Inference Backend | **当前唯一已 first-party performance-qualified 的模型族；Quality / 384K+ 仍 OPEN** |
| **P0** | **Qwen3.8-Flash-Next** | 官方 125B main + 51B n-gram embedding、6B active；原生 262K、可扩展 1M；Coding/Agent 外部指标很强 | 2×GB10 Fast Main Coding / Repo Agent / Long-context Candidate | **比 300B+ 模型更贴近 2×GB10 的现实容量；但本仓 Runtime / KV / Quality 仍 OPEN** |
| **P0** | **DeepSeek-V4-Flash-0731** | 官方模型卡 304B；Coding/Agent benchmark 强；1M context；vLLM/SGLang/DSpark | Main Coding / Architect / Repo-scale Agent | **2×低比特、4×官方 FP8 容量候选；GB10 分布式运行仍未验证** |
| **P1** | **GLM-5.3-Flash** | 官方 320B total / 18B active；sparse+linear attention；Coding/Agent/长上下文效率取向 | Coding / Repo / Long-context Agent | **2×低比特、4×FP8 容量候选；本地 Runtime / Quality 仍 OPEN** |
| **P1** | **MiniMax-M3** | 官方约 428B / 23B active；1M context；MSA；multimodal + coding/agentic | Long-context / Multimodal Coding / Research | **官方 base 对当前 fleet 太大；4×GB10 可研究独立 low-bit variant，但不是官方 MXFP4 已验证结论** |
| **P2 / Reference** | **Kimi-K3** | 官方 2.8T / 104B active；1M；native MXFP4；长时 Coding/Agent flagship | Cloud/API Quality Flagship / Future Large-cluster Reference | **官方 HF 仓库约 1.56TB；当前 1×/2×/4×GB10 与 PRO6000 都不适合 native full-weight** |

`P0 / P1 / P2` 是**测试优先级**，不是质量总分，也不是购买顺序。

## 证据怎么读

当前候选同时存在三种证据，不得混写：

| 证据 | 含义 |
| --- | --- |
| **First-party measured** | 本仓自己在目标硬件上跑过，当前只有 Qwen3.8-27B 三档性能链达到这一层 |
| **Official vendor evidence** | 模型厂商公开模型卡 / benchmark / deployment docs；可证明“值得测”，不能证明你的 GX10 已适配 |
| **Capacity arithmetic** | 参数量 × bit-width 的权重下界；只用于排除明显不可能或筛选候选，不能证明 Runtime / KV / Context / Speed |

因此：

```text
外部模型很强
!= 目标 GB10 已经好用

权重放得下
!= 长上下文放得下

Runtime 能启动
!= Coding Production Qualified
```

---

## 当前硬件优先顺序

| 硬件 | P0 | P1 | 暂不值得为了它买硬件 |
| --- | --- | --- | --- |
| **1×GX10 / 128GB** | Qwen3.8-27B：Quality + 128K→512K；Qwen3.8-Flash-Next 的明确 low-bit/offload 可行性 | DeepSeek / GLM 明确 low-bit variant 的 Runtime Gate | MiniMax-M3 official base、Kimi-K3 |
| **2×GB10 / 256GB** | **Qwen3.8-Flash-Next official FP8**；DeepSeek-V4-Flash low-bit | GLM-5.3-Flash low-bit；MiniMax-M3 independent low-bit capacity gate | Kimi-K3 native MXFP4 |
| **4×GB10 / 512GB** | **DeepSeek-V4-Flash-0731 official FP8 capacity candidate**；Qwen3.8-Flash-Next FP8 | GLM-5.3-Flash FP8 capacity candidate；MiniMax-M3 low-bit long-context candidate | Kimi-K3 native MXFP4 |
| **RTX PRO 6000 96GB** | Qwen3.8-27B BF16/FP8/NVFP4 quality comparison | Qwen Flash Next / DeepSeek 的 aggressive low-bit or offload experiments | 300B+ high-quality full-resident 方案 |

这里的 `official FP8 capacity candidate` 只表示**权重规模在聚合内存上有希望**；仍必须验证 GB10 的 distributed runtime、通信、KV、Actual Context、TTFT、Decode 和稳定性。

---

## 容量筛选边界

只做候选筛选，不冒充实测：

- Qwen3.8-Flash-Next：官方架构为 **125B main + 51B n-gram embeddings**，6B active/token；官方有 FP8 variant。按 1 byte/param 粗略估计，权重级别明显更适合 **2×GB10 256GB** 进入正式 Runtime/Context Gate，但 runtime/KV 仍占空间；
- DeepSeek-V4-Flash-0731：官方模型卡按 **304B** 计；FP8 权重下界约 304GB，因此 1×/2×GB10 无法作为官方 FP8 full-resident 目标，4×GB10 只是容量候选；
- GLM-5.3-Flash：320B；FP8 下界约 320GB，4-bit 下界约 160GB；
- MiniMax-M3：428B；4-bit 下界约 214GB，但官方 base checkpoint 与“某个第三方 4-bit/MXFP4 variant”必须分开评价；
- Kimi-K3：2.8T native MXFP4，4-bit 理论下界约 1.4TB；官方 HF repo 当前约 1.56TB，更直接说明 4×GB10 512GB 不是 native full-weight 目标。

不同厂商对“参数量”是否包含额外 embedding / draft head / vision 模块的统计口径可能不同。**容量决策优先使用目标模型自己的官方模型卡与实际文件规模，不跨厂商表格混用参数数。**

---

# P0 — Qwen3.8-27B：当前单 GX10 第一方锚点

本仓已有 BF16 / FP8 / NVFP4 mixed 在 1×GX10 的 32K+256 warm Formal100。

当前性能排序：

```text
NVFP4 > FP8 > BF16
```

但这只是**性能**。下一步真正有价值的是：

1. BF16 / FP8 / NVFP4 **Quality Gate**；
2. 128K → 256K → 384K → 512K Actual Context；
3. Pure Prefill / Memory / KV；
4. Real Coding Tool Loop。

角色：

- NVFP4：Fast Worker / Local Inference Backend P0；
- FP8：性能-质量平衡候选；
- BF16：Quality / Precision reference。

官方来源：
- https://github.com/QwenLM/Qwen3.8
- https://huggingface.co/Qwen/Qwen3.8-27B

---

# P0 — Qwen3.8-Flash-Next：这轮复查后提升为 2×GB10 首要候选

这是上一版 shortlist 的一个明显遗漏，已经修正。

官方资料给出的关键点：

- 125B main model + 51B n-gram embeddings；
- 6B parameters activated per token；
- GDN + QSA sparse-attention 路线，专门降低长序列 attention 成本；
- n-gram embedding 可以设计为 host-memory offload；
- native context 262,144，官方描述可扩展到 1,000,000；
- 官方 benchmark 中 Coding、Agent、CoWork 相比 Qwen3.8-27B 有多项明显提升；
- 官方 Hugging Face 已提供 FP8 variant。

### 当前硬件判断

| Hardware | 判断 | 下一步 |
| --- | --- | --- |
| 1×GX10 | 官方 FP8 full-resident 不适配；low-bit/offload OPEN | 只测试明确 variant，不用配置上限推断 |
| **2×GB10** | **P0；官方 FP8 容量最值得优先验证** | Runtime → 256K → 384K/512K → Quality → Tool Loop |
| 4×GB10 | P0；容量更从容 | 重点看长 context / multi-agent / scaling 是否真的得到收益 |
| PRO6000 96GB | low-bit/offload OPEN | 不能把“能启动”当 high-quality main agent |

为什么它比 300B+ 模型更适合先测 2×GB10：**参数规模与激活规模都更贴近 256GB 聚合内存，而且官方目标本身就是 Coding + efficiency + long context。** 但这是候选排序，不是性能预测。

官方来源：
- https://github.com/QwenLM/Qwen3.8-Flash-Next
- https://huggingface.co/Qwen/Qwen3.8-Flash-Next
- https://huggingface.co/Qwen/Qwen3.8-Flash-Next-FP8

---

# P0 — DeepSeek-V4-Flash-0731：4×GB10 主 Coding / Architect 高质量候选

官方模型卡支持的事实包括：

- official Flash 0731 release；
- model card 304B；
- 1M context；
- Terminal Bench 2.1、NL2Repo、DeepSWE、Toolathlon 等 Agent/Coding benchmark 很强；
- 支持 vLLM / SGLang；
- bundled DSpark draft head / speculative decoding route。

### 当前硬件判断

| Hardware | 判断 |
| --- | --- |
| 1×GX10 | 官方 FP8 full-resident 不可能；低比特 OPEN |
| 2×GB10 | low-bit P0/P1 Candidate；必须单独 Quality Gate |
| **4×GB10** | **官方 FP8 权重容量 plausible，但 distributed runtime / KV / context 全部 OPEN** |
| PRO6000 96GB | aggressive low-bit/offload 实验，不是 high-quality full-resident 目标 |

推荐角色：Main Coding / Architect / Repo-scale Agent 候选。

官方来源：
- https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731
- https://api-docs.deepseek.com/quick_start/pricing/
- https://github.com/sgl-project/sglang/blob/main/docs/cookbook/autoregressive/DeepSeek/DeepSeek-V4.mdx
- https://arxiv.org/abs/2606.19348

---

# P1 — GLM-5.3-Flash：高效率 Coding / Agent / Long-context 候选

官方资料支持：

- 320B total / 18B active；
- natively multimodal；
- sparse + linear attention；
- 官方称相对 GLM-5.2 在 benchmark/real-world workload 上提升，并逼近高端闭源 Coding/Agent 水平；
- 官方本地部署入口包含 SGLang、vLLM、Transformers；
- NVIDIA 也提供 GLM-5.3-Flash FP8 的数据中心部署 recipe。

这说明它**值得测**，但 NVIDIA 在 H200/GB200 等目标上的 recipe 不能被转写成“4×GB10 已适配”。

当前路线：

- 2×GB10：独立 4-bit / low-bit variant P1；
- 4×GB10：FP8 capacity candidate P1；
- PRO6000：very-low-bit/offload only；
- 第一方 Runtime/Quality 前不升 Production Recommendation。

官方来源：
- https://huggingface.co/zai-org/GLM-5.3-Flash
- https://docs.nvidia.com/dynamo/dev/recipes/glm-5-3-flash
- https://huggingface.co/docs/transformers/main/en/model_doc/glm5_next

---

# P1 — MiniMax-M3：长上下文 / 多模态 Coding 候选，但修正量化语义

官方资料支持：

- ~428B total / ~23B active；
- 1M context；
- MiniMax Sparse Attention (MSA)；
- Coding / Agentic / Cowork + native multimodality；
- 官方提供 vLLM、SGLang、Transformers、KTransformers、Unsloth 等本地部署路径。

**本次复查修正：官方公开 README 并没有证明“官方 MXFP4/MXFP8 checkpoint”。** 所以之前把 `2×/4×GB10 MXFP4` 写得像官方模型路径是不严谨的。

现在统一改为：

```text
MiniMax-M3 official base
!=
third-party low-bit / 4-bit / MXFP4 variant
```

当前硬件：

- 1×GX10：official base 不适配；
- 2×GB10：third-party low-bit capacity gate，空间可能很紧；
- **4×GB10：third-party low-bit long-context candidate**，但必须重新走 Runtime + Quality；
- PRO6000：official base 不适配。

许可还需要注意：官方是 `minimax-community`，不是 MIT/Apache；进入真实交付前应单独检查商业使用条件。

官方来源：
- https://huggingface.co/MiniMaxAI/MiniMax-M3
- https://github.com/MiniMax-AI/MiniMax-M3
- https://www.minimax.io/models/text/m3
- https://www.minimax.io/blog/minimax-m3

---

# P2 / Reference — Kimi-K3：旗舰参考，不是当前本地采购 Trigger

官方资料：

- 2.8T total / 104B active；
- 1M context；
- native multimodality；
- MXFP4 weights / MXFP8 activations；
- 长时 Coding、Knowledge Work、Reasoning 是核心定位；
- 官方 HF repo 当前约 1.56TB。

因此：

```text
Quality / Capability Reference: 高价值
Current local native-weight fit: UNSUITABLE
```

不要从“Kimi-K3 很强”推导成“因此 4×GX10 值得为了 K3 买”。当前更合理用途是 Cloud/API Quality Reference 或未来更大内存服务器/集群参照。

官方来源：
- https://huggingface.co/moonshotai/Kimi-K3
- https://github.com/MoonshotAI/Kimi-K3
- https://www.kimi.com/en/blog/kimi-k3

---

## 当前测试顺序（复查后）

```text
1×GX10
  P0  Qwen3.8-27B: Quality + 128K/256K/384K/512K
  P1  Qwen3.8-Flash-Next: explicit low-bit/offload feasibility only

PRO6000 96GB
  P0  Qwen3.8-27B high-quality reference / quality comparison
  P1  Qwen Flash Next / DeepSeek low-bit experiments with independent Quality Gate

2×GB10
  P0  Qwen3.8-Flash-Next official FP8
  P0  DeepSeek-V4-Flash low-bit
  P1  GLM-5.3-Flash low-bit
  P1  MiniMax-M3 independent low-bit capacity gate

4×GB10
  P0  DeepSeek-V4-Flash official FP8 capacity/runtime/context qualification
  P0  Qwen3.8-Flash-Next FP8 long-context/scaling qualification
  P1  GLM-5.3-Flash FP8 qualification
  P1  MiniMax-M3 third-party low-bit long-context qualification

Kimi-K3
  P2  Watch / API / future large-cluster reference
```

### 所有候选必须走同一资格链

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

没有完成前，页面可以明确说“**推荐测试**”，不能写成“**生产推荐**”。

机器可读候选 Registry：[`model-intelligence/registry.json`](../../model-intelligence/registry.json)。
