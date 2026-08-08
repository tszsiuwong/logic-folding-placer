# 工作日志：Agent × Placer 迭代探索

## 2026-08-07 ~ 08: gcd 最小可行验证

### 完成

- [x] 3D placement（heteroplace3d）：66s，HPWL 2765 µm
- [x] 2D placement（OpenROAD RePlAce）：HPWL 3500 µm
- [x] 同面积（2A, 1819 µm²）对比：3D/2D = 79%
- [x] 逐单元 2D→3D 位移分析：平均 47.4 µm，r=0.919
- [x] 网线级拆解：71% 跨 Die，长短线分布变化
- [x] HBT 位置提取（221 个）+ 溢流分析（11% bin 超限）
- [x] HPWL 逐阶段收敛图（3D 1000 次迭代 + 2D 三阶段）
- [x] Rent 指数：p = 0.698

### 关键数据

| 指标 | 2D | 3D |
|------|-----|-----|
| HPWL | 3500 µm | 2765 µm |
| 利用率 | 23.6% | 23.6% |
| 跨 Die 网线 | — | 71% |
| 中位线长 | 7.5 µm | 7.7 µm |
| 平均位移 | — | 47.4 µm |
| HBT | — | 221 |
| Rent p | 0.698 | — |

### 踩坑

- 2D baseline：heteroplace3d 不支持纯 2D；OpenROAD 26Q1 pin placement + tracks 需手动配置
- matplotlib MacOSX backend 灰度 bug → 改用 Agg
- scatter `c=` 走 colormap → 改用 `color=`
- edgecolors 覆盖颜色 → 去掉
- log 有 ANSI 转义码 → regex 前先 strip
- 密度计算：从 DBL LibCell 查 cell size 算实际面积

### HBT

- 输出文件 `Terminal` 行即为 HBT 位置（非 IO pin）
- 221 个 HBT，X 2.1–30.0 µm，Y 2.0–25.9 µm
- 1.5 µm pitch 约束：11% bin 溢流，最大 2× 容量
- 当前 heteroplace3d 输出含 HBT 数据（`dbl_custom_write`）

### 视角切换

全部文档从"后端分析 placer 行为"重写为"架构决策的物理后果量化"。不再以后端技术细节为主线，改为以架构师关心的问题为起点，后端数据为回答。详见 `agent_friendliness.md`。

- OpenROAD GPL 逐迭代 HPWL 为 0（已知 bug，只在阶段汇总可用）
- heteroplace3d partition_input 是软约束
- 3D 阶段 HPWL 只有 BIHPWL（bindary HPWL），与 2D 阶段 HPWL 不可比
