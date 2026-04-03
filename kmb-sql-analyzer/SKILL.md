---
name: kmb-sql-analyzer
description: |
  SQL分析与数据建模原子 skill。解析 SQL 结构，设计 Model 与 Question，
  输出 `migration_plan.json`，是迁移流程的核心枢纽和必经步骤。
origin: KMB-Skill
dependencies: []
---

# SQL 分析与数据建模 Skill

## When to Use

- 已拿到原始 SQL，需要拆成 Model 与 Question。
- 用户要分析 SQL、生成 MBQL、判断 I 表/S 表策略。
- 任意迁移任务进入资源创建之前。

## Required Inputs

- `sql_file` 或 `sql` 二选一
- 可选: `database`
- 可选: 输出路径；默认 `migration_plan.json`

## If Inputs Missing

- `sql_file` 与 `sql` 都缺失时必须询问或等待上游提供，不能凭描述猜 SQL。
- `database` 未提供时可使用默认数据库配置。
- 输出路径未提供时，默认写为 `migration_plan.json`。

## Execution Steps

1. 解析 SQL，识别：
   - 源表
   - 维度字段与聚合字段
   - `GROUP BY`
   - `WHERE`
   - `ORDER BY`
   - JOIN 复杂度
2. 设计 Model 层：
   - 移除聚合，保留原始粒度
   - 预计算日期、CASE 分类、排序字段与必要标记字段
   - 处理 I 表/S 表规则：I 表不限制 `ds`，S 表固定 T+1
3. 设计 Question 层：
   - breakout 对齐原 SQL 的 `GROUP BY`
   - aggregation 名称对齐原 SQL 列名
   - 条件聚合使用 `CASE` 风格，不把复杂业务逻辑塞回 Dashboard
4. 输出 `migration_plan.json`，至少包含：
   - `analysis`
   - `model`
   - `questions`
   - `visualization`
5. 对复杂 SQL 标记决策点，供下游或人工复核。

### 下游交接要求

- `model` 产物必须可直接交给 `kmb-model-builder`
- `questions[*]` 产物必须可直接交给 `kmb-question-builder`
- `visualization` 产物必须可直接交给 `kmb-viz-config`
- 统一交接格式参考 `references/skill-handoffs.md`

## Outputs

- `migration_plan.json`
- 必要时输出 `model.sql`
- 分析摘要，至少说明表类型、粒度、推荐建模方案与风险点

## Failure Handling

- SQL 无法解析时，返回失败原因与未解析片段，不生成伪计划。
- JOIN 或子查询复杂度过高且无法稳定映射时，标记需要人工确认。
- 若聚合无法安全还原为 Model 粒度，停止自动方案输出。

## Do Not

- 不直接创建 Model、Question 或 Dashboard。
- 不跳过 I 表/S 表判断。
- 不把 Dashboard 参数逻辑误下沉为 Model 固定过滤条件。

## Escalation / Hand-off

- 分析完成后交给 `kmb-model-builder` 与 `kmb-question-builder`。
- 遇到复杂 JOIN、窗口函数或条件聚合无法定案时，升级为人工复核。
