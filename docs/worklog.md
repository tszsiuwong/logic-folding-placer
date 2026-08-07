# 工作日志：Agent × Placer 迭代探索

## 2026-08-07 ~ 08: 最小可行验证 — gcd case

### 做了什么
1. 在服务器（TITAN RTX 24GB）用 `heteroplace3d v20260807` 跑通了 gcd（NanGate45 同质双 Die，~412 实例）
2. 写了解析工具链：DEF 坐标提取、partition 层指派解析、log HPWL 追踪
3. 画了四格对比图：2D 原始 → Bottom Die → Top Die → Folding Map
4. 尝试四种方式获取同面积 2D baseline，全部失败

### 发现了什么

**层分布：**
- Die0=142 (40%), Die1=213 (60%)，placer 没有自然均衡的趋向

**模块亲和性：**
- 总线信号组（req_msg 32条、resp_msg 16条）**完整保留**在同一 Die
- 匿名门级逻辑（257 个单元）被随机 45/55 切分
- gcd 层级太浅，无真正模块结构可分析

**面积幻觉（关键发现）：**
- 3D 用两块等面积 Die（总硅面积 = 2A），2D 用一块（面积 = A）
- 3D 单元分布在双倍面积上，天然密度更低、线更短
- HPWL 下降不能直接归因于"垂直折叠"——需要面积归一化

**HBT 不可见：**
- log 显示 236 个 HBT，但输出 DEF 中无实体
- HBT 是中间评估阶段的虚拟结构

**流水线拆解：**

| 阶段 | 耗时 | HPWL |
|------|------|------|
| 3D 初始布局 + 层指派 | 45.7s | — |
| 2D 全局布局（分 Die 后） | 14.3s | 24.74M |
| HBT 映射 | ~0s | 15.47M |
| 细节布局 | 4.0s | 9.80M |
| 写输出 | 2.0s | — |
| **总计** | **66.0s** | **9.80M** |

物理变换：355 节点 → 591（+236 HBT filler），371 网线 → 607（+236 跨层），最终输出 301 组件。

### 2D baseline 尝试

| # | 方式 | 结果 |
|---|------|------|
| 1 | `global_place_3d_flag: 0` + 单 Die LEF | segfault（target_density 类型不兼容） |
| 2 | `only_2d: 1` + `partition_input` 全 Die0 | 2.5D 阶段覆盖软约束，仍分 204/151 |
| 3 | `dreamplace` 二进制 + DEF 输入 | 找不到 `default` JSON key，不支持 DEF |
| 4 | DBL `NumTechnologies 1` | libtorch segfault |

**结论：当前二进制不支持纯 2D placement。** 需要 Bookshelf 格式转换（走 dreamplace）或源码修改。

### 踩了什么坑
- 服务器基准目录初始有嵌套 `nangate45_3D/nangate45_3D/`，后被整理为 `platform/`
- 2D DEF 多了 `+ SOURCE TIMING` 字段，正则需适配
- HBT 想画但不在输出 DEF 里
- batch 脚本 `set -e` + grep 失败导致静默退出
- matplotlib 中文字体需手动配置
- 四种 2D baseline 方法全部不可行

### 对 Agent 的方法论启示
1. **tier 标注优先级**：总线信号 > 模块边界 >> 匿名逻辑
2. **"3D HPWL < 2D HPWL" 不能作为优化信号**：面积不对等
3. **Agent 需要一个适配层**：把 placer 的输出（DEF/log/partition）转成结构化数据
4. **异构设计（有命名模块层级）是分析亲和性的前提**：gcd 层级太浅

### 下一步（如需继续）
- [ ] 跑 jpeg（23K 实例，有 FDCT/Zigzag 模块层级），验证"模块亲和性"假说
- [ ] 用 OpenROAD 做 2D baseline（走 DEF + OpenDB）
- [ ] 定义 Agent ↔ Placer 最小接口 schema

### 已知限制（截至 2026-08-08）
- heteroplace3d 不支持纯 2D placement，`partition_input` 是软约束
- dreamplace 需 Bookshelf 格式，当前 benchmark 是 DEF
- 同面积 2D vs 3D HPWL 对比不可行——面积预算不对等
- HBT 不出现在输出 DEF 中
- gcd 无模块层级，亲和性分析只能测总线级别

### 仓库产出
| 文件 | 内容 |
|------|------|
| `docs/gcd_analysis.md` | 静态分析报告 |
| `docs/worklog.md` | 本文档 |
| `docs/gcd_2d_vs_3d.png` | 四格对比图 |
| `scripts/plot_placement.py` | DEF 解析 + 画图脚本 |
| `scripts/analyze.py` | partition 解析 + 模块聚类 |
| `scripts/run_batch.sh` | 批量实验脚本（服务器端） |
