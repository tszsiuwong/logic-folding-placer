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

- 工具：HeteroPlace3D v20260807（基于 DREAMPlace）
- 基准：NanGate45 3D（TaiWei-Pin-3D），同质双 Die 堆叠
- GPU：NVIDIA TITAN RTX 24GB，CUDA 13.0

## 当前进展

### 完成

- [x] gcd（~412 实例）3D placement：66s，9.80M HPWL
- [x] 完整分析框架：partition 解析 → HPWL 追踪 → 模块聚类 → 规则提取
- [x] 图形输出：Bottom Die vs Top Die 布局对比

### 核心发现

1. **总线信号同层保留**：req_msg（32 条）、resp_msg（16 条）全在 Die1，未被切散
2. **匿名逻辑随机切分**：257 个通用门 45/55 分布，placer 无结构性线索
3. **面积不对等**：3D 用双倍硅面积（2A vs A），HPWL 对比不公平
4. **HBT 不可见**：236 个 hybrid bonding terminal 只在 log 中，不出现在输出 DEF

### 受阻

- [ ] 纯 2D baseline：四种方式均失败——当前 heteroplace3d 不支持
- [ ] 模块亲和性：gcd 层级太浅，需更大设计验证

## 文档

| 文件 | 内容 |
|------|------|
| [gcd_analysis.md](docs/gcd_analysis.md) | gcd 完整分析报告 |
| [worklog.md](docs/worklog.md) | 实验过程日志（踩坑记录） |
| [gcd_3d_placement.png](docs/gcd_3d_placement.png) | 3D 布局可视化 |

## 关联仓库

- [logic-folding-geometry](https://github.com/tszsiuwong/logic-folding-geometry) — 几何分析（Step 1）
- [agentic_circuit_optimizer](https://github.com/hengliao1972/agentic_circuit_optimizer) — TAO 全流程设计文档
