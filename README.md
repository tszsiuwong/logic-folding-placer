# logic-folding-placer

通过实验数据回应 [Agentic TAO Physical Design Flow](https://github.com/hengliao1972/agentic_circuit_optimizer/blob/main/agentic_tao_physical_design_flow.md) 的当前状态：哪些能力已有低保真验证，哪些差距仍待填补。

## 我们在做什么

跑了两个 benchmark 的 2D/3D placement：

| | gcd | jpeg |
|---|---|---|
| 实例数 | 301 | ~40K |
| 3D placer | heteroplace3d | heteroplace3d |
| 2D placer | OpenROAD RePlAce | OpenROAD RePlAce |

从 placement 输出中逐网线、逐单元地提取数据，做统计分析。方法详见 [agent_friendliness.md](docs/agent_friendliness.md)。

## 回应 TAO §3.1–§3.2：观测粒度与查询即报告

TAO 文档批判了批处理模型的"观测粒度失配"——Agent 只能看到全设计文本报告，无法做单元/路径级的细粒度观测。

**当前状态**：在 placement 完成后，从 DEF/Verilog/partition 文件中提取数据，实现了逐网线的 2D/3D HPWL 对比、逐单元的位移追踪、逐 bin 的 HBT 溢流分析。但这些分析是静态的——在 placement 完成后做，而非在 placement 过程中做增量观测。

**差距**：缺少"事务级变异 API"（`move_cells(ids, tier=1)`）和"增量传感器"（改 100 个单元后毫秒级更新受影响路径）。当前每次变异需要全量重跑 placer（gcd 66s，jpeg 198s），无法支撑内环的百轮探索。

## 回应 TAO §3.3：单一真源

TAO 文档设想一个统一数据库容纳逻辑、物理、层指派、约束与度量。

**当前状态**：用 DEF + Verilog + partition 三个文件在 Python 中按实例名 join，构成临时的分析视图。gcd 上覆盖率 100%（301/301）。

**差距**：文件级 join 依赖工具命名保真度，无一致性保证。综合重命名后的覆盖率未验证。

## 回应 TAO §1.2：细粒度逻辑折叠的质量

TAO 文档的核心物理假设：分割方案的质量直接决定最终 PPA。

**当前状态（gcd 数据）**：

- 3D HPWL = 2D × 79%
- 逐线统计：129 变短、134 变长（50/50）
- 20µm 以上线 90% 受益（p<0.001），5µm 以下线 86% 受损
- 层指派与 2D 空间邻近性无关（同/跨 Die 邻居原始距离均为 41µm）
- 11,587 个 HBT，1.5µm pitch 下 11% bin 溢流

**差距**：只有 gcd 一个极小设计的完整数据。jpeg 实验进行中。没有时序信息。分析是"跑完了回头看"，不是 per-move 反馈。

## 回应 TAO §2.3：路径感知网表分割器

TAO 文档规格了分割器的核心算法需求：关键度加权的路径折叠、增量接口、稳定 ID。

**当前状态**：异质 3D placer 已实现切分与布局的联合执行，但分割质量取决于线长启发式而非时序关键度。partition_input 是软约束——Agent 改了 tier，2.5D 阶段可能覆盖。

**差距**：无硬约束 tier assignment。无增量接口。placer 不支持"对特定单元簇重指派 tier 并评估增量影响"。

## 从路线二到路线三的关键缺口

结合实验数据，TAO 文档描述的路线三（一体化新工具）需要以下四项工具侧改进：

1. **增量 placement**：没有增量，Agent 的"每步变异→评估"循环无法高频运行
2. **结构化输出**：DEF 正则解析是脆弱的格式适配，新工具应以 API/结构化格式直接输出
3. **Tier 硬约束**：Agent 需要"这 50 个单元锁死在 Die0，其余自由"
4. **穿透综合的稳定 ID**：前端标注到门级网表的归因链不能断

## 文档

| 文件 | 内容 |
|------|------|
| [agent_friendliness.md](docs/agent_friendliness.md) | 方法论：架构决策的物理后果量化 |
| [gcd_analysis.md](docs/gcd_analysis.md) | gcd 实验数据（完整） |
| [worklog.md](docs/worklog.md) | 实验过程记录 |
| [figures/](figures/) | 所有可视化图表 |

## 关联仓库

- [agentic_circuit_optimizer](https://github.com/hengliao1972/agentic_circuit_optimizer) — TAO 全流程设计文档
- [logic-folding-geometry](https://github.com/tszsiuwong/logic-folding-geometry) — 3D 折叠的几何分析
