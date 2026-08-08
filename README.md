# logic-folding-placer

异构 3D 布局器行为分析——为 Agentic Partition 提供经验规则。

## 定位

TAO 物理设计流程中的**内环引擎**（Step 2）：

```
logic-folding-geometry     →  几何上界预测（纯理论）
    ↓
logic-folding-placer       →  真实 placer 行为分析（本项目）
    ↓
agentic_3d_partition       →  Agent 策略生成
    ↓
agentic_tao_physical_design_flow → 全流程框架
```

目标：从 heteroplace3d 的实验数据中，逆向挖掘 placer 的行为规律，给 Agent 喂经验知识（类似 `logic-folding-geometry` 从几何第一性原理推导出 d₂≥5 阈值）。

## 实验环境

- 3D placer：HeteroPlace3D v20260807（DREAMPlace），TITAN RTX 24GB，CUDA 13.0
- 2D placer：OpenROAD 26Q1-951（RePlAce + ABCDPlace）
- 基准：NanGate45 3D（TaiWei-Pin-3D），同质双 Die F2F 堆叠

## 当前进展

### 完成

- [x] gcd 2D/3D placement，同面积对比：3D/2D = 79%
- [x] 逐单元位移分析：r=0.919，平均 47.4 µm
- [x] 网线级拆解：71% 跨 Die，长短线分布变化
- [x] HBT 数据：221 个，溢流分析（11% bin 超限）
- [x] HPWL 收敛曲线：3D 1000 次迭代 + 2D 三阶段
- [x] Rent 指数：p = 0.698
- [x] Agent 友好性评估

### 核心数据

| 指标 | 2D | 3D |
|------|-----|-----|
| HPWL | 3500 µm | 2765 µm |
| 利用率 | 23.6% | 23.6% |
| 跨 Die 网线 | — | 71% |
| 中位线长 | 7.5 µm | 7.7 µm |
| HBT | — | 221 |
| Rent p | 0.698 | — |

### 受阻

- [ ] 模块亲和性：gcd 层级太浅，需更大设计验证

## 文档

| 文件 | 内容 |
|------|------|
| [gcd_analysis.md](docs/gcd_analysis.md) | gcd 完整分析报告 |
| [worklog.md](docs/worklog.md) | 实验过程日志 |
| [agent_friendliness.md](docs/agent_friendliness.md) | Agent 友好性评估 |
| [gcd_2d_vs_3d.png](figures/gcd_2d_vs_3d.png) | 2D vs 3D 等比对比图 |
| [gcd_displacement.png](figures/gcd_displacement.png) | 逐单元位移分析 |

## 关联仓库

- [logic-folding-geometry](https://github.com/tszsiuwong/logic-folding-geometry) — 几何分析（Step 1）
- [agentic_circuit_optimizer](https://github.com/hengliao1972/agentic_circuit_optimizer) — TAO 全流程设计文档
