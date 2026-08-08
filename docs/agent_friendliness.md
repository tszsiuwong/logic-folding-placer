# Agent 友好性评估

> 基于 gcd case 的完整实验流程。

## 可直接使用 ✅

| 能力 | 说明 |
|------|------|
| 2D baseline | OpenROAD RePlAce，LEF/DEF 输入，分钟级 |
| 3D placement | heteroplace3d，分钟级 |
| partition 解析 | sidecar `.def.partition` 文件，cell→tier 映射 |
| HBT 位置 | `Terminal` 行在 DBL 输出中，221 个坐标 |
| 逐单元位移 | 2D/3D DEF 中实例名相同，可对位计算 |
| 网线级 HPWL | Verilog + DEF 同算法计算，可按 Die 内/跨 Die 分类 |
| 单元面积 | DBL `LibCell` 条目查 cell 尺寸 |
| Rent p | 递归谱分割，约 30 秒 |

## 需适配 ⚠️

| 问题 | 影响 |
|------|------|
| HPWL 在 log 文本中 | Agent 需 grep + 正则提取 |
| OpenROAD GPL 逐迭代 HPWL 为 0 | 2D 收敛曲线只有阶段节点 |
| 3D BIHPWL vs 2D HPWL 不可比 | 不能直接做逐迭代对比 |
| 路径全相对 + symlink | 部署耦合 |
| `partition_input` 软约束 | Agent 改 tier 不保证生效 |

## 需工具侧支持 ❌

| 需求 | 说明 |
|------|------|
| 增量模式 | 改一个 tier 需全量重跑（66s） |
| 结构化摘要 | 每次运行输出 JSON/YAML 格式的 PPA |
| partition 硬约束 | locked 态的 tier 不被 placer 覆盖 |
| HBT 写入最终 DEF | 目前只在中间 DBL 输出有 |

## 数据获取方式

| 数据 | 来源 |
|------|------|
| 2D HPWL | OpenROAD log → legalized HPWL，或 Verilog+DEF 同算法 |
| 3D HPWL | heteroplace3d log → detailed placement finished，或 Verilog+DEF |
| HBT 位置 | `dbl_custom_write` 输出 → `Terminal` 行 |
| 单元面积 | `gcd.dbl` → `LibCell` 条目 |
| 网线分类 | Verilog + 3D DEF → 跨 Die vs Die 内 |
| 位移 | 2D DEF + 3D DEF → 同名实例坐标差 |
