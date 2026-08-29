# Runners

Runner 是“怎么测”的实现层，与 suite（“测什么”）和 hardware（“在哪测”）分离。

计划支持的 runner family：

- `vllm/`
- `sglang/`
- `llama-cpp/`
- `mlx/`
- 未来实际需要的 ROCm/XPU 等路径

## Runner Contract

每次正式运行必须能导出或记录：

- runtime name/version/commit
- 完整启动命令
- model path/revision
- weight precision / KV precision
- configured context
- actual input/output tokens
- cache state
- concurrency/batch
- sampling/reasoning config
- raw timing data
- memory telemetry
- stability outcome

不同 runner 的平台特有指标可以追加，但核心字段必须落入统一 result schema。
