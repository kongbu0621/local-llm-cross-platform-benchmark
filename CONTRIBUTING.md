# Contributing

欢迎提交可复现的本地 LLM 测试改进、runner、schema 修正和第三方参考证据。

## 第一方主结果

仓库维护者的主结果只来自实际拥有并实际运行的硬件。外部贡献者若提交自己的硬件结果，应明确标记贡献者、环境和 evidence；仓库维护者不会把它冒充为维护者第一方实测。

## Result PR 最低要求

建议至少包含：

1. `results/.../<experiment_id>.json`
2. 对应 environment snapshot（去除隐私）
3. raw benchmark log 或可核验原始输出
4. 精确 model revision
5. runtime version/commit 与完整参数
6. dataset/prompt revision 与 hash
7. Actual Context / actual output tokens
8. 失败时保留错误证据

## 不接受

- 仅凭模型卡“支持 1M”填写 1M 实测结果
- 用低上下文数据补高上下文空缺
- 未说明 KV precision / cache / concurrency 的性能数字
- 只贴截图、无法确认关键运行条件的“排行榜成绩”作为 A 级证据
- 模型权重、密钥、Token、代理订阅、私有数据
- 违反第三方数据集许可/访问条款的原题镜像

## Community Reference

论坛、Reddit、GitHub Discussion 等第三方结果可以贡献为 Evidence C，但必须附原始来源 URL，并保留“未知字段为空”的原则，不猜测补齐。
