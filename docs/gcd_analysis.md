# gcd 实验数据：架构决策的物理后果

**设计**: gcd（301 实例，371 网线，54 IO），NanGate45 同质双裸片堆叠。Rent p = 0.698。

> 本文档是 [agent_friendliness.md](agent_friendliness.md) 中描述的方法在 gcd 上的具体实验数据。读本文档前建议先读那篇——它解释了为什么做这些分析。本文档只记录数据。

## 实验条件

| | 2D | 3D |
|---|---|---|
| 工具 | OpenROAD 26Q1（RePlAce） | heteroplace3d v20260807 |
| Die 面积 | 44.61×40.79 µm (1819 µm²) | 2 × 31.54×28.84 µm (1819 µm²) |
| 利用率 | 23.6% | 23.6% |
| HPWL | 3500 µm | 2765 µm |
| 3D/2D | — | 79% |

---

## 一、3D 堆叠的全局效果

3D HPWL 为 2D 的 79%。但逐线看，265 条网线中 129 条变短、134 条变长——近乎五五开。

![Per-net HPWL](../figures/gcd_per_net_hpwl.png)

## 二、线长与收益：长线受益，短线受损

| 2D 线长 | 网线数 | 变短 | 变长 | 均值比 | 95% CI | p(H₀:ratio=1) |
|---|---|---|---|---|---|---|
| 0–2 µm | 51 | 11% | 86% | 5.25 | [3.73,6.78] | <0.001 |
| 2–5 µm | 53 | 33% | 64% | 1.91 | [1.48,2.34] | <0.001 |
| 5–10 µm | 51 | 45% | 54% | 1.31 | [1.07,1.54] | 0.013 |
| 10–20 µm | 59 | 59% | 40% | 0.88 | [0.74,1.03] | 0.106 ns |
| 20–100 µm | 44 | 90% | 9% | 0.60 | [0.52,0.68] | <0.001 |

Spearman ρ = −0.64（p = 5×10⁻³²）。20µm 以上显著变短，10–20µm 为过渡带。

![Ratio CI](../figures/gcd_ratio_ci.png)

| 长度区间 | 2D 网线数 | 3D 网线数 | 变化 |
|---|---|---|---|
| 0–2 µm | 51 | 37 | −27% |
| 2–20 µm | 163 | 194 | +19% |
| 20–50 µm | 40 | 34 | −15% |
| 50–100 µm | 4 | 0 | −100% |

中位数 2D=7.5 µm → 3D=7.7 µm。方差从 19.2 压缩到 9.0。

![Wirelength Distribution](../figures/gcd_wl_dist.png)

## 三、层指派

| 组 | 单元数 | Die 0 | Die 1 | 保留？ |
|----|------:|------:|------:|:----:|
| 总线 req_msg | 32 | 0 | 32 | 是 |
| 总线 resp_msg | 16 | 0 | 16 | 是 |
| 通用逻辑门 | 257 | 116 | 141 | 否 |

同/跨 Die 邻居在 2D 上的原始距离均为 41µm。

![Die Map](../figures/gcd_disp_diemap.png)

## 四、键合点密度

221 个 HBT。1.5µm pitch 约束下，11% bin 溢流，最大 2× 容量。

![HBT Positions](../figures/gcd_hbt_pos.png)

![HBT Overflow](../figures/gcd_hbt_congestion.png)

![HBT Density](../figures/gcd_hbt_density_dist.png)

## 五、2D→3D 位移

| 分位 | 位移 (µm) |
|------|-----:|
| P50 | 43.7 |
| mean ± σ | 47.4 ± 20.1 |
| max | 88.5 |

位移与离 2D 中心距离的 r = 0.919。

![Displacement Histogram](../figures/gcd_disp_hist.png)

![Correlation](../figures/gcd_disp_corr.png)

![Vectors](../figures/gcd_disp_vec.png)

## 六、实验环境细节

### 2D Placement

| 参数 | 值 |
|------|-----|
| 工具 | OpenROAD 26Q1-951（RePlAce + ABCDPlace） |
| Floorplan | 44.61×40.79 µm，1819 µm² |
| 利用率 | 23.6%，自然密度 |

![2D Placement](../figures/gcd_2d.png)

![2D HPWL Journey](../figures/gcd_2d_journey.png)

### 3D Placement

| 参数 | 值 |
|------|-----|
| 工具 | heteroplace3d v20260807（DREAMPlace） |
| GPU | NVIDIA TITAN RTX 24GB |

上 Die：31.54×28.84 µm，909 µm²，利用率 23.1%，159 单元。  
下 Die：31.54×28.84 µm，909 µm²，利用率 24.1%，142 单元。  
Offset (0,0)，F2F 对齐。

| 层 | 单元数 | 单元面积 (µm²) | 利用率 |
|----|------:|--------:|------:|
| Die 0（底） | 159 | 210 | 23.1% |
| Die 1（顶） | 142 | 219 | 24.1% |

![3D Dies](../figures/gcd_3d_dies.png)

### HPWL 逐阶段

| 阶段 | 耗时 | 总 HPWL | Die0 | Die1 |
|------|------|------:|------:|------:|
| 3D 初始布局 | 45.7s | 2,499 µm | — | — |
| 2D 全局布局 | 14.3s | 12,370 µm | 5,529 | 6,887 |
| HBT 映射 | ~0s | 7,737 µm | 2,985 | 4,752 |
| 细节布局 | 4.0s | 4,902 µm | 2,071 | 2,832 |
| **总计** | 66.0s | — | — | — |

![HPWL Journey](../figures/gcd_hpwl_journey.png)

## 局限

- 只在极小设计（301 实例）上验证
- 数据来自 placement 最终输出，非增量观测
- 没有时序信息
- 实例名 join 在当前实验中覆盖率 100%，综合重命名后未知