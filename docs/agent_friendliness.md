# Agent 友好性评估：HeteroPlace3D

## 友好 ✅

| 点 | 说明 |
|----|------|
| sidecar partition 文件 | cell → tier 映射独立输出，Agent 无需解析 DEF |
| 分钟级延迟 | gcd 66s，ariane133 4.7min |
| 确定性输出 | 同 seed 同结果 |
| `partition_input` 接口存在 | 已预留 |

## 不友好 ❌

### 致命

| 问题 | 说明 |
|------|------|
| **无结构化输出** | HPWL/Die 分布埋在 log 文本中 |
| **partition 是软约束** | `partition_input` 仅作热启动，2.5D 覆盖 |
| **无增量模式** | 改一个 tier 也要全量重跑 |
| **面积效应无法回避** | 2D(面积A): 3.30M, 3D(面积2A): 5.53M — 168%，Agent 不能拿绝对 HPWL 当信号 |

### 严重

| 问题 | 说明 |
|------|------|
| 纯 2D baseline 工具链极脆弱 | 需 OpenROAD + 手动 tracks + 正确 layer 名，8+ 次尝试才成功 |
| HBT 不在输出中 | log 有，DEF 无 |
| 输出/输入不可 diff | `partition_input` vs 产出无对照 |

### 一般

| 问题 | 说明 |
|------|------|
| 错误处理是 segfault | 非法参数 crash 无错误原因 |
| 路径全相对 | 依赖 symlink |

> 实测基准: gcd, 2D=OpenROAD RePlAce, 3D=heteroplace3d, HPWL 同算法(Verilog+DEF)
