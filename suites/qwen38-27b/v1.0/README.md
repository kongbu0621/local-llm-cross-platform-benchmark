# Qwen3.8-27B Cross-Platform Work Benchmark v1.0

状态：**FROZEN FOR INITIAL DATA PREPARATION**

本 suite 是本仓库第一套正式跨平台测试母本。后续 GB10、RTX PRO 6000、Mac 以及实际购入的其他硬件，均应复用本 suite 的冻结定义；方法变化必须发布新版本。

## Model Arms

### A — BF16 Golden Reference

- Repo: `Qwen/Qwen3.8-27B`
- Revision: `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0`
- HF tree size observed: ~55.6 GB
- Role: 最高质量参考基线

### B — Official FP8

- Repo: `Qwen/Qwen3.8-27B-FP8`
- Revision: `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a`
- HF tree size observed: ~30.9 GB
- Role: 官方高质量量化对照

### C — NVFP4

- Repo: `unsloth/Qwen3.8-27B-NVFP4`
- Revision: `9e3d73c76eddb75f795cc24ccfbc5affe41c66bd`
- HF tree size observed: ~23.4 GB
- Role: Blackwell 低精度性能/长上下文候选

> Revision 在 suite v1.0 中锁定。若上游 `main` 更新，不得静默跟随。

## Hardware Axis

当前第一方正式计划：

1. `gb10-01` — 1× NVIDIA GB10
2. `pro6000-01` — RTX PRO 6000 Blackwell 96GB
3. 未来实际到手的 Mac / 2×GB10 / 其他硬件按同一合同追加

未实际拥有的硬件不产生第一方成绩。

## Context Axis

### Native/Core

- 32K
- 128K
- 256K

### Extended/Deep Dive

- 384K
- 512K
- 768K
- 1M

任何 `Actual Context` 必须来自真实执行，不得把配置上限当测试结果。

## V1.0 Quality Core

- GPQA Diamond — high-difficulty reasoning
- IFBench — strict instruction following
- HumanEval+ — fast coding regression
- LiveCodeBench — main coding quality
- LongBench v2 — real long-context reasoning
- Needle-in-a-Haystack — retrieval grid
- NoLiMa — semantic long-context retrieval

受限制/有访问条件的数据只保留 manifest、来源、revision、hash 和获取说明，不将受限制原题提交到公共仓库。

## Performance Core

使用固定 tokenizer revision 与 deterministic seed 生成 exact-token payload。

固定 Context：32K / 128K / 256K；Deep Dive 再扩展到 384K / 512K / 768K / 1M。

至少记录：

- PP tok/s
- TTFT
- Decode/TG tok/s
- E2E@32K
- Peak Memory / KV
- Cache State
- Concurrency
- Stability

## Quality Isolation Pass

BF16 / FP8 / NVFP4 第一轮质量比较：

- MTP/speculative decoding: OFF
- Prefix Cache: OFF
- Concurrency: 1
- KV precision: 尽量统一并单独记录
- Prompt / tokenizer / sampling / seed: 按相同测试合同固定

目标：先测权重量化本身对质量与基础性能的影响。

## Production Optimization Pass

在 isolation pass 完成后，允许按平台开启：

- MTP / speculative decoding
- Prefix cache
- platform-specific kernels
- KV quantization
- concurrency / batching

必须标记 `comparison_mode=platform_optimized`，不得与 isolation 结果混为一谈。

## Output Stability

V1.0 包含固定 32K 长输出测试。若实际生成不足 32,768 tokens、early EOS、重复退化、乱码或崩溃，则 E2E@32K 记为失败，不外推速度。
