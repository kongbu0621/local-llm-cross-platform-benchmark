# Qwen3.8-27B / GX10 — 衍生数据与决策结论（2026-09-03）

这份页面把已经完成的实测转换成**更容易用于工程决策的衍生数据**。数值来自当前 Formal100：1×GX10 / Qwen3.8-27B / 32,768 input + 256 output / Concurrency=1 / 1 warmup 后主批次。它不新增 benchmark，也不把未测项补成实测。

> 这三条 canonical Formal100 是 `cache_state=warm`、`comparison_mode=platform_optimized`、Evidence B、`partial_suite_metrics`。相对比较基于相同 runner workload 维度、seed、warmup 数和并发；它们不是 frozen suite 的 cold-cache 完整 isolation 结果。

指标定义统一见：[Benchmark 指标统一解释](../metrics/benchmark-metrics-glossary.md)。Canonical results 见：[results/qwen38-27b-v1.0/gb10-01](../../results/qwen38-27b-v1.0/gb10-01/)。

## 1. Formal100 基线

| Precision | Effective Prefill* (tok/s) | Pure Prefill | TTFT (ms) | TPOT (ms/token) | Decode (tok/s) | E2E (ms) | Completion |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| BF16 | 936.453 | 未单独测 | 34991.596 | 252.447 | 3.961 | 99365.625 | 100/100 |
| FP8 | 1187.130 | 未单独测 | 27602.710 | 156.783 | 6.378 | 67582.360 | 100/100 |
| NVFP4 | 1300.614 | 未单独测 | 25194.249 | 110.122 | 9.081 | 53275.252 | 100/100 |

\* `Effective Prefill = 32768 / TTFT(s)`；是 Derived，不是 Pure Prefill `pp_tps`。

## 2. 相对 BF16 的性能收益

| Precision | Effective Prefill gain | TTFT reduction | TPOT reduction | Decode gain | E2E reduction | E2E speedup |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| FP8 vs BF16 | +26.77% | -21.12% | -37.89% | +61.02% | -31.99% | 1.470× |
| NVFP4 vs BF16 | +38.89% | -28.00% | -56.38% | +129.24% | -46.38% | 1.865× |

这说明低精度收益不是只出现在 Decode：首 token 和完整请求耗时也同时改善。

## 3. NVFP4 相对 FP8

| 指标 | NVFP4 相对 FP8 |
| --- | ---: |
| Effective Prefill | +9.56% |
| TTFT | -8.73% |
| TPOT | -29.76% |
| Decode | +42.37% |
| E2E | -21.17% |
| E2E speedup | 1.269× |

**工程含义：** NVFP4 相对 FP8 的主要增益来自生成阶段（Decode +42.37%），首 token 链路仍有约 9.56% Effective Prefill 收益。

## 4. 单请求绝对时间节省

百分比之外，直接看每个 32K+256 请求少等多少秒：

| 对比 | TTFT 少等 | Post-first-token 少等* | E2E 少等 |
| --- | ---: | ---: | ---: |
| FP8 vs BF16 | 7.389 s | 24.394 s | 31.783 s |
| NVFP4 vs BF16 | 9.797 s | 36.293 s | 46.090 s |
| NVFP4 vs FP8 | 2.408 s | 11.899 s | 14.307 s |

\* `Post-first-token = E2E - TTFT`，是同一批均值的 Derived 差值，不是 pure decode kernel time。

这对交互式 Agent 更直观：NVFP4 相比 BF16，每次请求平均约 **提前 9.8 秒开始回复、提前 46.1 秒完成**。

## 5. 100 请求整批时间成本

| Precision | 100 请求总耗时 | 相对 BF16 节省 | 节省比例 |
| --- | ---: | ---: | ---: |
| BF16 | 2h45m36.6s | — | — |
| FP8 | 1h52m38.3s | 52m58.3s | 31.99% |
| NVFP4 | 1h28m47.5s | 1h16m49.0s | 46.38% |

NVFP4 相对 FP8 再节省约 **23m50.7s / 100 requests**，约 21.17%。这是本轮最直接的“机器时间成本”结论之一。

## 6. 实测批处理能力：Requests / Hour

由 Formal100 实际总 duration 反推当前串行 workload 的有效请求处理能力：

```text
requests/hour = completed_requests / benchmark_duration_seconds × 3600
```

| Precision | Measured requests/hour | 相对 BF16 | 相对 FP8 |
| --- | ---: | ---: | ---: |
| BF16 | 36.23 | — | — |
| FP8 | 53.27 | +47.03% | — |
| NVFP4 | 67.57 | +86.51% | +26.86% |

这个指标不是通用“QPS 上限”，而是**当前 32K+256、Concurrency=1 的实测等效批处理速度**。对串行 Agent 队列/离线任务预算很有用。

## 7. E2E 时间结构：瓶颈正在迁移

把 E2E 粗分为 `TTFT` 与 `E2E - TTFT` 两段：

| Precision | TTFT share of E2E | TTFT (s) | Post-first-token tail (s) | Tail share of E2E |
| --- | ---: | ---: | ---: | ---: |
| BF16 | 35.21% | 34.992 | 64.374 | 64.79% |
| FP8 | 40.84% | 27.603 | 39.980 | 59.16% |
| NVFP4 | 47.29% | 25.194 | 28.081 | 52.71% |

**重要结论：** 随着 Decode 大幅加速，TTFT/输入处理在 E2E 中的占比从 BF16 的约 35% 提升到 NVFP4 的约 47%。所以在 NVFP4 上继续只优化 Decode，边际收益会下降；**Prefill/TTFT 正在成为下一阶段更值得优化的瓶颈。**

