# Agentic Coding Evidence — 单 GB10 真实编码循环外部证据

> 这页回答：**模型能不能在真实 Agent Loop 里搜索、修改、调用工具、运行测试并把任务做完？**
>
> 这里全部是外部同 GB10 证据，不是本仓 First-party Production Qualification。机器记录见 [`agentic-coding-evidence.json`](../../model-intelligence/agentic-coding-evidence.json)。

## 为什么要独立成一条证据轴

```text
Vendor Coding Benchmark
!= GB10 Runtime PASS
!= Context PASS
!= Real Agent Coding Loop PASS
!= 本仓 Coding Production Qualified
```

因此 L2/L3 不能只看 tok/s 和通用 benchmark，还必须单独观察 Agentic Coding。

---

# 外部同 GB10 真实 Coding Loop

主要来源：`DG1001/local-agentic-coding-128gb`。硬件是 ASUS Ascent GX10 / NVIDIA GB10 / 128GB unified memory；主套件包含 4 个 Python coding tasks、86 个 hidden tests，并通过本地 Agent harness 操作真实文件和测试。

| Model / Variant | Harness | Hidden tests | Run / Repeat | Wall-clock | 正确解释 |
| --- | --- | ---: | --- | ---: | --- |
| **DeepSeek-V4-Flash 压缩单机 Variant** | opencode | **86/86** | 1 run | 25:49 | 单 GB10 能闭合 agent loop；不是 2× official checkpoint |
| **Laguna-S-2.1 NVFP4** | opencode | **86/86** | 1 run | 30:56 | P0 复现候选；单 run 不能变成可靠性概率 |
| **Qwen3.8-Flash-Next UD-Q3_K_XL** | opencode | **86/86** | **2 runs，均 86/86** | 33:33 / 38:24 | 当前最强的单 GB10 重复 Coding Loop 外部信号之一 |
| Qwen3.8-27B NVFP4+MTP external | jaja | **86/86** | 1 run | 54:03 | 补充本仓 Qwen3.8 性能链，但 harness / Variant 不完全相同 |
| Qwen3.6-27B dense | opencode | **86/86** | 1 run | 3:07:36 | 能做对但等待成本极高：Capability != Production Fitness |
| **KAT-Coder-V2.5-Dev** | opencode | 84/86 | 1 run | 25:59 | Coding Specialist 高价值候选 |
| Qwen3.6-35B-A3B NVFP4 | opencode | **86/86** | 1 run | 21:01 | 极快的完美 run，但不能单独代表稳定性 |
| Qwen3.6-35B-A3B NVFP4 | Java/jaja | 64 / 67 | **2 back-to-back runs** | 分开记录 | 同 server/config family 在另一 harness 下明显波动；一个 run 还暴露 harness STOP gap |
| GLM-5.3-Flash UD-IQ1_S | opencode | 9/86 | 1 run | 35:28 | 9 分来自 untouched seed；只证明这个 exact config 失败，不是 GLM family verdict |

**关键修正：** `86 / 64 / 67` 不能伪装成“同一个 opencode 条件的三次重复”。机器 ledger 已拆成两个 evidence records：一个 opencode 86/86，另一个 Java/jaja 64/67 repeated pair。

来源：

- https://github.com/DG1001/local-agentic-coding-128gb
- https://github.com/DG1001/local-agentic-coding-128gb/blob/main/docs/variance.md

---

# 1. Laguna S 2.1 是本轮真正的高价值遗漏

Poolside Laguna S 2.1 是约 118B total / 8B active 的 MoE，官方明确面向 **agentic coding / long-horizon work**，并提供 NVFP4 / INT4 等本地路线。

单 GB10 的外部 serving 证据已经非常成熟：

- `poolside/Laguna-S-2.1-NVFP4`；
- vLLM 0.25/0.26；
- 128K sweet-spot；non-spec / safer profile 可推到约 250K/256K；
- DFlash 对 code decode 有明显收益；
- 同时公开保留旧 vLLM tool-call gibberish、deep-prefill hard hang、统一内存 OOM 等失败边界。

再叠加真实 coding suite 的 86/86，因此它应该进入：

```text
1×GX10 P0 first-party replication pool
```

但不能推出：

```text
external 86/86
→ 本仓 Quality Qualified        ❌
→ 384K/512K Coding PASS         ❌
→ 24h autonomous PASS           ❌
→ Production Recommended        ❌
```

来源：

