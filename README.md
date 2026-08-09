# logic-folding-placer

架构师做层指派决策时，缺少物理后果的量化反馈。这个仓库用 placement 实验数据，逐节回应 [agentic_tao_physical_design_flow](https://github.com/hengliao1972/agentic_circuit_optimizer/blob/main/agentic_tao_physical_design_flow.md) 的构想——哪些能做了、哪些还差。

> 当前是离线分析——placement 跑完 → 读 DEF → 做统计。离 TAO 构想的在线 Agent 闭环还需要 placer 工具侧的增量接口。

## 回应 §1.2：细粒度逻辑折叠

TAO 判断分割方案的质量直接决定 PPA。gcd 上测了：

| 架构师想知道 | 数据 |
|---|---|
| 3D 省多少线？ | 同面积同密度，3D HPWL = 2D × 79% |
| 长线真的受益？ | 20µm 以上 90% 变短（p<0.001），5µm 以下 86% 变长 |
| 层指派保留信号组了吗？ | 总线 req_msg/resp_msg 完整在 Die1；匿名逻辑分散 |
| HBT 密度有风险？ | 221 个，1.5µm pitch 下 11% bin 溢流 |
| 单元被移了多少？ | 平均位移 47µm，r=0.919 |

详见 [gcd_analysis.md](docs/gcd_analysis.md)

## 回应 §3.1–§3.2：观测粒度与查询即报告

TAO 批判了批处理模型的"观测粒度失配"。我们在 placement 完成后从 DEF/Verilog 提取了逐网线、逐单元的数据——观测粒度达到了细粒度，但不是增量的。缺少"事务级变异 API"和"增量传感器"。

## 回应 §3.3：单一真源

用 DEF + Verilog + partition 三个文件按实例名 join。gcd 上覆盖率 100%（301/301）。但依赖工具命名保真度，没有一致性保证。

## 回应 §2.3：路径感知分割器

异质 3D placer 已实现切分与布局联合执行。但 partition_input 是软约束，Agent 改 tier 可能被 2.5D 覆盖。无增量接口。

## 从路线二到路线三

需要工具侧支持：

1. **增量 placement**：改一个 tier 不用全量重跑
2. **结构化输出**：JSON/API 替代 DEF 解析
3. **Tier 硬约束**：Agent 说"这 50 个锁在 Die0"
4. **穿透综合的稳定 ID**：前端标注到门级网表的归因链

## jpeg 实验（暂停）

同引擎 2D/3D 对比的前提条件不满足。待 DREAMPlace 2D 的 Verilog bus 修复后继续。[jpeg_analysis.md](docs/jpeg_analysis.md)

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