注意：`E2E - TTFT` 是端到端剩余时间，不是严格 pure decode kernel time；这里描述的是**相对瓶颈占比迁移**，不是说 NVFP4 的 Prefill 变慢。NVFP4 的 Effective Prefill 仍是三档最快。

## 8. Formal100 稳定性衍生指标

### 8.1 CV — 相对波动

| Precision | TTFT CV | TPOT CV | E2E CV |
| --- | ---: | ---: | ---: |
| BF16 | 1.199% | 0.843% | 0.963% |
| FP8 | 0.835% | 0.762% | 0.732% |
| NVFP4 | 0.774% | 0.780% | 0.713% |

三档在当前 Formal100 内的相对波动都约 1% 或更低；NVFP4 的 TTFT/E2E CV 最低。

### 8.2 P99 tail：百分比和“多等几秒”

| Precision | TTFT P99 vs mean | TTFT P99 多等 | TPOT P99 vs mean | E2E P99 vs mean | E2E P99 多等 |
| --- | ---: | ---: | ---: | ---: | ---: |
| BF16 | +4.04% | +1.414 s | +2.32% | +2.71% | +2.691 s |
| FP8 | +3.31% | +0.914 s | +3.17% | +3.37% | +2.276 s |
| NVFP4 | +3.68% | +0.928 s | +2.86% | +3.25% | +1.729 s |

P99 没有数量级放大。当前最慢约 1% 请求相对均值多出的 E2E 等待仍约 1.7～2.7 秒；它不能替代 24h soak、长输出或长上下文稳定性。

## 9. Formal5 → Formal100 可重复性

| Precision | TTFT drift | TPOT drift | Decode drift | E2E drift | Effective Prefill drift |
| --- | ---: | ---: | ---: | ---: | ---: |
| BF16 | -6.65% | -4.67% | +4.89% | -5.38% | +7.13% |
| FP8 | -0.16% | +0.50% | -0.50% | +0.23% | +0.16% |
| NVFP4 | +0.29% | +0.12% | -0.12% | +0.20% | -0.29% |

FP8/NVFP4 的阶段均值与 Formal100 高度接近；BF16 多轮 Formal5 有明显状态变化，因此更不能挑一个 5-run 代表最终性能。

## 10. Runner 聚合吞吐、峰值与单请求速度

| Precision | Request throughput (req/s) | Output throughput (tok/s) | Peak output throughput (tok/s) | Total token throughput (tok/s) | Single Decode (tok/s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| BF16 | 0.010064 | 2.576338 | 5.00 | 332.347664 | 3.961 |
| FP8 | 0.014797 | 3.787954 | 7.00 | 488.646127 | 6.378 |
| NVFP4 | 0.018770 | 4.805214 | 10.00 | 619.872662 | 9.081 |

`Peak output throughput` 来自 vLLM 的 `max_output_tokens_per_s` runner metric，**不是 cap**。`Output throughput` 把 TTFT/input-processing 摊进整场 wall-clock；Decode 则回答首 token 后的单请求生成速度。

## 11. 当前最有价值的决策结论

1. **当前 warm 32K+256 workload 的综合效率排序稳定：NVFP4 > FP8 > BF16。** 排序同时体现在 Effective Prefill、TTFT、TPOT、Decode、E2E、duration 与 requests/hour；
2. **NVFP4 的最大优势来自 Decode，但瓶颈已向 TTFT/Prefill 迁移。** 相对 FP8，Decode +42.37%，Effective Prefill +9.56%；TTFT 已占 NVFP4 E2E 的约 47%；
3. **真实时间成本差异很大。** NVFP4 相对 BF16 每请求平均少约 46.1 秒；每 100 requests 少约 76m49s；
4. **等效串行处理能力接近翻倍。** 当前 workload 下 NVFP4 约 67.6 requests/hour，BF16 约 36.2，提升约 86.5%；
5. **FP8/NVFP4 的 Formal5→Formal100 漂移很小。** 对当前 workload，小样本 gate 对 warm-batch 正式均值有较好的预测性；
6. **BF16 对阶段状态更敏感。** 这一结论来自多轮 latency/throughput 的真实变化，不再用 `max_output_tokens_per_s` 的错误“限速”解释；
7. **当前 100/100 + 低 CV/P99 tail 是批次稳定证据，不是系统长期稳定证据；**
8. **Hardware Gate 与性能/质量是不同证据链。** FP8/NVFP4 kernel/hardware path 已闭环，但不能自动推出质量；
9. **这批结果是 partial suite evidence。** 有 warmup 且缺 Pure Prefill/Peak Memory/KV/cold-cache/long-output 等，不应标成完整 frozen suite PASS。

## 12. 有公式但本轮故意不做的“伪衍生”

下面这些虽然可以拿当前均值硬算，却会跨越实测边界，因此**不进入正式结论**：

- 用 256-output TPOT 外推 8K/32K output 完成时间；
- 用 32K Effective Prefill 线性外推 128K/256K/1M TTFT；
- 用启动/诊断日志里的 KV 信息外推目标 context Peak Memory；
- 用 100-request 完成率外推 24h failure rate；
- 用 Hardware Gate 推导模型质量；
- 用单 GX10 结果推导 2×/4× scaling efficiency。

这些都必须新增真实测试。

## 13. 仍然不能从现有数据算出的东西

- Pure Prefill `pp_tps`；
- 正式 cold-cache isolation 结果；
- 正式 `E2E@32K`（32K input + 32K output）；
- 128K / 256K / 384K / 512K / 768K / 1M 同合同性能和稳定性；
- 目标 context 下 Peak Device/Host Memory 与 KV Cache；
- 24h soak / reboot / crash recovery；
- 模型质量、代码质量、长上下文语义保持；
- 多 GX10 scaling efficiency。

这些保持 **未测 / 不可计算**。