- https://huggingface.co/poolside/Laguna-S-2.1
- https://huggingface.co/poolside/Laguna-S-2.1-NVFP4
- https://github.com/Reederey87/laguna-s-2.1-dgx-spark
- https://github.com/sudoingX/dgx-spark-laguna

---

# 2. Qwen3.8-Flash-Next 必须至少拆三种 Variant

```text
Official FP8
!= RadixArk NVFP4
!= Unsloth UD-Q3_K_XL GGUF
```

UD-Q3_K_XL 在 `llama-server -c 65536` 下连续两次 86/86，是很有价值的 repeat signal；但它只覆盖约 65K coding-run context。

所以：

```text
65K repeated Coding PASS
!= 256K/384K/512K Coding PASS
```

RadixArk NVFP4 则更值得测大 Context / PLE streaming / 2×TP2。两条路线解决的是不同问题，不能合并成“Qwen Flash Next 一个分数”。

---

# 3. DeepSeek 单节点路线应该被重新评价

外部 88GB 左右压缩 setup 在单 GX10 上得到 86/86、25:49。这说明单机 DeepSeek 不只是“能启动的实验”，值得真正比较：

- aggressive quant 对 harder reasoning 的损失；
- 实际 bugfix/edit loop 是否比传统 Quality benchmark 更耐量化；
- Useful Engineering Work / Hour 是否胜过 Laguna/Qwen。

但它与 2×GB10 的 official mixed checkpoint 是**不同 Variant**，不得串证据。

---

# 4. 一次满分不是可靠性

外部 variance 研究显示，同一模型 / server family 的结果可以因 sample 和 harness 行为显著变化。

尤其要区分：

```text
Model variance
Harness failure
Turn-budget censoring
Context compaction failure
Tool-parser / protocol failure
```

例如外部 Qwen3.6 repeated pair 中，一个任务出现 4-token STOP、0 tool call，harness 却把它当完成。这是 Harness Gate，不应该简单算成模型质量下降。

因此本仓未来 Coding Production Suite 应逐步采用：

```text
Formal Coding 5
→ repeated / multi-seed
→ mean / min / max
→ named failure modes
```

至少记录：

- hidden-test pass；
- completed task；
- wall-clock；
- tool calls；
- retry count；
- human intervention；
- context compaction；
- regression；
- self-stop；
- run-to-run variance。

---

# 5. Coding Tool / Harness 本身就是 L3 变量

外部实验直接证明：同一个模型换 harness，结果可能不仅速度不同，**任务是否成功也会改变**。

因此第三层正确对象仍是：

```text
Coding Tool
× Model Variant
× Runtime
× Context Strategy
× Agent Harness Policy
× Workspace / Build / Test Host
× Hardware
```

不能降维成：

```text
Model X Coding Fitness = 90
```

---

# 对当前 1×GX10 第一方复现顺序的影响

```text
P0  Qwen3.8-27B
    已有本仓性能链；补 Quality / 128K→512K / repeated Coding Loop

P0  Laguna-S-2.1 NVFP4
    mature GB10 runtime + external 86/86 agentic loop

P0  Qwen3.8-Flash-Next
    RadixArk NVFP4：大 Context / fast serving
    UD-Q3_K_XL：两次 86/86 coding repeat reference

P0  Qwen3.5-122B-A10B Hybrid
    mature 256K Classic/Sweet Spot

P1  DeepSeek V4 compressed single-node
    external 86/86；aggressive quant quality 必须严查

P1  KAT-Coder-V2.5-Dev
    external 84/86；Coding Specialist

P1  gpt-oss-120b
    Agent / Tool-use Classic；native 128K

P2  Qwen3-Coder-30B-A3B / Nemotron 3 Super
    Classic Coder / NVIDIA Agent reference
```

这个排序是**第一方验证价值**，不是全球模型排名。

---

# 证据权限边界

External Agentic Coding Evidence 可以：

```text
提高 Candidate Test Priority
暴露 Harness / Runtime failure mode
选择更值得复现的 exact Variant
指导本仓 L3 Task Suite 设计
```

不能：

```text
external hidden tests PASS
→ quality_status = QUALIFIED      ❌

external Agent Loop PASS
→ PRODUCTION_QUALIFIED            ❌

65K Coding PASS
→ 512K Coding PASS                ❌

一个 Harness PASS
→ 所有 Coding Tool 都适配         ❌
```

真正 Production Recommendation 仍必须回到本仓：

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
