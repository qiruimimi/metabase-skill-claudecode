---
name: kmb-metabase
description: |
  KMB (Metabase) 数据平台根导航 skill。提供共享规范、参考资料入口、
  渐进加载规则和子 skill 路由，不负责直接承接完整业务执行。
---

# KMB (Metabase) 根导航 Skill

## When to Use

- 用户只表达泛化的 KMB 帮助需求，还未明确是查询、建模还是迁移。
- 需要确定应该进入哪个 `kmb-*` 子 skill。
- 需要查共享规范、API 标准、MBQL 最佳实践或离线数据入口。

## Required Inputs

- 用户当前目标，至少能判断属于查询、分析、创建资源或迁移中的一种。

## If Inputs Missing

- 先从用户原话判断最接近的任务类型，不要求先激活本 skill。
- 如果目标可以直接映射到子 skill，立即下钻到对应 skill，不停留在本根 skill 中展开长流程。
- 只有在任务仍然模糊时，才询问用户是要查询、分析还是迁移。

## Execution Steps

1. 判断用户任务属于哪一类：
   - 查小站页面、图表、SQL -> `kmb-space-query`
   - 分析 SQL、拆 Model/Question -> `kmb-sql-analyzer`
   - 创建 Collection -> `kmb-collection-builder`
   - 创建 Model -> `kmb-model-builder`
   - 创建 Question -> `kmb-question-builder`
   - 配置图表 -> `kmb-viz-config`
   - 创建 Dashboard -> `kmb-dashboard-builder`
   - 端到端迁移 -> `kmb-migration`
2. 仅提供当前任务所需的最小共享上下文。
3. 仅在必要时下钻共享资源：
   - API 细节 -> `agents/rules/` 或 `references/api-reference.md`
   - MBQL 细节 -> `references/mbql-best-practices.md`
   - Dashboard 参数映射 -> `references/dashboard-configs.md`
   - skill 交接契约 -> `references/skill-handoffs.md`
   - 小站离线映射 -> `space-data/`
4. 不要一次性加载全部 `references/`、`rules/`、`space-data/`。

## Outputs

- 选定的子 skill 名称。
- 必要时返回下一步应读取的共享资源路径。
- 不直接输出迁移资产、Model、Question 或 Dashboard 结果。

## Failure Handling

- 如果用户目标跨多个子 skill，优先路由到 `kmb-migration` 或最上游的原子 skill。
- 如果共享文档之间冲突，按 SSOT 顺序处理：`agents/rules/*` > 当前子 skill `SKILL.md` > `references/*`。
- 如果任务无法归类，先归入最上游可验证的 skill，再由该 skill 决定是否升级到 workflow。

## Do Not

- 不直接替代子 skill 执行完整流程。
- 不要求子 skill 先“激活 kmb-metabase”才可工作。
- 不在这里复制所有 API、MBQL、迁移细节。
- 多步链路优先遵循 `references/skill-handoffs.md`，不要临场猜测切换顺序。

## Escalation / Hand-off

- 需要实际执行任务时，立即 hand off 到对应子 skill。
- 需要端到端交付时，交给 `kmb-migration`，不要在根 skill 自行编排。
