# Agentic Coding Evidence — 单 GB10 真实编码循环外部证据

> 这页回答一个与普通 Quality Benchmark 不同的问题：**模型能不能在真实 Agent Loop 里搜索、修改、调用工具、运行测试并把任务做完？**
>
> 这里全部是 **外部同 GB10 可复现证据**，不是本仓第一方 Production Qualification。它的作用是筛选最值得我们自己复现的模型/Variant，而不是直接宣布“生产推荐”。

## 为什么必须独立一层

下面五件事不能再混：

```text
模型厂商 Coding benchmark 很高
!=
GB10 上能稳定 serve
!=
能处理目标 Context
!=
真实 Agent Tool Loop 能完成任务
!=
本仓大型项目 Production Qualified
```

因此 Model Intelligence 现在除了 Hardware / Context / Quality，还需要单独观察 **Agentic Coding Evidence**。

---

## 当前最重要的一组同硬件证据

来源主线：`DG1001/local-agentic-coding-128gb`，硬件是 **ASUS Ascent GX10 / NVIDIA GB10 / 128GB unified memory**，与 DGX Spark 属于同 GB10 类硬件。其主套件是 4 个真实编码任务、每模型 86 个 hidden tests，并通过 opencode / Claude Code / Oh My Pi / 后续专用 Java harness 驱动本地 endpoint。

| Model / Variant | Harness | Hidden tests | Wall clock | 关键判断 |
| --- | --- | ---: | ---: | --- |
| **DeepSeek-V4-Flash，DG1001 单机压缩 Variant** | opencode | **86/86** | **25:49** | 单 GB10 上已经证明“能闭合真实编码 loop”；但它不是 2×GB10 official mixed checkpoint |
| **Laguna-S-2.1 NVFP4** | opencode | **86/86** | 30:56 | **本轮最大遗漏之一**：模型本身就是 agentic coding / long-horizon 取向，且单 GB10 serving 路线成熟 |
| **Qwen3.6-27B dense** | opencode | **86/86** | 3:07:36 | 质量可过，但 dense decode 导致人类等待成本过高；“能做对”不等于生产甜点 |
| **KAT-Coder-V2.5-Dev** | opencode | 84/86 | 25:59 | 很强的 Coding Specialist 候选，但仍是一轮数据 |
| **Qwen3.8-27B NVFP4+MTP external setup** | jaja | **86/86** | 54:03 | 对我们已有 Qwen3.8 第一方性能链很有价值，但 harness 不同，不能横比 wall-clock |
| **Qwen3.8-Flash-Next UD-Q3_K_XL** | opencode | **86/86，连续两次** | 33:33 / 38:24 | **目前找到的单 GB10 最强重复 Agent Coding 信号之一**；必须和 RadixArk NVFP4 分 Variant |
| **Qwen3.6-35B-A3B NVFP4** | opencode | 64→67→**86/86** | 最快完美 run 21:01 | 极快，但重复波动很大；非常适合做“稳定性反例” |
| **GLM-5.3-Flash UD-IQ1_S** | opencode | 9/86 | 35:28 | **不是 GLM 家族差**；这 9 分是 seed 自带，证明的是这条 IQ1_S 配置失败 |

机器记录：[`model-intelligence/agentic-coding-evidence.json`](../../model-intelligence/agentic-coding-evidence.json)。

---

# 这组数据真正告诉我们什么

## 1. Laguna S 2.1 应进入 1×GX10 P0 复现池

Poolside 官方 Laguna S 2.1 是约 118B total / 8B active 的 MoE，明确为 **agentic coding / long-horizon work** 设计，并提供 1M model-context 能力与 NVFP4 / INT4 等量化路线。

单 GB10 的公开 serving 证据已经很成熟：

- `poolside/Laguna-S-2.1-NVFP4`；
- 约 74GB NVFP4 + draft；
- vLLM 0.25/0.26；
- 128K sweet-spot，250K/256K non-spec / safer profiles；
- DFlash code decode 可到约 40 tok/s 级，但具体数字强依赖 profile；
- 公开文档明确记录旧 vLLM tool-call gibberish、deep-prefill hard hang、统一内存 OOM 等真实失败边界。

更关键的是，独立 agentic-coding suite 中 Laguna 得到 **86/86 hidden tests**。

所以它不是“因为厂商 benchmark 漂亮”进入 shortlist，而是：

```text
官方 Agentic Coding 定位
+
单 GB10 成熟 Runtime
+
真实 Agent Loop hidden-test PASS
=
1×GX10 高价值 P0 first-party replication candidate
```

仍然不能推出：384K/512K Coding PASS、24h autonomous PASS、Production Qualification。

公开来源：

- https://huggingface.co/poolside/Laguna-S-2.1
- https://huggingface.co/poolside/Laguna-S-2.1-NVFP4
- https://github.com/Reederey87/laguna-s-2.1-dgx-spark
- https://github.com/sudoingX/dgx-spark-laguna
- https://github.com/DG1001/local-agentic-coding-128gb

---

## 2. Qwen3.8-Flash-Next 还要再拆一个 Variant

我们前面已经拆开：

```text
Official FP8
!=
RadixArk NVFP4
```

现在还要加：

```text
Unsloth UD-Q3_K_XL GGUF
```

因为 DG1001 的真实 Agent Coding 结果用的是 `llama-server -c 65536` 的 Q3_K_XL 路线，**连续两次 86/86**。这是比单次 benchmark 更有价值的重复信号。

