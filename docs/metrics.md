# Metrics Contract

## Performance

| Field | Definition |
|---|---|
| `pp_tps` | Prompt Prefill throughput，按实际输入 token 计算 |
| `ttft_ms` | 请求发出到首个输出 token 的 wall-clock 时间 |
| `decode_tps` | 首 token 后到最后 token 的持续生成速度 |
| `e2e_wall_ms` | 请求发出到最后 token 接收完成的总 wall-clock 时间 |
| `inter_token_p50_ms` | 输出 token 间隔 P50 |
| `inter_token_p95_ms` | 输出 token 间隔 P95 |
| `inter_token_p99_ms` | 输出 token 间隔 P99 |

## E2E@32K

固定合同：

- Input: **32,768 actual tokens**
- Output: **32,768 actual generated tokens**
- Concurrency: **1**
- Cache: **Cold**
- Timing boundary: API/request 发出 → 最后一个 token 完整接收

若出现 early EOS、长度不足、错误、超时或服务崩溃，则 `e2e_32k.status != pass`，不得按短输出速度外推。

## Memory

至少记录：

- model_weights_bytes（可获得时）
- kv_cache_bytes（可获得时）
- runtime_workspace_bytes（可获得时）
- peak_device_memory_bytes
- peak_host_memory_bytes
- swap_bytes
- `measurement_method`

Unified Memory、VRAM、Host RAM 的测量口径必须明确，不直接把不同平台工具输出当作完全等价指标。

## Quality

V1 Core 质量维度：

- Reasoning
- Instruction Following
- Coding
- Long-context Retrieval
- Long-context Reasoning
- Output Stability

原始 benchmark 分项永久保留；任何 composite score 只能作为派生指标，不能替代原始成绩。

## Stability

至少记录：

- completed
- error_class
- error_message / evidence reference
- early_eos
- repetitive_output
- gibberish
- oom
- server_crash
- timeout
- context_truncated

长时间测试可增加：1h / 8h / 24h 连续运行状态、内存泄漏与吞吐衰减。

## Power / Thermals

条件允许时记录：

- idle_w
- avg_prefill_w
- avg_decode_w
- peak_w
- peak_temperature_c
- throttling_observed

可派生 `tokens_per_joule`，但必须保留功耗测量工具和采样方法。

## Multi-node

多节点时额外记录：

- node_count
- interconnect
- link_speed
- RDMA
- TP / DP / EP
- communication stack / NCCL 等版本
- single-node baseline
- speedup
- scaling_efficiency

`scaling_efficiency = speedup / node_count`。
