---
name: kmb-dashboard-builder
description: |
  Metabase Dashboard 原子 skill。负责创建 Dashboard、添加 dashcards、
  配置布局和 parameter mappings，并返回 `dashboard_id`。
origin: KMB-Skill
dependencies:
  - scripts/lib/kmb
---

# Dashboard 构建 Skill

## When to Use

- 已有一组 Question/Card，需要组装成 Dashboard。
- 迁移流程已完成 Question 与可视化配置，准备交付页面。

## Required Inputs

- `name`
- `collection_id`
- `cards_config` 或等价布局配置，内含 `card_id`, `row`, `col`, `size_x`, `size_y`
- 可选: Dashboard 级参数配置

## If Inputs Missing

- `name` 与 `collection_id` 缺失时必须询问。
- 没有布局配置时，可默认按原页面卡片顺序做顺序排布；若属于迁移场景，优先由 workflow 提供。
- 参数映射不明确时，不自行猜测复杂 `parameter_mappings`。

## Execution Steps

1. 调用 `scripts/create_dashboard.py` 创建 Dashboard，获取 `dashboard_id`。
2. 组装 `cards_config`，新卡片使用负数临时 ID。
3. 调用 `scripts/add_cards.py` 或等价 API 更新 dashcards。
4. 如有筛选器，配置 Dashboard 参数与 `parameter_mappings`。
5. 校验卡片数量、布局与必要筛选器是否完整。
6. 输入的 `card_id` 应来自 `kmb-question-builder`，若做过样式更新则优先使用 `kmb-viz-config` 输出的版本。

## Outputs

- `dashboard_id`
- Dashcards 布局结果
- 参数映射配置摘要

## Failure Handling

- 布局配置缺字段时，返回具体缺失项。
- `parameter_mappings` 结构不合法时，停止提交并返回错误位置。
- 添加卡片失败时，不继续宣称 Dashboard 组装完成。

## Do Not

- 不创建 Question。
- 不在这里重写图表可视化逻辑。
- 不使用不存在的 `/api/dashboard/:id/cards` 端点。

## Escalation / Hand-off

- 完成后将 `dashboard_id` 交回 workflow 或调用方。
- 参数映射无法自动恢复时，升级人工确认。
