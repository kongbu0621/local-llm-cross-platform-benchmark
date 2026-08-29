# Hardware Comparison Rules

## 1. Hardware status

硬件状态枚举：

- `planned`: 规划/候选，不代表购买承诺，不进入正式结果
- `owned`: 已实际拥有，但尚未完成对应 suite 的正式 benchmark
- `tested`: 已完成至少一组满足证据要求的正式 benchmark
- `retired`: 已退役，历史结果继续保留
- `external`: 第三方参考硬件，仅用于 Evidence C

只有 `owned/tested/retired` 的真实第一方设备可以产生第一方结果；`planned` 不允许出现推测分数。

## 2. Hardware Model、Physical Node、Topology 分离

必须区分：

- Hardware Model：例如 NVIDIA GB10、RTX PRO 6000
- Physical Node：实际机器实例
- Topology：例如 1×GB10、2×GB10 TP2、4×GB10 等

同一硬件型号的不同节点数量/互连拓扑是不同测试对象。

## 3. Strict Comparable vs Platform Optimized

### Strict Comparable

尽可能固定模型、精度、KV、runtime、workload、sampling、cache、concurrency，仅改变硬件。

### Platform Optimized

允许不同平台使用原生最佳路径，例如：

- NVIDIA: CUDA / vLLM / SGLang / NVFP4 等
- Apple: Metal / MLX / Apple 适配量化
- AMD: ROCm 路径
- Intel: XPU / oneAPI / SYCL 路径

结果必须标记 comparison_mode，禁止把不同优化栈的结果包装成“纯硬件差异”。

## 4. Multi-node

多节点结果必须额外记录：

- node_count
- node IDs
- interconnect 类型
- link speed / MTU
- RDMA 是否启用
- TP / DP / EP
- 通信库版本
- 单节点 baseline（若存在）

## 5. OS / Driver 是实验维度

同一硬件在不同 OS、kernel、driver、CUDA/ROCm/Metal/XPU 栈下可以形成独立实验。不得只写 GPU 名称而省略系统软件环境。

## 6. 价格与成本

若记录成本，只保存带日期的观察值：

- hardware_price_observed
- currency
- price_date
- condition（new/used/refurbished 等）

不得把动态价格写成硬件永久属性。
