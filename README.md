# logic-folding-placer

架构师做层指派决策时，缺少物理后果的量化反馈。这个仓库用 placement 实验数据，回应 [agentic_tao_physical_design_flow](https://github.com/hengliao1972/agentic_circuit_optimizer/blob/main/agentic_tao_physical_design_flow.md) 的构想。

## 一、TAO 需要回答的问题全貌

TAO 文档描述了一条从 RTL 到多层版图的完整物理实现链（§2.2，步骤 1–11），并构想了 Agent 在其中扮演的角色（§3，§5）。将这些问题按粒度分层：

| 层次 | 问题 | 我们当前状态 |
|------|------|-------------|
| 单步 placement | 层指派的质量如何？长线是否受益？ | ✅ gcd 已覆盖 |
| placement 过程 | 能否做到 per-move 的增量反馈？ | ❌ 缺少增量接口 |
| 全流程（步骤 3–11） | CTS、布线、STA、热、签核——每一步能否细粒度观测？ | ❌ 未触及 |
| 端到端闭环 | 前端变异 → 综合 → 物理实现 → PPA 回流到架构师 | ❌ 依赖综合和稳定 ID |
| Agent 决策层 | §3.2 的事务 API、快照/分支、归因链 | ❌ 需要工具侧全新设计 |

## 二、我们现在做了哪些

在 gcd（301 实例）上完成了 2D/3D placement 的细粒度分析，回应了 §1.2 的核心判断：

- 同面积同密度，3D HPWL = 2D × 79%
- 20µm 以上线 90% 变短（p<0.001），5µm 以下 86% 变长
- 层指派保留了总线信号组（req_msg/resp_msg 完整在 Die1），匿名逻辑分散
- 221 HBT，1.5µm pitch 下 11% bin 溢流

数据来源：从 DEF/Verilog/partition 文件中提取，不需要修改任何 EDA 工具。

详见 [gcd_analysis.md](docs/gcd_analysis.md)

此外在以下方面做了低保真验证：

- 观测粒度（回应 §3.1）：逐网线 HPWL 对比、逐单元位移、逐 bin HBT 密度——但都是 placement 完成后的静态分析
- 单一真源（回应 §3.3）：DEF + Verilog + partition 按实例名 join，gcd 覆盖率 100%
- 路径感知分割器（回应 §2.3）：确认了 partition_input 是软约束

jpeg（40K 实例）的同引擎 2D/3D 对比因 Verilog bus 问题暂停，待 DREAMPlace 2D 修复后继续。

## 三、我们后面计划做哪些

与 OpenROAD / DREAMPlace 团队迭代，推进以下工具能力：

| TAO 步骤 | 开源工具 | 需要什么 |
|----------|---------|---------|
| ① 综合 | Yosys + ABC | tier 标注穿透 |
| ② 路径感知分割 | DREAMPlace / OpenROAD 3D | tier 硬约束、增量接口、结构化输出 |
| ③ 布图规划 | OpenROAD | 多层耦合 PDN |
| ④ 3D 布局 | DREAMPlace / OpenROAD 3D（**当前已覆盖**） | 增量评估 |
| ⑤-⑦ 键合点/CTS/布线 | OpenROAD | 跨层感知、HBT 合法化 |
| ⑧ STA | OpenSTA / HeteroSTA | 跨层统一时序图 |
| ⑨ 热/IR | OpenROAD | 增量热估计 |
| ⑩-⑪ 签核/LEC | 商业 EDA | 多层 DRC/LVS、LEC |

同时：自动化分析管线、更大 benchmark（jpeg → ariane133）、DREAMPlace 2D 跑通后做同引擎 2D/3D 对比。

## 四、我们想做但还没做到的

TAO 构想的闭环需要后端数据和架构师判断之间的双向通道。我们现在能产生数据，但数据怎么到架构师手里、架构师怎么把决策反馈回来——这个通道不存在。

这是下一步最重要的事：和架构师一起把这条通道定义出来。

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
