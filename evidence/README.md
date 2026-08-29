# Evidence

这里保存允许公开的原始证据，例如：

- 环境快照（已去除 hostname/IP/账号等不必要信息）
- benchmark raw log
- 启动参数
- 结果文件 SHA256
- OOM / crash / timeout 等失败证据

不要提交：Token、cookie、代理订阅、私有 IP、模型权重、受限制题目、私有工程源码或其他敏感数据。

建议路径：

```text
evidence/<suite_id>/<node-or-topology>/<experiment_id>/
```

A 级结果应尽可能让 `results/...json` 能引用到对应 evidence 文件。
