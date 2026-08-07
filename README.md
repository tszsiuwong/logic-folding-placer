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

- [x] gcd 2D baseline（OpenROAD，同面积 2A，自然密度） + 3D placement（heteroplace3d）
- [x] 同面积同算法 2D vs 3D HPWL：**7.00M vs 5.53M，3D 省 21%**
- [x] 完整分析框架：partition 解析 → HPWL 追踪 → 模块聚类 → 规则提取
- [x] 可视化：2D vs 3D Bottom/Top 等比缩放对比图
- [x] Agent 友好性评估

### 核心发现

1. **3D 省 21% HPWL**：同面积自然密度下，与 geometry 预测（17%）方向一致
2. **密度决定结论**：dens=0.20（强制 filler）时 3D 反输 27%，公平对比须用自然密度
3. **总线信号同层保留**：req_msg（32）、resp_msg（16）全在 Die1
4. **匿名逻辑随机切分**：257 个门 45/55，无结构性线索

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
