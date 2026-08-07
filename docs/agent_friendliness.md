# Agent 友好性评估：HeteroPlace3D

> 从 Agent 开发者的视角，评估 heteroplace3d v20260807 作为内环引擎的可用性。

## 友好 ✅

| 点 | 说明 |
|----|------|
| sidecar partition 文件 | cell → tier 映射以独立文本文件输出，Agent 无需解析 DEF |
| 分钟级延迟 | gcd 66s，ariane133 4.7min，在内环可接受范围 |
| 确定性输出 | 同 seed 同结果，Agent 可复现验证 |
| `partition_input` 接口存在 | 虽然目前是软约束，但接口已预留 |

## 不友好 ❌

### 致命

| 问题 | 说明 | 对 Agent 的影响 |
|------|------|----------------|
| **无结构化输出** | HPWL / Die 分布 / HBT 数全部埋在 log 文本中 | Agent 每次读取都要 grep + 正则，脆弱 |
| **partition 是软约束** | `partition_input` 仅作热启动，2.5D 阶段会覆盖 | Agent 改 tier 不保证生效，无法试"如果这 200 个单元换层会怎样" |
| **无增量模式** | 每次只能全量重跑 | 改一个单元 tier 也要 66s，百轮探索 = 小时级，内环死掉 |

### 严重

| 问题 | 说明 | 对 Agent 的影响 |
|------|------|----------------|
| **纯 2D baseline 不可用** | 四种方式均失败（segfault / 格式不支持） | Agent 没法判断 3D 相对 2D 的 ΔPPA |
| **HBT 不在输出中** | log 显示 236 个，DEF 中无实体 | Agent 看不到跨层连接的实际布局 |
| **输出与输入不可 diff** | `partition_input` 和 `partition_output` 无对照 | Agent 没法知道"我的意图 vs placer 实际执行"的差异 |
| **目标密度 area 不对等** | 3D=2A vs 2D=A，HPWL 天然低 | Agent 不能把 HPWL 下降归因于折叠收益 |

### 一般

| 问题 | 说明 | 对 Agent 的影响 |
|------|------|----------------|
| **错误处理是 segfault/crash** | 非法参数导致 crash 而非报错 | Agent 拿到的是进程退出码，不是错误原因 |
| **路径全相对** | 依赖 symlink + 固定目录结构 | 换一个工作目录就崩，部署耦合 |
| **dreamplace 不支持 DEF** | 仅支持 Bookshelf `.aux` 格式 | 切换 2D 模式需要格式转换 |

## 建议优先级

| 优先级 | 需求 | 理由 |
|--------|------|------|
| P0 | 结构化摘要输出（JSON 或 key-value） | Agent 闭环的最基本前提 |
| P0 | `partition_input` 硬约束模式 | Agent 能控制层指派 = 能产生变异 |
| P1 | 增量模式（改 tier 不重跑全局） | 内环从小时级压到秒级的关键 |
| P1 | 纯 2D 模式 | 没有 baseline 就没有 ΔPPA |
| P2 | HBT 写入 DEF | 跨层连接可追溯 |
| P2 | 输出 vs 输入 diff | Agent 可审计 placer 行为 |

---

> 实验基础：gcd, NanGate45 F2F, heteroplace3d v20260807
