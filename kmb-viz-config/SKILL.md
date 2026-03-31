---
name: kmb-viz-config
description: |
  Metabase 图表可视化原子 skill。负责设置 display、series_settings、
  column_settings 与表格/双轴/百分比格式。
origin: KMB-Skill
dependencies:
  - scripts/lib/kmb
---

# 可视化配置 Skill

## When to Use

- 已有 Question/Card，需要配置图表展示方式。
- 迁移流程需要把小站图表类型映射到 KMB。

## Required Inputs

- `card_id`
- `config_file` 或等价 viz 配置
- 可选: 原图类型信息，如 `LineSimple`, `PieSimple`, `MixLineBar`

## If Inputs Missing

- `card_id` 缺失时必须询问。
- viz 配置缺失时，至少根据原图类型生成最小配置；若原图类型也缺失，则询问或等待上游提供。
- 未指定图表类型时，不自行猜复杂双轴逻辑。

## Execution Steps

1. 判断原图类型与目标 `display`。
2. 配置 `graph.dimensions`、`graph.metrics`、`series_settings`、`column_settings`。
3. 对百分比、双轴、表格固定列等特殊格式做显式设置。
4. 调用 `scripts/update_viz.py` 更新卡片可视化配置。

## Outputs

- 已更新的 `card_id`
- 生效的可视化配置摘要

## Failure Handling

- 图表类型无法映射到 KMB 时，停止自动配置并标明不支持点。
- 缺少关键 metric/dimension 时，不生成猜测性的配置。

## Do Not

- 不创建 Question。
- 不在这里决定 Dashboard 布局。

## Escalation / Hand-off

- 单卡片配置完成后交给 `kmb-dashboard-builder`。
- 原图配置过于复杂且无稳定映射时，升级人工复核。
