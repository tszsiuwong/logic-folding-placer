# logic-folding-placer

架构决策的物理后果量化——从 placement 数据中回答架构师关心的问题。

## 为什么需要这个

架构师决定模块的层次归属、数据通路的跨层边界、键合点的密度预算。这些决策直接影响 PPA，但传统流程中，架构师能看到的反馈只有一个全局 HPWL 数字。

HPWL 降了 2%——是所有线均匀改善，还是一半变好一半变坏？关键路径上的那几根线到底怎样了？"模块 A 和 B 分到不同层"这个决策的物理代价是多少？

这些问题在传统 EDA 流程中没有答案。本仓库试图用实验数据回答其中一部分。

## 方法

不从 placer 的报告里 grep。直接从 placement 的标准输出文件（DEF、Verilog、partition）中读数据，按实例名对齐，在 Python 里做统计。详细方法见 [agent_friendliness.md](docs/agent_friendliness.md)。

## 当前实验：gcd（301 实例）

### 实验条件

| | 2D | 3D |
|---|---|---|
| 工具 | OpenROAD RePlAce | heteroplace3d |
| Die 面积 | 44.61×40.79 µm (1819 µm²) | 2 × 31.54×28.84 µm (1819 µm²) |
| 利用率 | 23.6% | 23.6% |

### 架构决策 → 量化反馈

| 架构师想知道 | 数据 |
|---|---|
| 3D 堆叠全局省多少线长？ | 3D HPWL = 2D × 79% |
| 长线真的受益吗？ | 20µm 以上线 90% 变短（p<0.001）；5µm 以下线 86% 变长 |
| 层指派是否保留了有结构的信号组？ | 总线 req_msg (32)/resp_msg (16) 完整在 Die1；匿名逻辑分散 45/55 |
| 键合点密度有风险吗？ | 1.5µm pitch：11% bin 溢流，最大 2× 容量 |
| 单元在 3D 中被移动了多少？ | 平均位移 47.4µm，r=0.919（离中心越远位移越大） |

### 局限

- 只在极小设计（301 实例）上验证
- 数据来自 placement 最终输出，非增量观测
- 没有时序信息
- 分析描述"发生了什么"，不替代架构决策

## 文档

| 文件 | 内容 |
|------|------|
| [agent_friendliness.md](docs/agent_friendliness.md) | 方法论文档：架构决策的物理后果量化 |
| [gcd_analysis.md](docs/gcd_analysis.md) | gcd 实验详细数据 |
| [worklog.md](docs/worklog.md) | 实验过程记录 |

## 关联仓库

- [logic-folding-geometry](https://github.com/tszsiuwong/logic-folding-geometry) — 3D 折叠的几何分析
- [agentic_circuit_optimizer](https://github.com/hengliao1972/agentic_circuit_optimizer) — TAO 全流程设计文档
