# Benchmark 指标统一解释

这份文档统一解释本仓库结果表里的性能、稳定性和衍生指标。以后 README、结果分表和跨平台对比都引用这里，避免同一个缩写在不同页面各自解释。

> 当前 GX10 / Qwen3.8-27B 这轮 Formal5 / Formal100 的 workload 是 **32,768 input + 256 output，Concurrency=1**。Formal100 主批次在 **1 次 warmup 之后**运行，因此它是有效的 warm-batch / `platform_optimized` 部分结果，不是 suite 冻结定义里的 cold-cache 完整 isolation 结果。除非明确写成 `E2E@32K`，否则本文中的 E2E 都是对应实际 workload 的端到端耗时。

## 先分清三类字段

| 类型 | 含义 | 示例 | 仓库规则 |
| --- | --- | --- | --- |
| **Measured / 实测** | runner、系统日志或 profiler 直接产生 | TTFT、TPOT、E2E、Std、P99、Output throughput | 保留原始证据与测量方法 |
| **Derived / 衍生** | 只由同合同实测值按公开公式计算 | Decode=`1000/TPOT`、Effective Prefill=`input/TTFT`、CV、Speedup、Drift | 必须标记 Derived/`*`，不得冒充独立实测 |
| **Unmeasured / 未测** | 现有证据不能严格得到 | 当前 Pure Prefill、32K-output E2E、24h soak | 写 `未测 / 不可计算`，禁止补洞 |

## 一眼先看懂

| 指标 | 中文直译 | 单位 | 趋势 | 最适合回答的问题 | 类型 |
| --- | --- | --- | --- | --- | --- |
| Pure Prefill / PP | 纯输入上下文处理速度 | tok/s | 越高越好 | “模型纯粹读 prompt 有多快？” | 当前未测 |
| Effective Prefill / PP* | 实际首 token 链路的有效输入速度 | tok/s | 越高越好 | “实际读完这段输入并开始回复有多快？” | Derived |
| TTFT | 首 Token 延迟 | ms / s | 越低越好 | “发请求后多久开始看到回复？” | Measured |
| TPOT | 每个输出 Token 的平均耗时 | ms/token | 越低越好 | “开始回复后，每个 token 要多久？” | Measured |
| Decode / TG | 持续生成速度 | tok/s | 越高越好 | “开始输出后的正文生成有多快？” | Derived from TPOT |
| E2E | 端到端总耗时 | ms / s | 越低越好 | “整个请求从发送到完成多久？” | Measured |
| ITL | 相邻输出 token 延迟 | ms | 越低越好 | “token-to-token 抖动大不大？” | Measured |
| Std | 标准差 | 与原指标同单位 | 越低越稳定 | “同一批请求波动大不大？” | Measured/statistical |
| CV | 变异系数 | % | 越低越稳定 | “不同均值下相对波动谁更小？” | Derived |
| P99 | 99 分位延迟 | 与原指标同单位 | 越低越好 | “最慢约 1% 请求会慢到什么程度？” | Measured/statistical |
| Completion | 成功完成率 | x/y 或 % | 越高越好 | “有没有失败或少生成？” | Measured |
| Peak output throughput | runner 的峰值输出 token 吞吐 | tok/s | 越高越好 | “按 runner 的时间桶统计，峰值输出吞吐到过多少？” | Measured/statistical |

## Prefill / PP（最容易混淆）

### Pure Prefill / `pp_tps`

严格 Prefill 只计算 prompt/input context 的模型 prefill 阶段，通常写 `pp_tps`，单位 `tok/s`。它不应包含 HTTP/API、scheduler、首 token decode、返回客户端等额外开销。

当前 GX10 Formal5/Formal100 使用 `vllm bench serve`，原始结果没有独立给出 pure-prefill duration，因此：

```text
Pure Prefill / pp_tps = 未单独测量
```

不能用别的指标把这个空缺“算满”。

### Effective Prefill / Effective PP / `Prefill*`

为了保留实际长输入体验，本仓库计算：

```text
Effective Prefill (tok/s)
= input_tokens / TTFT_seconds
= 32768 / (TTFT_ms / 1000)
```

它包含 TTFT 链路中的额外开销，因此必须写 **Effective / Derived / `Prefill*`**，不能改名成 Pure Prefill。

当前 Formal100：

| Precision | Effective Prefill / PP* (tok/s) | Pure Prefill `pp_tps` |
| --- | ---: | --- |
| BF16 | 936.453 | 未单独测量 |
| FP8 | 1187.130 | 未单独测量 |
| NVFP4 | 1300.614 | 未单独测量 |

以后若完成独立 pure-prefill benchmark，两列同时保留，不覆盖历史。

## TTFT — Time To First Token

`TTFT` 是从客户端发出请求，到收到第一个输出 token 的 wall-clock 时间。大致包含：API/请求 → scheduler → prompt prefill → 首 token decode → 返回客户端。

因此：

```text
TTFT ≠ pure prefill time
```

对编码 Agent 和大上下文问答，TTFT 直接决定“发出指令后多久开始工作”。

## TPOT — Time Per Output Token

`TPOT` 表示首 token 之后，每生成一个输出 token 平均耗时多少毫秒，单位 `ms/token`，越低越好。

## Decode / TG — Token Generation

本仓库当前表中的 Decode 由 TPOT 派生：

```text
Decode (tok/s) = 1000 / TPOT (ms/token)
```

