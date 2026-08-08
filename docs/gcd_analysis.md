# gcd 分析报告：2D vs 3D 同面积对比

**设计**: gcd（301 实例，371 网线，54 IO），NanGate45 同质双裸片堆叠  
**Rent 指数**: p = 0.698（递归谱分割，R² = 0.813）——CPU 控制逻辑典型范围

---

## 一、3D Placement（HeteroPlace3D）

| 参数 | 值 |
|------|-----|
| 工具 | heteroplace3d v20260807（DREAMPlace） |
| GPU | NVIDIA TITAN RTX 24GB，CUDA 13.0 |
| 输入 | `2_2_floorplan_io.def`（Innovus 2D floorplan）+ `.v` 网表 |
| Die 面积 | 63.08 × 57.68 µm（A），总硅面积 2A，双 Die F2F 堆叠 |
| 目标密度 | 0.2 per die（含 HBT filler） |

### 流水线

| 阶段 | 耗时 | |
|------|------|------|
| 3D 初始布局 + 层指派 | 45.7s | 355 节点 → 591（+236 HBT filler） |
| 2D 全局布局 | 14.3s | 分 Die 后精化 |
| 细节布局 | 4.0s | ABCDPlace + 独立集匹配 |
| 写输出 | 2.0s | DEF + tier sidecar |
| **总计** | **66.0s** | 301 组件 + 54 pin，371 网线 |

### 层分布

| 层 | 单元数 | 占比 |
|----|------:|----:|
| Die 0（底） | 142 | 40% |
| Die 1（顶） | 213 | 60% |

![3D Bottom vs Top Die](../figures/gcd_3d_dies.png)

---

## 二、2D Baseline（OpenROAD）

| 参数 | 值 |
|------|-----|
| 工具 | OpenROAD 26Q1-951（RePlAce + ABCDPlace） |
| 工艺 | NanGate45，FreePDK45_38x28_10R_NP_162NW_34O |
| 输入 | `2_2_floorplan_io.v` 网表，`initialize_floorplan` 创建 floorplan |
| Die 面积 | 89.22 × 81.57 µm（2A，√2 等比放大） |
| 目标密度 | 0.07（自然密度，无 filler） |
| 引擎 | RePlAce Nesterov 全局布局 + ABCDPlace 细节布局 |

| 指标 | 值 |
|------|-----|
| 实例 | 301 可移动 |
| 网线 | 371 |
| HPWL | **7.00 M DBU** |

![2D Placement](../figures/gcd_2d.png)

---

## 三、收益来源：压缩 vs 折叠

![2D vs 3D](../figures/gcd_2d_vs_3d.png)

| | HPWL (DBU) |
|---|---|
| 2D | **7.00 M** |
| 3D | **5.53 M** |
| 3D / 2D | **79%（省 21%）** |

> **背景**：在 [logic-folding-geometry](https://github.com/tszsiuwong/logic-folding-geometry) 中，我们曾用完全图（p=1）推导 3D 折叠的几何上界：双 Die 堆叠可节省约 17% 总曼哈顿线长，收益来源是长线（d₂ ≥ 5）被垂直路径替代。本次实验用真实布局器在真实网表上检验这一预测。

**收益数字一致（21% vs 17%），但机制不同。**

| | geometry 预测 | 实测 |
|---|---|---|
| HPWL 收益 | 17% | 21% — 方向一致 |
| 收益来源 | 垂直折叠替代长线（d₂≥5） | **平面压缩：单元被挤到更小面积** |
| 证据 | — | r=0.919：位移由离中心距离驱动；同 Die vs 跨 Die 邻居 2D 距离完全相同 |

placer 并没有利用垂直维度做"把需要靠近的单元叠起来"——同 Die 和跨 Die 的单元在 2D 上的原始距离一样（都是 41µm）。层指派近乎随机。省下的 21% HPWL 主要来自"多了一倍硅面积但单元还是那些"的密度优势，而非跨层链接替代了长线。

geometry 的 17% 是 p=1 完全图假设下的理想值。gcd 实测 p = 0.698（R² = 0.813，递归谱分割），属于 CPU 控制逻辑的典型范围。在这个互联复杂度下，placer 没有采用垂直折叠——收益来自面积压缩，而非跨层链接替代长线。

---

## 四、逐单元 2D→3D 位移分析

301 个实例在 2D 和 3D DEF 中名称完全相同，可精确对位。

### 位移分布

| 分位 | 位移 (µm) |
|------|-----:|
| min | 4.5 |
| P25 | 32.4 |
| P50 | 43.7 |
| P75 | 63.1 |
| max | 88.5 |
| mean ± σ | 47.4 ± 20.1 |

![Displacement Histogram](../figures/gcd_disp_hist.png)

### 距离-位移相关性

**r = 0.919**（极强正相关）。离 2D 中心越远的单元，位移越大——面积压缩效应主导，非 placement 策略差异。

![Correlation](../figures/gcd_disp_corr.png)

### 方向偏差

| | 均值 (µm) | 范围 |
|---|---|---|
| dx | **−29.3** | [−79, +22] |
| dy | **−26.1** | [−73, +15] |

单元整体向原点收缩。2D die 面积 89×82 µm，3D 每 Die 63×58 µm——边角单元被拉回。

### Die 间差异

| Die | 数量 | 平均位移 |
|-----|------|---------|
| Die0 | 159 | 44.6 µm |
| Die1 | 142 | 50.6 µm |

![By Die](../figures/gcd_disp_die.png)

### 位移方向向量

灰色箭头：每个单元从 2D 位置移到 3D 位置的方向和距离。蓝=Die0，橙=Die1。

![Vectors](../figures/gcd_disp_vec.png)

### 位移热力图

颜色越红，位移越大。外围单元被压缩向中心。

![Heatmap](../figures/gcd_disp_heat.png)

### 2D 邻近性与 Die 分配

| 关系 | 平均 2D 距离 |
|------|--------:|
| 分配到同 Die | 41 µm |
| 分配到不同 Die | 41 µm |

**完全相同。** placer 的层指派与 2D 空间邻近性无关——Die 分配近乎随机（除总线信号外）。

![Die Map](../figures/gcd_disp_diemap.png)

---

## 五、模块亲和性

| 组 | 单元数 | Die 0 | Die 1 | 完整保留？ |
|----|------:|------:|------:|:----:|
| 总线：req_msg | 32 | 0 | 32 | 是 |
| 总线：resp_msg | 16 | 0 | 16 | 是 |
| 主体：通用逻辑门 | 257 | 116 | 141 | 否（45/55） |

---

## 六、对 Agent 的启示

1. **tier 标注优先级**：总线信号 > 模块边界 >> 匿名逻辑
2. **3D 省 21% HPWL**：同面积自然密度下成立
3. **placer 不保留 2D 空间邻近性**：Agent 必须通过 partition 硬约束控制层指派
4. **面积压缩（r=0.919）是位移主因**：不同 density 可翻转结论方向
