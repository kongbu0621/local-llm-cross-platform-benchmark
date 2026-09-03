# Model Intelligence — 高质量模型、Variant、Context、Agent Coding 与硬件证据

> **给人看的 Model Intelligence 入口。** 这里不做“模型新闻榜”，而是回答：**谁值得测、在哪套硬件上测、Context 证据到底到哪一层、真实 Agent Coding Loop 有没有证据。**
>
> 机器底座分成两部分：[`registry.json`](../../model-intelligence/registry.json) 保存 Model/Variant/Hardware/Context 证据；[`agentic-coding-evidence.json`](../../model-intelligence/agentic-coding-evidence.json) 单独保存真实 Agent Coding Loop 外部证据。

完整分析：

- [高质量大模型候选推荐与 GB10 / PRO6000 适配](high-quality-model-recommendations.md)
- [Agentic Coding Evidence：真实编码循环外部证据](agentic-coding-evidence.md)

---

## 当前 shortlist

| Priority | Model / Variant | 1×GX10 | 2×GB10 | 4×GB10 | Context / Agent Coding 关键信号 | 本仓 Qualification |
| --- | --- | --- | --- | --- | --- | --- |
| **P0** | **Qwen3.8-27B BF16 / FP8 / NVFP4** | **FIRST-PARTY @32K** | OPEN | OPEN | 本仓 Formal100；外部 Qwen3.8 NVFP4 agentic suite 有 86/86，但 Variant/harness 不完全同一 | Performance qualified；Quality / 128K+ / Production OPEN |
| **P0** | **Laguna-S-2.1 NVFP4** | **GOOD external** | 通常不需要先扩节点 | OPEN | 单 GB10 runtime 成熟；外部真实 Agent Coding 86/86；官方 agentic-coding / long-horizon 定位 | External candidate；本仓全部 OPEN |
| **P0** | **Qwen3.8-Flash-Next RadixArk NVFP4** | **GOOD external，PLE streaming** | **GOOD external，TP2** | OPEN | 262K serving；单双 GB10 都已有公开路线 | External candidate；本仓全部 OPEN |
| **P0** | **Qwen3.8-Flash-Next UD-Q3_K_XL GGUF** | **GOOD external** | 未作为首要 TP2 Variant | OPEN | 65K Coding Loop **连续两次 86/86**；必须和 RadixArk/official FP8 分开 | External candidate；本仓全部 OPEN |
| **P0** | **Qwen3.5-122B-A10B Hybrid INT4+FP8** | **GOOD external @256K** | 无需先扩节点 | OPEN | 单 GB10 成熟、256K、公开约 52–59 tok/s；Classic/Sweet-Spot | External candidate；本仓全部 OPEN |
| **P0** | **DeepSeek-V4-Flash-0731 official mixed checkpoint** | full-resident 不适配；压缩 Variant另算 | **GOOD external，TP2** | **GOOD external，TP4** | 2×公开接受接近 900K prompt；官方 Coding/Agent 信号强 | External candidate；本仓全部 OPEN |
| **P1 / Classic** | **openai/gpt-oss-120b MXFP4** | **GOOD external** | 不需要为了它扩节点 | OPEN | Agent/Tool-use 参考强；native 128K 限制 384K/512K 主 Repo 角色 | External reference；本仓 OPEN |
| **P1** | **GLM-5.3-Flash LibertAIDAI NVFP4** | full-resident 不适配 | **GOOD external，512K profile** | **GOOD external，large-KV** | 2×已有 440K needle byte-exact；对 384K/512K 很直接 | External candidate；本仓 OPEN |
| **P1** | **KAT-Coder-V2.5-Dev** | **GOOD external** | 不需先扩节点 | OPEN | 单 GB10 外部 Agent Coding 84/86；35B/3B-active Coding Specialist | External candidate；本仓 OPEN |
| **P1** | **nvidia/MiniMax-M3-NVFP4** | 不适配 | 250GB 对 2×过紧 | **GOOD external** | 4×已有 262K benchmark + 1M KV/serving；多模态/长上下文 | External candidate；本仓 OPEN |
| **P2 / NVIDIA Ref** | **Nemotron-3-Super-120B-A12B-NVFP4** | **GOOD external** | 不需先扩节点 | OPEN | NVIDIA-native Agent/Long-context；vendor up-to-1M 不能当 deep-prompt PASS | External reference；本仓 OPEN |
| **P2 / Classic Coder** | **Qwen3-Coder-30B-A3B-Instruct** | 容量轻松；外部高吞吐路线 | 不需扩节点 | OPEN | 30.5B/3.3B-active、native 256K、Agentic Coding / repo-scale 官方定位 | Candidate reference；本仓 OPEN |
| **P2** | **MiniMax-M3 community W4A16/GPTQ** | 不适配 | CONDITIONAL external | OPEN | 2×可行性路线存在，但 aggressive quant 必须独立 Quality Gate | External feasibility only |
| **WATCH** | **Kimi-K3 native MXFP4** | native 不适配 | native 不适配 | native 不适配 | 2.8T/104B-active、1M；只做 API / future large-cluster reference | WATCH |

`P0/P1/P2/WATCH` 是**第一方验证优先级**，不是质量总分、速度排行榜或采购顺序。

---

# 四条证据轴必须分开

## 1. Hardware Evidence

回答：**这个 exact Variant 在这个 topology 上能不能可靠 serve？**

```text
FIRST_PARTY_MEASURED
REPRODUCIBLE_EXTERNAL
STRONG_EXTERNAL
UNKNOWN
```

