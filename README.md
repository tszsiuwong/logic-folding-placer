# logic-folding-placer

架构师做层指派决策时，缺少物理后果的量化反馈。这个仓库用 placement 实验数据，逐节回应 [agentic_tao_physical_design_flow](https://github.com/hengliao1972/agentic_circuit_optimizer/blob/main/agentic_tao_physical_design_flow.md) 的构想。

## 一、TAO 问了什么，我们答了多少

| TAO § | TAO 原文 | PD+EDA 侧的对应事务 | 初步结论 |
|-------|---------|-------------------|---------|
| §1.2 | "分割方案的质量直接决定最终 PPA" | 逐网线 HPWL 对比 | 长线受益(90%)，短线受损(86%) |
| §2.2 步骤 2 | "输出每个单元的层指派 + 层间连接表" | 层分布、信号组保留 | 总线保留、匿名逻辑分散 |
| §3.1 | "全设计文本报告要智能体自己 grep" | DEF/Verilog 逐网线提取 | 静态可做、增量未及 |
| §3.3 | "设计状态散落在十几种文件格式里" | DEF+Verilog+partition join | 实例名 join 可达 100% |
| §2.2 步骤 5 | "键合点数量与信号网数量同量级" | HBT 密度、溢流 | 11% bin 溢流、最大 2× |
| §3.2 | "理想工具是作为智能体工具集存在的 EDA" | 增量接口、结构化输出 | 缺失 |
| §2.2 步骤 4 | "线长模型须把层间连接作为第三维短边" | 同引擎 2D/3D 公平对比 | 引擎差异未消除 |
| §5.1 | "后端环：变异→LEC→增量STA→Pareto" | 离线 vs 在线闭环 | 缺失 |

## 二、我们现在做了哪些

**回应 §1.2（细粒度折叠）**

同面积同密度下，3D HPWL = 2D × 79%。但收益不均——20µm 以上线 90% 变短（p<0.001），5µm 以下 86% 变长。中位数几乎没动（7.5→7.7µm），收益来自剪掉超长尾。

**回应 §2.2 步骤 2（分割质量）**

层指派保留了总线信号组（req_msg 32 条、resp_msg 16 条完整在 Die1），匿名逻辑门被分散（257 个实例 45/55）。同 Die 和跨 Die 的单元在 2D 上的原始距离相同（41µm）——层指派与 2D 空间邻近性无关。

**回应 §3.1（观测粒度）+ §3.3（单一真源）**

从 DEF/Verilog/partition 中提取数据，不需要修改任何 EDA 工具。gcd 上实例名 join 覆盖率 100%（301/301），30 秒内完成全部分析。但这是 placement 完成后的静态分析，不是增量观测。

**回应 §2.2 步骤 5（键合点）**

221 个 HBT，1.5µm pitch 下 11% bin 溢流，最大 2× 容量。HBT 位置从 `dbl_custom_write` 输出的 Terminal 行提取。

详见 [gcd_analysis.md](docs/gcd_analysis.md)

jpeg（40K 实例）因同引擎 2D/3D 对比的前提条件不满足，实验暂停。数据见 [jpeg_analysis.md](docs/jpeg_analysis.md)。

## 三、我们能推动合作者一起做的

TAO 文档 §2.1 列出了完整的 SOTA 工具链。与 OpenROAD / DREAMPlace 团队迭代推进：

| TAO 步骤 | 开源工具 | 需要什么 |
|----------|---------|---------|
| ① 综合 | Yosys + ABC | tier 标注穿透 |
| ② 路径感知分割 | DREAMPlace / OpenROAD 3D | tier 硬约束、增量接口、结构化输出 |
| ③ 布图规划 | OpenROAD | 多层耦合 PDN |
| ④ 3D 布局 | DREAMPlace / OpenROAD 3D（**已覆盖**） | 增量评估 |
| ⑤-⑦ 键合点/CTS/布线 | OpenROAD | 跨层感知、HBT 合法化 |
| ⑧ STA | OpenSTA / HeteroSTA | 跨层统一时序图 |
| ⑨ 热/IR | OpenROAD | 增量热估计 |
| ⑩-⑪ 签核/LEC | 商业 EDA | 多层 DRC/LVS、LEC |

同时：自动化分析管线（config→placement→数据→报告，一键完成）、更大 benchmark（jpeg → ariane133）、DREAMPlace 2D 跑通后做同引擎 2D/3D 公平对比。

## 四、我们想做但还没做到的：和架构师一起定义反馈通道

TAO 在多处描述了架构师做判断、Agent 和 EDA 提供数据支撑的协作模式。以下是几个具体场景及当前差距：

**§2.4：架构师布设 tier 意图后，需要看到物理后果**

> 人负责外层动作——布设模块级 tier 意图与 jump_tier 候选点（定义搜索空间）。

架构师标注了"模块 A 在 Die0、模块 B 在 Die1"，下一步需要知道这个决策的物理后果——HPWL 变化、HBT 密度、是否导致局部溢流。这些数据我们可以从 placement 结果里提取（gcd 已验证），但目前需要手动跑 placement → 手动分析 → 手动汇总，没有自动化的反馈通道。

**§2.4：Agent 改动了 hint 标注，架构师需要审查**

> 审查 hint 改写 diff 中的反直觉结果、批准 locked 升级。

Agent 在探索中移动了某些 hint 态单元，产生了 diff。架构师需要看到"哪些单元被改了、从哪层到哪层、对 HPWL 和 HBT 的预估影响是多少"。这个 diff 的物理后果量化正是我们可以做的，但目前 Agent 本身不存在，diff 也不存在。

**§5.2：架构师需要定期看到端到端的物理 PPA**

> 端到端环的定位是校准环——定期对前端 Pareto 档案上的活跃点跑端到端，修正前端代理模型的偏差。

这需要在每次前端变异后自动触发综合→布局→分析→汇总 PPA 报告。我们的分析管线可以输出这份报告，但目前是离线手动的。

**§3.6.2：Agent 发现冲突，架构师需要裁定**

> Agent 不自行裁定，输出冲突报告，提交外层（人）裁决。

架构师收到冲突报告后，需要的不是原始数据，而是"如果选方案 A，HPWL 预计 X；如果选方案 B，HPWL 预计 Y"。这种 what-if 对比需要增量 placement 才能做——目前不存在。

---

四个场景的共同缺口：**数据能产生，但到架构师手里的通道没建立。** 下一步需要和架构师一起定义这条通道——什么频率、什么格式、什么粒度。

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
