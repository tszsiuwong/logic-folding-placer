# logic-folding-placer

架构师做层指派决策时，缺少物理后果的量化反馈。这个仓库用 placement 实验数据来填这个空白。

## 做了什么

在 gcd（301 实例）和 jpeg（40K 实例）上跑了 2D/3D placement，从输出文件中提取逐网线、逐单元的数据，向上聚合到架构师关心的维度。

> 这些分析是离线的——placement 跑完 → 读 DEF → 做统计。TAO 构想的在线 Agent 闭环还需要 placer 工具侧的增量接口和结构化输出。

## gcd 实验（完成）

| 架构师想知道 | 数据 |
|---|---|
| 3D 堆叠全局省多少线长？ | 2D/3D 同面积同密度，3D HPWL = 2D × 79% |
| 长线真的受益吗？ | 20µm 以上线 90% 变短（p<0.001）；5µm 以下 86% 变长 |
| 层指派是否保留了有结构的信号组？ | 总线 req_msg/resp_msg 完整在 Die1；匿名逻辑分散 45/55 |
| 键合点密度有风险吗？ | 221 HBT，1.5µm pitch 下 11% bin 溢流 |
| 单元在 3D 中被移动了多少？ | 平均位移 47µm，r=0.919 |

详见 [gcd_analysis.md](docs/gcd_analysis.md)

## jpeg 实验（暂停）

同引擎 2D/3D 对比的前提条件不满足。待 DREAMPlace 2D 的 Verilog bus 修复后继续。详见 [jpeg_analysis.md](docs/jpeg_analysis.md)

## 文档

| 文件 | 内容 |
|------|------|
| [agent_friendliness.md](docs/agent_friendliness.md) | 方法论：架构决策的物理后果量化 |
| [gcd_analysis.md](docs/gcd_analysis.md) | gcd 实验数据 |
| [jpeg_analysis.md](docs/jpeg_analysis.md) | jpeg 实验数据 |
| [worklog.md](docs/worklog.md) | 实验过程记录 |

## 关联仓库

- [agentic_circuit_optimizer](https://github.com/hengliao1972/agentic_circuit_optimizer) — TAO 全流程设计文档
- [logic-folding-geometry](https://github.com/tszsiuwong/logic-folding-geometry) — 3D 折叠的几何分析
