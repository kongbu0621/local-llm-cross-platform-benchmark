# Dataset Policy

本目录保存 **数据集定义、来源、revision、许可/访问条件、下载方法、文件清单与 SHA256**，而不是无条件镜像第三方原始数据。

## Public Repo 原则

可以提交：

- dataset manifest
- 官方 source URL
- revision / release / split
- license / access notes
- 下载或生成脚本
- 本地文件 SHA256
- 允许公开的自有 synthetic workload

默认不提交：

- 有访问条件/保密要求的 benchmark 原题
- 第三方许可证不允许再分发的内容
- 用户私有工程数据
- 模型权重
- 任何账号 token / cookie / proxy credential

## Local Layout

第一方机器建议使用：

```text
~/xxj/data/
├── datasets/
├── needle/
├── long-context/
├── coding/
├── prompts/
└── manifests/
```

仓库中的 manifest 是可复现合同；本地原始数据以 manifest 的 hash 验证。

## Freeze Rule

一个 suite 的数据集选择可以先冻结，但只有在 `revision + file list + SHA256` 补齐后，才进入 `materialized` 状态。

数据更新不得覆盖旧 manifest；发布新 suite 版本。