## 2. Context Evidence

必须拆：

```text
Configured / Model Length
!= KV Allocated
!= Actual Prompt Processed
!= Retrieval / Needle Validated
!= Coding Production Qualified
```

例如 DeepSeek V4 official 在 2×GB10 已有接近 900K actual-prompt 外部证据；GLM NVFP4 在 2×GB10 已有 440K needle。它们都仍然不是本仓 512K/1M Coding Production PASS。

## 3. Quality Evidence

回答：coding / reasoning / instruction / tool-use / long-context **模型能力信号**从哪里来。

Vendor benchmark、第三方 benchmark、社区经验都可以提高“值得测”的优先级，但本仓未跑 Quality Gate 时：

```text
quality_status = OPEN
```

## 4. Agentic Coding Evidence

回答：**模型是否真的在 Agent Loop 里搜索、修改、调用工具、跑测试并把任务做完。**

这次新加入的外部 ledger 记录：

- exact Model Variant；
- GB10 topology；
- runtime；
- Agent harness；
- task suite；
- hidden tests；
- run count；
- wall-clock；
- tool calls；
- repeat variance；
- caveats。

外部 Agent Coding PASS 只能提高 replication priority，不能跳过本仓 L3。

---

# 这轮审计最重要的新结论

## Laguna S 2.1 不应该被漏掉

它是约 118B / 8B-active MoE，官方明确面向 agentic coding / long-horizon work；单 GB10 NVFP4/DFlash serving 已经非常成熟，公开文档甚至保留了旧 vLLM tool-call gibberish、deep-prefill hard hang、统一内存 OOM 等失败边界。

更重要的是，同 GB10 外部真实 Agent Coding suite 给出 **86/86 hidden tests**。

因此：

```text
Laguna-S-2.1 NVFP4
= 1×GX10 P0 first-party replication candidate
```

但仍然：

```text
external 86/86
!= 本仓 Quality Qualified
!= 384K/512K PASS
!= Production Recommended
```

## Qwen3.8-Flash-Next 不能只保留一个 Variant

现在至少拆成：

```text
Official FP8
!= RadixArk NVFP4
!= Unsloth UD-Q3_K_XL GGUF
```

其中 UD-Q3_K_XL 在外部同 GB10 agentic suite 中 **两次连续 86/86**，这是目前发现的非常有价值的重复 Coding Loop 信号；但它只有 65K coding-run context，不能反推 256K/512K。

## “一次跑满分”也不能变成可靠性排名

同一 Qwen3.6-35B-A3B NVFP4 在重复运行里出现过明显波动。外部作者明确指出：**one run is not a measurement**。

因此本仓未来 Coding Production Suite 必须从：

```text
1 run
```

升级成：

```text
Formal Coding 5
→ repeated / multi-seed
→ mean / min / max / failure modes
```

并至少记录：hidden-test success、wall-clock、tool calls、retry、human intervention、compaction、regression、self-stop、run-to-run variance。

---

# 现有 1×GX10：现在最值得先复现什么

```text
P0  Qwen3.8-27B
    完成本仓 Quality + 128K→512K + Coding Loop

P0  Laguna-S-2.1 NVFP4
    成熟单 GB10 runtime + external 86/86 Agent Coding

P0  Qwen3.8-Flash-Next
    RadixArk NVFP4：大 Context / fast serving
    UD-Q3_K_XL：两次 86/86 coding-loop reference

P0  Qwen3.5-122B-A10B Hybrid
    256K mature Classic/Sweet Spot

P1  DeepSeek-V4 single-node compressed lane
    agentic 能力强，但 aggressive quant quality 必须严查

P1  KAT-Coder-V2.5-Dev
    84/86 Coding Specialist external signal

P1  gpt-oss-120b
    Agent/Tool-use Classic，native 128K

P2  Qwen3-Coder-30B-A3B / Nemotron 3 Super
    轻量 Classic Coder / NVIDIA Agent reference
```

**这说明第二台 GX10 很有价值，但仍然不能由“缺模型可跑”来触发购买。单节点的软件/模型空间还很大。**

---

# 2× / 4× GB10 的定位保持不变

2×第一批统一合同横比：

```text
P0  DeepSeek-V4-Flash-0731 official
P0  Qwen3.8-Flash-Next NVFP4
P1  GLM-5.3-Flash NVFP4
P2  MiniMax aggressive low-bit
```

4×只有在 2×第一方 L3 已证明出现不可由模型/runtime/context strategy 解决的容量、KV、并发或模型放置瓶颈时，才应该升级为 ACTION。主要价值是 MiniMax NVFP4、GLM/DeepSeek large-KV、1M、并发与多 Agent placement，而不是幻想单流 Decode 线性翻倍。

---

# 固定语义

```text
Popularity != Quality
Quality != Hardware Fit
Hardware Fit != Context Fit
Context Fit != Agentic Coding Fit
Agentic Coding Fit != Coding Production Qualification
```

Variant 仍然是基本推荐单位。某个 Variant 的速度、Context、质量或 Agent Loop 证据，不得自动转移给同家族其他 Variant。

统一资格链：

```text
CANDIDATE
→ Runtime Gate
→ Formal5
→ Formal100
→ Quality Gate
→ Context-band Gate
→ Agentic Coding Repeatability
→ L2 Agent Workload Fitness
→ Real Coding Production Loop
→ L3 Coding Production Fitness
→ Production Recommendation
```