但是它只证明：

- 65K context 下；
- 这套 llama.cpp / GGUF Variant；
- 这 4 个 Python tasks；
- 这套 opencode harness；

能稳定解决这一类任务。

不能把它的结果转给 RadixArk NVFP4，也不能因为它两次 86/86 就写“512K Main Coding Agent 已经 qualified”。

---

## 3. DeepSeek V4 的单机路线应该从“实验奇技淫巧”升一级

我们之前把单 GB10 DeepSeek 主要看成 2-bit / streaming 的 P1 实验路线。

但真实 agentic coding evidence 表明：一套约 88GB 的压缩 DeepSeek V4 local setup 在同一 GX10 上可以 86/86，25:49 完成四个任务。

这说明单机 DeepSeek 至少值得进入 **P0/P1 边界复现**，尤其可以回答：

- aggressive compression 对 harder reasoning 到底损失多少；
- 实际 bugfix / edit loop 能否比通用 quality benchmark 更耐量化；
- 与 Laguna / Qwen Flash Next 的 Useful Engineering Work per Hour 谁更高。

但必须保持 Variant 边界：它不是 2×GB10 的 official mixed checkpoint。

---

## 4. “一次 86/86”不能当可靠性结论

这组外部数据里最有价值的并不是冠军，而是**方差**。

同一个 Qwen3.6-35B-A3B NVFP4 在多轮中出现过约 64、67、86；Nemotron 甚至多轮跨度达到几十个 hidden-test points。来源作者明确指出：**one run is not a measurement**。

因此本仓未来的 Coding Production Suite 不能只做：

```text
每模型 × 1次
```

至少应逐步形成：

```text
Formal Coding 5
→ Formal Coding N
→ multi-seed / repeated run
→ mean / min / max / failure modes
```

尤其要记录：

- hidden-test success；
- task success；
- wall-clock；
- tool calls；
- human intervention；
- retry count；
- context compaction；
- regression；
- self-stop；
- run-to-run variance。

---

## 5. Harness 本身就是 Production Configuration 的一部分

同一个模型换 opencode / Oh My Pi / Claude Code，结果可能改变，不只是速度改变。

外部报告中一个非常重要的失败模式是：Claude Code 自身 baseline context footprint 在某些 65K 模型配置上会触发 compaction thrashing，导致任务直接失败。这说明第三层必须评价：

```text
Coding Tool
× Model
× Context
× Harness Policy
× Runtime
× Hardware
```

而不能只写：

```text
Model X Coding Fitness = 90分
```

这正好支持我们 L3 的 `Coding Production Configuration` 定义。

---

# 对当前模型 shortlist 的影响

## 1×GX10 第一方复现顺序应调整为

```text
P0  Qwen3.8-27B
    → 已有本仓性能链，补 Quality / 128K→512K / Coding Loop

P0  Laguna-S-2.1 NVFP4
    → 成熟单机 runtime + external 86/86 agentic loop

P0  Qwen3.8-Flash-Next
    → RadixArk NVFP4：大 Context / fast serving
    → UD-Q3_K_XL：两次 86/86 coding-loop reference

P0  Qwen3.5-122B-A10B Hybrid
    → 256K mature Classic/Sweet Spot

P1  DeepSeek V4 single-node compressed lane
    → external 86/86，但必须严查 aggressive quant quality

P1  gpt-oss-120b
    → Agent / Tool-use Classic；native 128K 限制主 Repo 角色

P1  KAT-Coder-V2.5-Dev
    → 84/86，Coding Specialist watch/replication

P2  Nemotron 3 Super / other NVIDIA references
    → 作为生态、Agent、Long-context 对照
```

这个顺序是“第一方验证价值”，不是全球模型排名。

---

# 还应该保留一个 Classic Coding Specialist

`Qwen3-Coder-30B-A3B-Instruct` 仍值得作为轻量 Classic Coding reference：

- 30.5B total / 3.3B active；
- native 262,144 context，可用 YaRN 扩到 1M；
- Apache-2.0；
- 官方明确面向 agentic coding / repo-scale understanding；
- 单 GB10 社区研究显示它可以达到很高交互 decode，并且比 dense coder 更适合作为交互 coding worker。

它不需要挤进当前 P0，因为 Laguna / Qwen Flash Next / DeepSeek 的“真实 Agent Loop + 大模型能力”证据更值得优先；但作为 Coding Specialist 的长期 reference 不应该消失。

公开来源：

- https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct
- https://github.com/heitor-mocelin/dgx-spark-research

---

# 最终边界

外部 Agentic Coding Evidence 可以做：

```text
提高 candidate test priority
暴露 harness/runtime failure mode
选择更值得花第一方测试时间的 Variant
设计本仓 Coding Production Suite
```

它不能做：

```text
external 86/86
→ quality_status = QUALIFIED       ❌

external agent loop PASS
→ Production Qualified             ❌

65K coding PASS
→ 512K coding PASS                 ❌

一个 harness PASS
→ 所有 coding tools 都适配         ❌
```

真正 Production Recommendation 仍必须回到本仓自己的：

```text
Runtime
→ Performance
→ Context
→ Quality
→ Agentic Coding Repeatability
→ Long Session / Recovery
→ L2 Agent Fitness
→ L3 Coding Production Fitness
```
