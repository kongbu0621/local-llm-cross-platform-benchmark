# Qwen3.8-27B / GX10 — 衍生数据与决策结论（2026-09-03）

这份页面只做一件事：把已经完成的同合同实测转换成**更容易用于决策的衍生数据**。所有数值都来自当前 Formal100（1×GX10 / Qwen3.8-27B / 32,768 input + 256 output / Concurrency=1），不增加新的 benchmark，也不把未测项补成实测。

指标定义统一见：[Benchmark 指标统一解释](../metrics/benchmark-metrics-glossary.md)。

## 1. Formal100 原始基线

| Precision | Prefill* (tok/s) | Pure Prefill | TTFT (ms) | TPOT (ms/token) | Decode (tok/s) | E2E (ms) | Completion |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| BF16 | 936.453 | 未单独测 | 34991.596 | 252.447 | 3.961 | 99365.625 | 100/100 |
| FP8 | 1187.130 | 未单独测 | 27602.710 | 156.783 | 6.378 | 67582.360 | 100/100 |
| NVFP4 | 1300.614 | 未单独测 | 25194.249 | 110.122 | 9.081 | 53275.252 | 100/100 |

\* `Prefill* = Effective Prefill = 32768 / TTFT(s)`；它是实际首 token 链路下的有效输入速度，不是严格 Pure Prefill `pp_tps`。

## 2. 相对 BF16 的性能收益

| Precision | Prefill* gain | TTFT reduction | TPOT reduction | Decode gain | E2E reduction | E2E speedup |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| FP8 vs BF16 | +26.77% | -21.12% | -37.89% | +61.02% | -31.99% | 1.470× |
| NVFP4 vs BF16 | +38.89% | -28.00% | -56.38% | +129.24% | -46.38% | 1.865× |

解释：在本轮 32K+256 workload 下，NVFP4 不只是 Decode 更快；首 token 等待和完整请求耗时也同时下降。FP8 也有明显收益，但幅度低于 NVFP4。

## 3. NVFP4 相对 FP8

| 指标 | NVFP4 相对 FP8 |
| --- | ---: |
| Prefill* | +9.56% |
| TTFT | -8.73% |
| TPOT | -29.76% |
| Decode | +42.37% |
| E2E | -21.17% |
| E2E speedup | 1.269× |

这说明在本轮短输出 workload 中，NVFP4 对持续生成阶段的优势大于对首 token 阶段的优势：Decode 提升约 42%，Prefill* 约提升 9.6%。

## 4. 100 请求整批时间成本

Formal100 的整场 duration：

| Precision | 100 请求总耗时 | 相对 BF16 节省 | 相对 BF16 节省比例 |
| --- | ---: | ---: | ---: |
| BF16 | 2h45m36.6s | — | — |
| FP8 | 1h52m38.3s | 52m58.3s | 31.99% |
| NVFP4 | 1h28m47.5s | 1h16m49.0s | 46.38% |

NVFP4 相对 FP8 进一步节省约 **23m50.7s / 100 requests**，即约 **21.17%**。

这类数字比单独看 tok/s 更接近实际 Agent/批处理成本：同样 100 个 32K+256 请求，NVFP4 比 BF16 少占用约 77 分钟的串行执行时间。

## 5. Formal100 稳定性衍生指标

### 5.1 CV — 相对波动

| Precision | TTFT CV | TPOT CV | E2E CV |
| --- | ---: | ---: | ---: |
| BF16 | 1.199% | 0.843% | 0.963% |
| FP8 | 0.835% | 0.762% | 0.732% |
| NVFP4 | 0.774% | 0.780% | 0.713% |

三种精度在这批 Formal100 里相对波动都约为 1% 或更低；NVFP4 的 TTFT/E2E CV 最低，FP8 与 NVFP4 的 TPOT CV 很接近。

### 5.2 P99 tail amplification

| Precision | TTFT P99 vs mean | TPOT P99 vs mean | E2E P99 vs mean |
| --- | ---: | ---: | ---: |
| BF16 | +4.04% | +2.32% | +2.71% |
| FP8 | +3.31% | +3.17% | +3.37% |
| NVFP4 | +3.68% | +2.86% | +3.25% |

P99 没有出现数量级放大；这说明当前 100-request 短输出批次的尾部可控。但它**不能替代 24h soak、长输出或 256K/512K/1M 上下文稳定性测试**。

## 6. Formal5 → Formal100 可重复性

| Precision | TTFT drift | TPOT drift | Decode drift | E2E drift | Prefill* drift |
| --- | ---: | ---: | ---: | ---: | ---: |
| BF16 | -6.65% | -4.67% | +4.89% | -5.38% | +7.13% |
| FP8 | -0.16% | +0.50% | -0.50% | +0.23% | +0.16% |
| NVFP4 | +0.29% | +0.12% | -0.12% | +0.20% | -0.29% |

FP8 / NVFP4 的 5-request 阶段结果与 100-request 正式结果高度接近；BF16 的多轮 Formal5 已显示明显运行状态差异，所以 BF16 更应该以 Formal100 为正式基线，而不能挑一个 5-run 代表最终性能。

## 7. Runner 聚合吞吐与单请求速度的关系

| Precision | Request throughput (req/s) | Output throughput (tok/s) | Total token throughput (tok/s) | Single-request Decode (tok/s) |
| --- | ---: | ---: | ---: | ---: |
| BF16 | 0.010064 | 2.576338 | 332.347664 | 3.961 |
| FP8 | 0.014797 | 3.787954 | 488.646127 | 6.378 |
| NVFP4 | 0.018770 | 4.805214 | 619.872662 | 9.081 |

`Output throughput` 把 TTFT/input-processing 时间也摊进整场 wall-clock，所以一定低于单请求 Decode。两者回答不同问题：Decode 看“开始输出后的打字速度”，aggregate throughput 看“整条流水线平均吞吐”。

## 8. 当前最有价值的决策结论

1. **速度排序在当前 workload 下非常稳定：NVFP4 > FP8 > BF16。** 这同时体现在 Prefill*、TTFT、Decode 和 E2E，不是只体现在某一个指标。
2. **NVFP4 的主要增益来自 Decode，但首 token 也有收益。** 相对 FP8，Decode +42.37%，Prefill* +9.56%，E2E -21.17%。
3. **FP8 / NVFP4 的 Formal5→Formal100 漂移很小。** 对当前 32K+256 workload，它们的小样本阶段结果具有较好的正式批次预测性。
4. **BF16 的阶段状态更敏感。** 多轮 Formal5 差异说明运行阶段、热状态等因素不能忽略；Formal100 更可信。
5. **100/100 完成 + 低 CV/P99 tail 说明本轮短输出批次稳定。** 但这不是长上下文/长输出/24h 系统稳定性的替代证据。
6. **Hardware Gate 与性能结论是两条不同证据链。** FP8/NVFP4 kernel/hardware path 已闭环，但这不能自动推导模型质量。

## 9. 仍然不能从现有数据算出的东西

下面这些不能靠数学“补出来”，必须新增真实测试：

- Pure Prefill `pp_tps`；
- 正式 `E2E@32K`（32K input + 32K output）；
- 128K / 256K / 384K / 512K / 768K / 1M 的同合同性能与稳定性；
- Peak Memory / KV Cache 在这些目标 context 下的完整工作表；
- 24h soak / reboot / crash recovery 稳定性；
- 模型质量、代码质量、长上下文语义保持；
- 多 GX10 scaling efficiency。

这些必须标记为 **未测 / 不可计算**，不能用当前 32K+256 数据外推。