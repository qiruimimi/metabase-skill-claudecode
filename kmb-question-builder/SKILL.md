---
name: kmb-question-builder
description: |
  Metabase MBQL Question 创建原子 skill。基于 Model 构建 breakout、aggregation、
  filter、order-by 与 expressions，返回 `question_id/card_id`。
origin: KMB-Skill
dependencies:
  - scripts/lib/kmb
---

# Question 构建 Skill

## When to Use

- 已有 `model_id`，需要创建展示层 Question。
- 迁移流程已完成建模，需要落地 MBQL。

## Required Inputs

- `model_id`
- `config_file` 或等价的结构化 Question 配置
- 可选: `collection_id`

## If Inputs Missing

- `model_id` 缺失时必须询问。
- 没有 Question 配置时，回退到 `kmb-sql-analyzer` 先产出方案。
- `collection_id` 未指定时，以配置中的值为准；若配置也没有，再询问。

## Execution Steps

1. 读取 Question 配置并检查 breakout、aggregation、filter、order-by。
2. 确保 aggregation 的 `name` 与原 SQL 指标名对齐。
3. 条件聚合使用 `CASE` 风格；复杂表达式仅在适合时放入 `expressions`。
4. 调用 `scripts/create_question.py` 创建 Question。
5. 记录返回的 `question_id/card_id`。
6. 将 `card_id` 作为下游交接物交给 `kmb-viz-config` 或 `kmb-dashboard-builder`。

## Outputs

- `question_id` 或 `card_id`
- 最终提交的 Question 配置摘要

## Failure Handling

- MBQL 配置不合法时，返回具体字段和结构错误。
- 需要 JOIN 但缺少稳定的关联方案时，暂停创建并回退分析阶段。

## Do Not

- 不在本 skill 中重新做 SQL 建模。
- 不把图表样式配置混入 Question 创建逻辑。

## Escalation / Hand-off

- 创建成功后交给 `kmb-viz-config` 或 `kmb-dashboard-builder`。
- 配置不完整时回退到 `kmb-sql-analyzer`。
