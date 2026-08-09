# jpeg 实验数据

**设计**: jpeg_encoder（39,866 实例，48,436 网线，47 IO），NanGate45 同质双裸片堆叠。

> ⚠️ 2D 和 3D 的密度未对齐。2D placer 天然向中心聚集（bbox/die 偏低），3D placer 将单元铺满 die。密度对齐前，HPWL 对比不具物理意义。

## 实验条件

| | 2D | 3D |
|---|---|---|
| 工具 | OpenROAD 26Q1（RePlAce） | heteroplace3d v20260807 |
| 全局利用率 | 35% | 35% |

## 已尝试的 2D 版本

| 版本 | Die (µm²) | bbox/die | HPWL | 说明 |
|---|---|---|---|---|
| aligned | 232,324 | 55% | 220,252 µm | 同面积，但单元挤在中心 |
| tight | 140,000 | 90% | 237,061 µm | 缩 die 去空白，仍有 10% 空隙 |

3D：总 232,184 µm²，每 Die bbox/die = 98%，HPWL = 349,983 µm。

![2D Tight vs 3D](../figures/jpeg_2d_tight.png)

## 密度问题

2D placer 在 35% 利用率下单元自然向中心聚集——线长优化驱使。`-density 0.7` 不改变单元分布。`-routability_driven` 待测试。3D placer 的 die 面积由输入 DEF 固定，单元被迫满铺。两个 placer 在同等利用率下的空间分配策略不同，是目前 2D/3D 公平对比的核心障碍。

## 3D Placement 详情

| 指标 | 值 |
|------|-----|
| 工具 | heteroplace3d v20260807 |
| 耗时 | 198s |
| Die | 每 Die 342×340 µm（116,092 µm²），总 232,184 µm² |
| 层分布 | Die0=19,735（49.4%），Die1=20,178（50.6%） |
| HBT | 11,587 |
| 局部密度（20µm bin） | P50=72%，0% 空 bin |
| 最终 HPWL | 485,570 µm（placer 内部报告） |

![3D Dies](../figures/jpeg_3d_dies.png)

![3D Density](../figures/jpeg_3d_density.png)

## 2D Placement 详情

| 指标 | 值 |
|------|-----|
| 工具 | OpenROAD 26Q1（RePlAce + ABCDPlace） |

## 待完成

- [ ] 密度对齐（routability_driven 或缩小 die 到 98% bbox）
- [ ] 逐网线 2D/3D 对比
- [ ] 逐单元位移分析
- [ ] HBT 溢流分析
- [ ] 模块亲和性分析（FDCT/Zigzag 层级）
