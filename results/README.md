# Results

本目录保存通过 `schemas/benchmark-result.schema.json` 的正式结构化结果。`results/` 是 README 主表和后续自动汇总的 canonical machine-readable source；`evidence/` 保存更原始的日志、profiler、环境和过程证据。

## Rules

- 每个 result 必须有唯一 `experiment_id`；
- 必须指向精确 suite、hardware node、model revision 与 runtime；
- `Actual Context` 使用真实 input/output token，不使用配置上限；
- Measured / Derived / Unmeasured 必须区分；没有 Pure Prefill 就令 `pp_tps=null`；
- cache/warmup 与 `comparison_mode` 必须真实记录，warm result 不得冒充 cold-cache strict comparison；
- 部分完成 suite 是合法结果，但应使用明确的 `coverage_status`，不能把 partial result 描述成完整 suite PASS；
- 失败实验也保存 canonical result；不存在的 latency/throughput 使用 `null`，不能把 raw runner 的 0 当作性能；
- Evidence C 第三方参考必须 `comparison_mode=community_reference`；
- 历史结果不覆盖；状态通过 `valid / superseded / invalidated` 表达；
- 公共 README 主表由这些结构化结果生成/校验，不手工维护另一套数字。

路径：

```text
results/<suite_id>/<node-or-topology>/<experiment-id>.json
```

当前 GX10 初始结果：

```text
results/qwen38-27b-v1.0/gb10-01/
├── 20260901-bf16-formal100-32k256.json
├── 20260901-fp8-formal100-32k256.json
├── 20260831-nvfp4-formal100-32k256.json
└── 20260831-nvfp4-b0-gpu085-failed.json
```

前三条是 1 warmup 后的 32K+256 warm Formal100，Evidence B、`platform_optimized`、`partial_suite_metrics`；最后一条保存 B0 failed attempt。Formal5 当前作为阶段/过程 evidence 保留，未提升为首页 canonical ranking result。
