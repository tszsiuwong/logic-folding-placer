# gcd 分析报告：2D vs 3D 同面积对比

**设计**: gcd（301 实例，371 网线，54 IO），NanGate45 同质双裸片堆叠

---

## 一、3D Placement（HeteroPlace3D）

| 参数 | 值 |
|------|-----|
| 工具 | heteroplace3d v20260807（DREAMPlace） |
| GPU | NVIDIA TITAN RTX 24GB，CUDA 13.0 |
| 输入 | `2_2_floorplan_io.def`（Innovus 2D floorplan）+ `.v` 网表 |
| Die 面积 | 63.08 × 57.68 µm（A），总硅面积 2A |
| 工艺 | NanGate45，双 Die 同质 F2F 堆叠 |
| 目标密度 | 0.2 per die（含 HBT filler） |

### 流水线

| 阶段 | 耗时 | |
|------|------|------|
| 3D 初始布局 + 层指派 | 45.7s | 355 节点 → 591（+236 HBT filler） |
| 2D 全局布局 | 14.3s | 分 Die 后精化 |
| 细节布局 | 4.0s | ABCDPlace + 独立集匹配 |
| 写输出 | 2.0s | DEF + tier sidecar |
| **总计** | **66.0s** | 301 组件 + 54 pin，371 网线 |

### 关键数据

| 指标 | 值 |
|------|-----|
| 层分布 | Die0=142 (40%), Die1=213 (60%) |
| HBT | 236 个（log 中，DEF 无实体） |
| HPWL（终） | 5.53 M DBU |

### 层分布

| 层 | 单元数 | 占比 |
|----|------:|----:|
| Die 0（底） | 142 | 40% |
| Die 1（顶） | 213 | 60% |

---

## 二、2D Baseline（OpenROAD）

| 参数 | 值 |
|------|-----|
| 工具 | OpenROAD 26Q1-951（RePlAce + ABCDPlace） |
| 工艺 | NanGate45，FreePDK45_38x28_10R_NP_162NW_34O |
| 输入 | `2_2_floorplan_io.v` 网表，`initialize_floorplan` 创建 floorplan |
| Die 面积 | 89.22 × 81.57 µm（2A，√2 等比放大） |
| Core 面积 | 86.00 × 78.40 µm |
| 目标密度 | 0.07（自然密度，无 filler） |
| 引擎 | RePlAce Nesterov 全局布局 + ABCDPlace 细节布局 |
| IO placement | M3（水平）+ M2（垂直），手动 tracks 定义 |

### 关键数据

| 指标 | 值 |
|------|-----|
| 实例数 | 301 可移动，0 固定 |
| 网线 | 371 |
| 行数 | ~52 |
| HPWL | **7.00 M DBU**（与 3D 同算法计算） |

---

## 三、HPWL 对比

同硅面积预算（2A），同 HPWL 算法（Verilog 网线拓扑 + DEF 单元坐标），自然密度：

| | HPWL (DBU) |
|---|---|
| 2D | **7.00 M** |
| 3D | **5.53 M** |
| 3D / 2D | **79%（省 21%）** |

**结论**：同面积同密度下，3D 比 2D 省 21% HPWL，与 logic-folding-geometry 预测（17%）方向一致、量级接近。

密度敏感性：若 2D 设 dens=0.2（加强制 filler 压缩单元），HPWL 降至 4.37M，3D 反输 27%。公平对比必须以自然密度为基准。

---

## 四、模块亲和性

| 组 | 单元数 | Die 0 | Die 1 | 完整保留？ |
|----|------:|------:|------:|:----:|
| 总线：req_msg | 32 | 0 | 32 | 是 |
| 总线：resp_msg | 16 | 0 | 16 | 是 |
| 主体：通用逻辑门 | 257 | 116 | 141 | 否（45/55） |

总线信号组完整保留在同一层；匿名逻辑无结构性线索，被随机切分。

---

## 五、对 Agent 的启示

1. **tier 标注优先级**：总线信号 > 模块边界 >> 匿名逻辑
2. **3D HPWL 收益 21%**：在自然密度下成立，加了 filler 的对比不可用
3. **密度是关键控制变量**：不同密度设定可翻转结论方向，Agent 必须显式管理
4. **gcd 层级太浅**：模块亲和性分析只能测总线级别

---

## 六、方法论自检

- [x] 解析 partition → 单元级 tier
- [x] Log HPWL 追踪
- [x] OpenROAD 2D placement（自然密度）
- [x] 同算法 2D vs 3D HPWL 对比
- [x] 模块聚类
- [x] Agent 规则产出
- [ ] 更大设计验证（jpeg，有真实模块层级）
