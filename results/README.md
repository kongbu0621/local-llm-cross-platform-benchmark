# Results

本目录只保存通过 `schemas/benchmark-result.schema.json` 的正式结构化结果。

## Rules

- 每个 result 必须有唯一 `experiment_id`
- 必须指向精确 suite、hardware node、model revision 与 runtime
- `Actual Context` 使用真实输入 token，不使用配置上限
- 失败实验也保存 result，并在 `stability` 中明确错误类型
- Evidence C 第三方参考必须 `comparison_mode=community_reference`
- 历史结果不覆盖；状态通过 `valid / superseded / invalidated` 表达

建议路径：

```text
results/<suite_id>/<node-or-topology>/<experiment_id>.json
```

公开主表应由这些结构化结果生成，而不是手工复制数字。
