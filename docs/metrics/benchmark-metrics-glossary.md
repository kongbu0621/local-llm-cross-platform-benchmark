# Benchmark 指标统一解释

这份文档统一解释本仓库结果表里的性能、稳定性和衍生指标。以后 README、结果分表和跨平台对比都引用这里，避免同一个缩写在不同页面各自解释。

> 当前 GX10 / Qwen3.8-27B 这轮数据的 workload 是 **32,768 input + 256 output，Concurrency=1**。除非明确写成 `E2E@32K`，否则本文中的 E2E 都是对应实际 workload 的端到端耗时。

## 一眼先看懂

| 指标 | 中文直译 | 单位 | 趋势 | 最适合回答的问题 |
| --- | --- | --- | --- | --- |
| Prefill / PP | 输入上下文处理速度 | tok/s | 越高越好 | “模型读 32K/256K/1M 上下文有多快？” |
| TTFT | 首 Token 延迟 | ms / s | 越低越好 | “我发出请求后多久开始看到回复？” |
| TPOT | 每个输出 Token 的平均耗时 | ms/token | 越低越好 | “开始回复以后，每个 token 要等多久？” |
| Decode / TG | 持续生成速度 | tok/s | 越高越好 | “开始输出以后正文生成有多快？” |
| E2E | 端到端总耗时 | ms / s | 越低越好 | “整个任务从发送到完成一共多久？” |
| Std | 标准差 | 与原指标同单位 | 越低越稳定 | “同一批请求波动大不大？” |
| CV | 变异系数 | % | 越低越稳定 | “不同量纲/不同均值下相对波动谁更小？” |
| P99 | 99 分位延迟 | 与原指标同单位 | 越低越好 | “最慢的约 1% 请求会慢到什么程度？” |
| Completion | 成功完成率 | x/y 或 % | 越高越好 | “这批请求有没有失败/少生成？” |

## Prefill / PP（最容易混淆）

### Pure Prefill / `pp_tps`

严格意义上的 Prefill，是模型只处理 prompt/input context 的吞吐，通常写成 `pp_tps`，单位 `tok/s`。

它回答的是：**模型读输入上下文到底多快。**

严格 Pure Prefill 应只计算 prompt prefill 阶段本身，不包含 HTTP/API、调度、首 token decode、返回链路等额外开销。

### Effective Prefill / Effective PP

当前 GX10 Formal5/Formal100 的 `vllm bench serve` 原始结果没有单独给出 pure prefill duration，因此本轮不能声称有严格 `pp_tps`。

为了保留一个可用的“实际输入处理体验”指标，本仓库使用：

```text
Effective Prefill (tok/s)
= input_tokens / TTFT_seconds
= 32768 / (TTFT_ms / 1000)
```

它包含 TTFT 链路中的 API/调度/首 token 等额外开销，因此必须标记为 **Effective / Derived**，不能冒充 Pure Prefill。

当前 Formal100：

| Precision | Effective Prefill / PP* (tok/s) | Pure Prefill `pp_tps` |
| --- | ---: | --- |
| BF16 | 936.453 | 未单独测量 |
| FP8 | 1187.130 | 未单独测量 |
| NVFP4 | 1300.614 | 未单独测量 |

以后如果跑独立 pure-prefill benchmark，两列会同时保留：`Prefill (pure)` 与 `Prefill (effective)`，不覆盖历史。

## TTFT — Time To First Token

`TTFT` 是从请求发出，到客户端收到第一个输出 token 的 wall-clock 时间。

大致包含：请求/API 开销 → scheduler → prompt prefill → 首 token decode → 返回客户端。

因此：

```text
TTFT ≠ pure prefill time
```

对于编码 Agent、大上下文问答，TTFT 很重要，因为它决定“发出指令以后多久开始看到模型工作”。

## TPOT — Time Per Output Token

`TPOT` 表示首 token 之后，每生成一个输出 token 平均需要多少毫秒。

单位：`ms/token`，越低越好。

它和 Decode 的关系是：

```text
Decode (tok/s) = 1000 / TPOT (ms/token)
```

例如 TPOT = 110 ms/token，则 Decode 约为 9.09 tok/s。

## Decode / TG — Token Generation

`Decode`（也常写 TG）表示首 token 之后的持续生成速度，单位 `tok/s`，越高越好。

