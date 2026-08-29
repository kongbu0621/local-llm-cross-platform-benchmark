# Evidence Levels

## A — Fully Reproducible

一条正式 A 级结果至少需要：

- 精确 model repo + revision/commit
- weight format / quantization
- tokenizer / chat template revision（适用时）
- hardware profile / node topology
- OS / kernel / architecture
- driver / CUDA / ROCm / Metal / XPU 等版本
- runtime + version/commit
- 完整启动参数
- workload / dataset / prompt revision
- Actual Context / actual output tokens
- cache / concurrency / sampling 状态
- 原始日志或机器可读原始输出
- 结构化 result JSON
- 环境快照
- 关键输入/manifest SHA256

## B — Verified

关键运行条件与结果可核验，但缺少少量 A 级原始证据。例如历史测试缺少完整 raw log，但模型 revision、参数、环境和结果文件均可确认。

B 级可以进入历史对比，但必须显示证据缺口。

## C — Community Reference

来源于第三方论坛、GitHub Issue/Discussion、Reddit、博客等社区实测。

必须记录：

- source URL
- author / publication date（可获得时）
- reported hardware / model / runtime
- reported context 与指标
- 无法确认的字段必须为空，不补猜测

C 级不得与本仓库第一方 A/B 级结果等权合并，也不得进入“第一方实测主榜”。

## Invalid / Superseded

- `invalidated`: 已证明测试配置、数据、计时或语义存在错误
- `superseded`: 仍然有效，但已有更新方法/版本替代

历史文件保留；不得静默修改旧数值来“修正”历史。
