# 架构决策的物理后果：一种量化反馈方法

## 问题

架构师决定一个模块放在哪一层、两条数据通路是否共享一个 Die、关键路径的跨层边界画在哪。这些决定直接影响最终的 PPA——但传统流程中，架构师在下一次 placement 完成后能看到的反馈只有一个全局 HPWL 数字。

HPWL 降了 2%——是所有线均匀变短了，还是一半变长一半变短？关键路径上的那几根线到底怎么样了？模块 A 和 B 分到不同层的决策，对 HBT 密度有什么影响？

这些问题在传统 EDA 流程中没有答案。不是工具不行——是工具输出的粒度不足以回答架构级问题。架构决策的物理后果，处于"知道有影响、不知道影响多大"的灰区。

## 这个方法试图做什么

在 gcd（301 实例）上，我们做了一个尝试：在 placement 完成后，从 DEF、Verilog 和 partition 文件中提取每个单元和每条网线的 2D/3D 对比数据，然后向上聚合到架构师关心的维度。

具体来说：

1. **架构决策："这条数据通路的关键路径应该保持在同一层"**
   - 能回答什么：同 Die 内的网线在 3D 中的 HPWL 变化（Die0 内 71%，Die1 内 76%）；跨 Die 网线在 2D 中原有多长（平均 15.3µm vs Die 内 7.9µm）

2. **架构决策："键合点密度在这个区域的预算是 X"**
   - 能回答什么：以 1.5µm pitch 为约束，221 个 HBT 中有 11% 的 bin 超出容量，最大溢出 2×；溢流集中在 die 中心区域

3. **架构决策："这个模块不应该被 placer 切碎"**
   - 能回答什么：同名总线信号（req_msg 32 条、resp_msg 16 条）被完整保留在 Die1；匿名逻辑门的 257 个实例则被分散在两层（45/55）

4. **架构决策的全局影响**
   - 能回答什么：3D 整体 HPWL 为 2D 的 79%；但逐线统计显示 129 条变短、134 条变长，50/50。20µm 以上的线 90% 受益（p<0.001），5µm 以下的线 86% 受损

## 方法

所有分析不需要修改 EDA 工具代码。数据来源是 placement 的标准输出文件：

| 数据 | 来源 |
|------|------|
| 单元坐标 (2D/3D) | DEF COMPONENTS |
| 网表拓扑 | Verilog |
| 层指派 | partition sidecar / DEF cell type 后缀 |
| HBT 位置 | dbl_custom_write Terminal |
| 单元尺寸 | DBL LibCell |

将这些文件在 Python 中按实例名 join，构成一个临时的分析数据库。从 join 到完成上述全部统计，约 30 秒。

## 局限

这个尝试只在 gcd（301 实例）上做过。更大设计上的可行性、实例名 join 在综合重命名后的覆盖率、时序信息的整合——都未经验证。

但最根本的局限是：以上所有分析都在 placement 完成后做静态统计。它把一个架构决策的物理后果量化出来，但不替代决策本身。架构师仍然需要判断：20µm 是长还是短、溢流 11% 是否可接受、某个模块"应该"在哪一层。

## 从当前 EDA 流程到 TAO Agent 的差距

本文档描述的东西——从 DEF/Verilog 提取数据、按实例名 join、做统计——本质上是给批处理 EDA 流程加了一层事后分析。它和 [agentic_tao_physical_design_flow](https://github.com/tszsiuwong/agentic_circuit_optimizer/blob/main/agentic_tao_physical_design_flow.md) 中构想的 Agent 系统之间，还有结构性的差距。

### TAO 设想的理想工具接口（§3.2）

| 契约 | TAO 设想 | 当前状态 | 差距 |
|------|---------|---------|------|
| 稳定 ID | 跨迭代稳定的单元/网/路径标识 | DEF 实例名在单次 run 中稳定；跨综合/迭代未验证 | 名存实亡——综合重命名是已知风险 |
| 事务级变异 API | `move_cells(ids, tier=1)` 毫秒级 | 无。每次变动需要全量重跑 placer（66s） | 结构性缺失——不是性能差距 |
| 增量传感器 | 改 100 个单元后毫秒级更新受影响路径 | 无。只能在 placement 完成后做静态统计 | 同上 |
| 查询即报告 | 结构化记录，非文本文件 | 文本文件（DEF/Verilog）+ 自定义 Python 解析 | 数据格式不对——需要反向工程 DEF 语法 |
| 快照与分支 | 设计状态可廉价快照、fork、diff | 无 | 缺失 |
| 全程归因键 | 每条记录可回溯到源码行 | 仅达到门级网表的实例名；未穿透综合 | 缺失 |

### 从路线二到路线三的关键缺口

当前实验对应 [agentic_tao_physical_design_flow](https://github.com/tszsiuwong/agentic_circuit_optimizer/blob/main/agentic_tao_physical_design_flow.md) 的路线二（补丁增强）的位置：保留开源 placer 做 placement，在外面包一层分析代码提取数据。实验表明这条路在极小规模上走得通。

但要走向路线三（一体化新工具），以下缺口是绕不开的：

1. **增量 placement 是硬前提。** 没有增量，Agent 的"每步变异→评估"循环就跑不起来。66 秒的全量重跑意味着百轮探索需要两小时——内环不成立。

2. **placer 需要输出结构化数据，而不是依赖外部解析。** 当前实验从 DEF 正则提取坐标、从 Verilog 解析拓扑——每一层都是脆弱的格式适配。新工具应该以 API 或结构化文件格式直接输出"每个单元的 (x,y,tier)"和"每条网线的 HPWL"。

3. **Tier assignment 需要硬约束模式。** 当前 partition_input 是软约束，2.5D 阶段会覆盖。Agent 需要能力说"这 50 个单元锁死在 Die0，其余自由"。

4. **需要穿过综合的稳定 ID。** 如果前端标注（"这是译码逻辑"）无法在综合后的门级网表中定位对应单元，归因链就断了。这是端到端闭环的前置条件。

## 结论

所有后端分析、EDA 工具、placement 实验——最终都服务于 [agentic_tao_physical_design_flow](https://github.com/tszsiuwong/agentic_circuit_optimizer/blob/main/agentic_tao_physical_design_flow.md) 中构想的 Agent 系统。本文档描述的静态分析方法在极小规模上证明了"细粒度量化反馈"的可行性，但要实现 TAO 文档设计的闭环，还需要 placer 工具侧的四个关键改进（增量 placement、结构化输出、tier 硬约束、稳定 ID）。