这是用户最容易直观感觉到的“模型打字速度”，但它**不包含前面的长上下文读取等待**。因此只看 Decode 会低估长上下文任务里 TTFT/Prefill 的重要性。

## E2E — End To End

`E2E` 表示从请求发出，到最后一个要求的输出 token 完整收到为止的总 wall-clock 时间。

当前 Formal5/Formal100 是：

```text
32,768 input + 256 output
```

所以当前 E2E 是 **E2E@32K+256** 的实际耗时，不是仓库固定合同 `E2E@32K`。

仓库里的正式 `E2E@32K` 专指：

```text
32,768 input + 32,768 output
Concurrency = 1
Cold Cache
```

没有生成满 32,768 output，不得填写正式 `E2E@32K`。

## ITL — Inter Token Latency

`ITL` 是相邻输出 token 之间的时间间隔。

它与 TPOT 高度相关，但不是完全同一个统计对象：TPOT 是请求级平均输出 token 时间，ITL 可以进一步观察 token-to-token 的抖动和尾部。

## Std — Standard Deviation

`Std` 是标准差，用来看同一批请求结果离均值有多分散。

例如 TTFT mean = 27,603 ms、std = 230 ms，说明大部分请求的首 token 延迟集中在均值附近。

标准差有单位，所以不同量纲或不同均值之间直接比较不总是直观。

## CV — Coefficient of Variation

`CV` 是变异系数：

```text
CV = Std / Mean × 100%
```

它把波动归一化成百分比，更适合横向比较不同精度或不同指标的相对稳定程度。

例如：

```text
CV = 0.8%
```

表示标准差约为均值的 0.8%。

CV 越小通常说明批次内越稳定，但它**不能替代 24h soak、重启恢复、OOM/crash 等系统级稳定性测试**。

## P50 / P90 / P95 / P99

这些是延迟分位数。

- `P50`：一半请求不超过这个值，近似中位数；
- `P90`：90% 请求不超过这个值；
- `P95`：95% 请求不超过这个值；
- `P99`：99% 请求不超过这个值，主要看尾延迟。

P99 比 mean 高多少，可以作为 tail amplification：

```text
P99 tail = (P99 / Mean - 1) × 100%
```

## Completion / Failed

`Completion` 记录按合同完整完成的请求数。

当前 Formal100 的 BF16 / FP8 / NVFP4 都是：

```text
100 / 100 completed
0 failed
```

这证明的是当前 workload 的请求级完成率，不代表更长上下文、更长输出或 24h 都同样稳定。

## Request / Output / Total Token Throughput

这些是 runner 对**整场 benchmark wall-clock** 的聚合统计，和单请求 Decode 不同。

- `Request throughput (req/s)`：整批每秒完成多少请求；
- `Output throughput (tok/s)`：整批输出 token / 整场耗时；
- `Total token throughput (tok/s)`：整批 input+output token / 整场耗时。

在 Concurrency=1 下，它们更接近“整条流水线端到端吞吐”；不能直接叫 Decode，也不能叫 Pure Prefill。

## Formal5 / Formal100

- `Formal5`：5 请求阶段 gate，用来快速确认配置、速度和初步稳定性；
- `Formal100`：100 请求正式批次，本轮正式性能/批次稳定性基线。

Formal5 的主要价值不是取代 Formal100，而是判断是否值得继续跑长批次，以及比较阶段状态是否漂移。

## Drift — Formal5 → Formal100 漂移

对同一指标：

```text
Drift = (Formal100 / Formal5 - 1) × 100%
```

延迟类指标（TTFT/TPOT/E2E）负数通常代表 Formal100 更快；吞吐/速度类指标（Decode/Prefill）正数通常代表 Formal100 更快。

只有在合同一致时 Drift 才适合直接解释；参数不同的 run 只能作为过程证据。

## Speedup / Reduction

为了让结果更容易用于决策，本仓库还会给出相对 BF16 或相对另一精度的衍生结论：

```text
Speedup = New speed / Baseline speed
Gain%   = (New / Baseline - 1) × 100%
Latency reduction% = (1 - New latency / Baseline latency) × 100%
```

这些都是从同合同实测值计算出的衍生数据，不是新的 benchmark。

## 使用规则

结果表必须同时保留“值 + 定义 + 测量/派生方式 + 解释边界”。如果某项没有真实测量：

```text
未测 / 不可计算
```

而不是用配置上限、别的 workload 或近似值补洞。