# Agent × EDA：为什么是革命性的

> 基于 gcd case 的完整实验流程。

## 传统 EDA 的分析瓶颈

传统 EDA 工具是批处理黑盒：输入 DEF/Verilog → 跑数小时 → 输出巨型报告和 log。分析靠 grep + 人工读报告。

以本次 gcd 实验为例，传统流程下你能拿到的是：

- heteroplace3d 的 66 秒运行日志（2.2MB 文本）
- OpenROAD 的 placement 报告（"legalized HPWL 2557.1 u"）
- 最终 DEF 文件

**这些信息不足以回答任何有意义的分析问题。** 你不会知道哪根线变长了、HBT 有没有溢流、20µm 以上的线是不是可靠受益。

## Agent 改变了什么

Agent 不依赖工具的报告格式。Agent 直接读 DEF 坐标、Verilog 网表拓扑、中间输出文件，用 Python 做结构化分析。以下是我们在此次 gcd 实验中实际完成的分析，传统流程下**每一项都需要数天手工劳动或根本做不到**：

### 逐网线统计学分析

| 分析 | 方法 | 传统 EDA |
|------|------|----------|
| 129 变短 / 134 变长 | Verilog 网表 + 2D/3D DEF 坐标 | 需要 Tcl 逐网线 `report_net`，265 条网线 × 手动 |
| Spearman ρ = −0.64, p=5×10⁻³² | scipy.stats.spearmanr | 无内置统计功能 |
| 95% CI + t-test 确定 20µm 阈值 | scipy.stats.ttest_1samp | 需要导出到 R/Python 再做 |
| 分区间统计 5 个 bucket | numpy 数组运算 | 逐区间手工 grep 分类 |

### 逐单元位移分析

| 分析 | 方法 | 传统 EDA |
|------|------|----------|
| r=0.919 位移-距离相关 | 2D/3D DEF 同名实例对位 | Tcl 逐单元 `get_property [get_cells X] x_location`，301 个 × 手工 |
| dx=−29.3, dy=−26.1 方向偏差 | numpy 向量运算 | 无工具 |

### HBT 密度与溢流

| 分析 | 方法 | 传统 EDA |
|------|------|----------|
| 221 个 HBT 位置提取 | dbl_custom_write 输出 Terminal 行 | 无工具——HBT 是内部数据 |
| 11% bin 溢流, 最大 2× 容量 | KDTree + numpy 二维直方图 | 无工具 |

### 层指派行为

| 分析 | 方法 | 传统 EDA |
|------|------|----------|
| 同/跨 Die 邻居 2D 距离相同（41µm） | 分组统计 + 邻居搜索 | 逐网线手工 |
| Rent 指数 p=0.698 | 递归谱分割 | 无工具 |

## 这不是"自动化"，是"不可能 → 可能"

上述每一项分析在传统 EDA 中都不是"费时间"的问题——**是根本做不到**。传统工具的设计目标是"产出可签核的版图"，不是"让工程师理解 placer 的行为"。

Agent 的价值不在于替代 placer，而在于填补"placer 能跑但人类无法理解"的分析真空。**这个真空过去不存在，因为过去没人做这么细粒度的 placer 行为研究。** TAO 物理设计流程要求理解 placer 的每一层行为——没有 Agent，单靠人工就是天文数字的工作量。

## 当前工具对接状态

| 能力 | 状态 | 数据来源 |
|------|------|----------|
| 2D/3D DEF 坐标读取 | ✅ 直接用 | 最终 DEF |
| 网表拓扑解析 | ✅ 直接用 | Verilog |
| partition 层指派 | ✅ 直接用 | sidecar `.def.partition` |
| HBT 位置 | ✅ 直接用 | `dbl_custom_write` Terminal 行 |
| 单元面积 | ✅ 直接用 | DBL LibCell 条目 |
| 3D 逐迭代 HPWL | ✅ 直接用 | log → BIHPWL |
| Cell 类型识别 | ✅ 直接用 | DBL / LEF |
| t-test, CI, 相关 | ✅ scipy.stats | Python |
| 增量 placement | ❌ 需工具支持 | — |
| partition 硬约束 | ❌ 需工具支持 | — |
| 结构化 JSON 输出 | ❌ 需工具支持 | — |

## 结论

Agent 友好的 placer 不是"在 placer 外面包装一套 API"。而是：**placer 输出足够的结构化数据，Agent 能用通用编程语言做统计学分析。** 当前的 heteroplace3d + OpenROAD 已经输出了足够的数据来做这件事——缺的不是新工具，缺的是有人写分析代码。Agent 填补了这个空缺。
