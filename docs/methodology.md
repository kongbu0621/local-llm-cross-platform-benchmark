# Benchmark Methodology

## 1. 目标

本仓库构建的是 **Local LLM 可复现实测能力地图**，不是单一 tokens/s 排行榜。

每个正式实验都必须回答：

- 测的是什么模型与精确 revision？
- 在什么真实硬件、OS、驱动与 runtime 上运行？
- 权重精度与 KV 精度分别是什么？
- 实际输入了多少 token（Actual Context）？
- 输出长度、并发、缓存状态、sampling/reasoning 配置是什么？
- 性能、质量、内存与稳定性结果是什么？
- 是否存在可复现证据？

## 2. 三类测试必须分开

### Quality / Canonical Benchmark

遵循对应公开 benchmark 的 canonical protocol。不同 benchmark 可以有不同 sampling 规则，不强行统一 temperature。

### Performance / Controlled Hardware Benchmark

为了比较硬件、量化和 runtime，固定 workload、输入 token、输出 token、并发与 cache 状态，尽量一次只改变一个变量。

### Production / Platform-Optimized Benchmark

允许每个平台使用适合自己的最佳 runtime、kernel、speculative decoding、KV 精度、prefix cache 等优化。此结果用于回答“实际每天使用哪个方案最好”，不得与 Controlled 结果混为一谈。

## 3. Core Matrix + Selective Deep Dive

不穷举所有组合。

### Core Matrix

每个重要模型至少覆盖：

- 32K / 128K / 256K
- Concurrency = 1
- Cold Cache
- 主流高质量权重格式
- 主流 runtime
- Quality + Performance + Stability 基础项

### Deep Dive

对重要或表现突出的模型继续覆盖：

- 384K / 512K / 768K / 1M
- MTP / speculative decoding
- Prefix Cache
- KV quantization
- 多并发
- 长时间稳定性
- 功耗、温度、Scaling Efficiency
- Agent / repo-level workload

## 4. 对比规则

### 严格可比层

尽可能固定：

- model source revision
- tokenizer / chat template
- prompt / dataset revision
- sampling / seed
- output limit
- cache state
- concurrency
- runtime source revision（条件允许时）

### 平台最优层

允许 NVIDIA CUDA、Apple MLX/Metal、AMD ROCm、Intel XPU/oneAPI 等使用各自更合适的原生路径，但必须明确记录所有差异。

## 5. Actual Context

`Configured Context` 与 `Actual Context` 必须分开。

只有模型实际完成了对应输入长度的 prefill/任务，才能记录该 `Actual Context`。不得用 runtime 参数上限、模型卡上限或短上下文外推填表。

对长上下文至少分别记录：

- configured_context_tokens
- actual_input_tokens
- prefill_completed
- output_completed
- retrieval/reasoning quality
- TTFT
- decode rate
- memory
- stability

## 6. 失败数据

以下都属于正式结果：

- OOM
- unsupported kernel / format
- server crash
- CUDA / ROCm / Metal / XPU error
- deadlock
- NaN
- gibberish
- repetitive output
- early EOS
- context truncation
- timeout
- memory leak

失败结果不得为了“表格完整”而用另一套配置静默替代。

## 7. 版本与历史

Suite 一旦发布，其测试母本和定义不得静默修改。

- 小幅兼容修正：新 patch/minor 版本
- 指标、任务或方法论变化：新 minor/major 版本
- 历史结果可标记 `superseded` / `invalidated`，但必须保留

## 8. 主结果边界

主结果只收录维护者实际拥有并实际运行的硬件。第三方社区结果必须单独标为 Evidence C，不能伪装成第一方实测。