例如 TPOT=110 ms/token，Decode≈9.09 tok/s。Decode 是“开始输出后的打字速度”，不包含前面的长输入等待。

## E2E — End To End

`E2E` 是从请求发出，到最后一个要求的输出 token 完整收到为止的总 wall-clock。

当前 Formal5/Formal100 是：

```text
32,768 input + 256 output
```

所以当前值应理解为 **E2E@32K+256 workload**，绝不能写成仓库正式的 `E2E@32K`。

正式 `E2E@32K` 固定要求：

```text
32,768 input + 32,768 output
Concurrency = 1
Cold Cache
完整生成 32,768 output tokens
```

## ITL — Inter Token Latency

`ITL` 是相邻输出 token 之间的时间间隔。它与 TPOT 高度相关，但统计对象不同：TPOT 是请求级平均输出 token 时间；ITL 能观察 token-to-token 抖动和尾部。

## Std — Standard Deviation

`Std` 是标准差，表示同一批请求围绕均值的离散程度。它带原指标单位，因此跨不同均值直接比较不总是直观。

## CV — Coefficient of Variation

`CV` 把标准差归一化：

```text
CV = Std / Mean × 100%
```

CV 越小，通常表示批次内相对波动越小。但 CV 不能替代 24h soak、重启恢复、OOM/crash 等系统级稳定性测试。

## P50 / P90 / P95 / P99

这些是分位数：P50 约等于中位数；P90/P95 表示 90%/95% 请求不超过该值；P99 主要观察最慢约 1% 请求的尾延迟。

常用衍生量：

```text
P99 tail amplification = (P99 / Mean - 1) × 100%
```

## Completion / Failed

当前 Formal100 的三档都是：

```text
100 / 100 completed
0 failed
```

这只证明当前 **32K+256、Concurrency=1、warm main batch** 的请求级完成率，不代表 32K 长输出、128K+ context 或 24h 同样稳定。

## Request / Output / Total Token Throughput

这些是整场 benchmark wall-clock 的聚合统计：

- `Request throughput (req/s)`：整批每秒完成多少请求；
- `Output throughput (tok/s)`：整批输出 token / 整场耗时；
- `Total token throughput (tok/s)`：整批 input+output token / 整场耗时。

它们回答“整条流水线平均吞吐”，不是单请求 Decode，也不是 Pure Prefill。

## Peak output token throughput / `max_output_tokens_per_s`

**重要修正：** vLLM 0.28.0 结果里的 `max_output_tokens_per_s` 是 runner **测出来的 Peak output token throughput**，不是配置项、限速器或 `max output cap`。

当前 Formal100 原始日志报告：

| Precision | Peak output throughput (tok/s) | runner `Peak concurrent requests` |
| --- | ---: | ---: |
| BF16 | 5.00 | 2 |
| FP8 | 7.00 | 2 |
| NVFP4 | 10.00 | 2 |

其中 runner 的 `Peak concurrent requests` 是其峰值时间桶统计字段；它**不能覆盖** benchmark 明确配置的 `Maximum request concurrency=1`。因此仓库始终把配置并发与 runner 峰值统计分开记录。

## Cache State / Warmup / Comparison Mode

比较性能时，必须先看缓存与 warmup 语义：

- `cold`：冻结 suite 要求的 cold-cache isolation；
- `warm`：主批次之前已有 warmup 或明确热状态；
- `prefix_cache`：命中前缀缓存；
- `mixed`：状态混合，必须进一步说明。

当前 GX10 Formal100 的原始命令都包含 `num_warmups=1`，所以 canonical result 写 `cache_state=warm`，并标成 `comparison_mode=platform_optimized`。这批数据仍然有效，但**不能冒充 frozen suite 的 cold-cache strict-comparable 完整结果**。

## Formal5 / Formal100

- `Formal5`：5 请求阶段 gate，用于快速确认配置、速度和初步稳定性；
- `Formal100`：100 请求正式批次，用作当前这轮 performance/warm-batch 基线。

Formal5 的价值是判断是否值得进入长批次，以及观察阶段状态漂移，不是取代 Formal100。

## Drift — Formal5 → Formal100

同一指标：

```text
Drift = (Formal100 / Formal5 - 1) × 100%
```

延迟类（TTFT/TPOT/E2E）负数通常表示 Formal100 更快；速度类（Decode/Effective Prefill）正数通常表示 Formal100 更快。只有 workload/runtime 条件足够一致时，Drift 才适合做因果式解释；否则只能作为状态变化证据。

## Speedup / Gain / Reduction

```text
Speedup = Baseline latency / New latency       # 延迟类等价速度倍率
Gain% = (New speed / Baseline speed - 1) × 100%
Latency reduction% = (1 - New latency / Baseline latency) × 100%
```

这些都是由同合同实测值产生的 Derived Data，不是新的 benchmark。

## 使用规则

所有结果页遵守四条：

1. **值必须带语义。** 同时标明 workload、cache/warmup、comparison mode 和 Evidence Level；
2. **Measured / Derived / Unmeasured 分开。** 衍生值必须可追溯到公式和原始值；
3. **失败不能用 0 冒充性能值。** 没有有效样本时 canonical result 使用 `null` 并保留失败证据；
4. **没有真实测量就写 `未测 / 不可计算`。** 不使用配置上限、别的 workload、别的机器或数学外推补洞。
