# KMB Skill Handoffs

这份文件定义各个 KMB skill 之间的交接契约，避免依赖记忆。

## 主链路

`kmb-space-query` -> `kmb-sql-analyzer` -> `kmb-model-builder` -> `kmb-question-builder` -> `kmb-viz-config` -> `kmb-dashboard-builder`

可选前置：

`kmb-collection-builder`

统一编排：

`kmb-migration`

## 交接契约

### `kmb-space-query`

- 产物：`page_id`、`graph_id`、页面元信息、原始 SQL
- 下游：
  - 分析 SQL 时交给 `kmb-sql-analyzer`
  - 端到端任务交给 `kmb-migration`

### `kmb-sql-analyzer`

- 输入：来自 `kmb-space-query` 或用户直接提供的 SQL
- 产物：
  - `migration_plan.json`
  - `model.sql` 或等价 Model SQL
  - `questions[]` 配置
  - `visualization` 配置
- 下游：
  - 把 `migration_plan.json.model.sql` 交给 `kmb-model-builder`
  - 把 `migration_plan.json.questions[*]` 交给 `kmb-question-builder`
  - 若保持 workflow 集中编排，则交回 `kmb-migration`

### `kmb-model-builder`

- 输入：
  - `collection_id`
  - `model.sql` 或 `migration_plan.json`
- 产物：
  - `model_id`
- 下游：
  - 把 `model_id` 交给 `kmb-question-builder`

### `kmb-question-builder`

- 输入：
  - `model_id`
  - 单张 question 配置
  - `collection_id`
- 产物：
  - `question_id/card_id`
- 下游：
  - 把 `card_id` 交给 `kmb-viz-config`
  - 或在无需样式改动时直接交给 `kmb-dashboard-builder`

### `kmb-viz-config`

- 输入：
  - `card_id`
  - visualization 配置
- 产物：
  - 更新后的 `card_id`
- 下游：
  - 交给 `kmb-dashboard-builder`

### `kmb-dashboard-builder`

- 输入：
  - `collection_id`
  - dashboard 名称
  - 有序 `card_id` 列表与布局配置
- 产物：
  - `dashboard_id`

### `kmb-collection-builder`

- 产物：
  - `collection_id`
- 下游：
  - `kmb-model-builder`
  - `kmb-dashboard-builder`
  - `kmb-migration`

### `kmb-migration`

- 负责完整链路
- 必须维护映射：
  - `page_id -> graph_id -> sql -> model_id -> card_id -> dashboard_id`

## 强约束

- 不能从 `kmb-space-query` 直接跳到 `kmb-model-builder`
- 没有 `model_id` 时不能创建 Question
- 没有 `card_id` 时不能配置 visualization
- Dashboard 组装前必须明确卡片顺序和布局
- `_s_d` 表的 `ds_time` 与 `T+1 ds` 约束由 `kmb-model-builder` 做硬校验
