---
name: kmb-migration
description: |
  小站(Space)到KMB的 workflow skill。固定编排 SQL 获取、分析建模、
  Collection/Model/Question/Viz/Dashboard 创建与交付验收。
origin: KMB-Skill
dependencies:
  - kmb-space-query
  - kmb-collection-builder
  - kmb-sql-analyzer
  - kmb-model-builder
  - kmb-question-builder
  - kmb-viz-config
  - kmb-dashboard-builder
---

# 小站 -> KMB 迁移 Workflow

## When to Use

- 用户要求“迁移小站页面到 KMB”。
- 用户同时给出 `page_id` 与目标 collection 或创建目标目录的要求。
- 任务需要端到端产出 Model、Question、Visualization、Dashboard 与验收结果。

## Required Inputs

- `page_id`
- 目标落点二选一：
  - `target_collection_id`
  - `create_collection_strategy`，即是否创建新 Collection 及其父级位置
- 是否保留原页面卡片结构；默认保留原卡片顺序与主要图表类型

## If Inputs Missing

- 缺 `page_id` 时必须询问，不可默认。
- 缺目标 Collection 信息时必须询问，不可直接创建到根目录。
- “是否保留原页面卡片结构”未说明时，默认保留原卡片数量、顺序和主要图表类型。
- 若用户只说“迁移 page 到 KMB”但未给细节，最少只追问 `page_id` 与目标 Collection 策略。

## Execution Steps

1. 边界确认
   - 记录 `page_id`、目标 Collection 策略、是否保留原页面结构。
   - 创建迁移工作目录，用于保存 SQL、`migration_plan.json`、问题配置和资产映射。
2. 上游获取: `kmb-space-query`
   - 读取页面结构，列出 page 下 graph 列表与图表类型。
   - 为每个待迁移 graph 提取原始 SQL。
   - 输出 `source_page.json`、`graph_inventory.json`、`raw_sql/<graph_id>.sql`。
3. Collection 准备: `kmb-collection-builder` 可选
   - 如果用户直接给了 `target_collection_id`，跳过创建。
   - 如果要求新建 Collection，按 `【P<page_id>】<页面名>` 命名，并记录 `collection_id`。
   - 输出 `target_collection.json`。
4. 核心分析: `kmb-sql-analyzer`
   - 对每个 SQL 生成可审阅的建模方案。
   - 必须确认 Model 粒度、I/S 表处理、breakout、aggregation 命名、条件聚合方式。
   - 输出 `migration_plan.json`；复杂页面可拆成 `plans/<graph_id>.json`。
5. 下游执行
   - `kmb-model-builder`: 创建 Model，输出 `model_id`。
   - `kmb-question-builder`: 按计划创建 Question，输出 `question_id/card_id`。
   - `kmb-viz-config`: 回写可视化配置，输出每张卡片的 viz 更新结果。
   - `kmb-dashboard-builder`: 创建 Dashboard、布局 dashcards、配置参数映射，输出 `dashboard_id`。

### 统一交接契约

按 `references/skill-handoffs.md` 执行交接，不要跳步：

- `kmb-space-query` -> 原始 SQL
- `kmb-sql-analyzer` -> `migration_plan.json`
- `kmb-model-builder` -> `model_id`
- `kmb-question-builder` -> `question_id/card_id`
- `kmb-viz-config` -> 更新后的 `card_id`
- `kmb-dashboard-builder` -> `dashboard_id`
6. 交付映射
   - 汇总 `asset_mapping.json`，至少包含 `page_id`、`graph_id`、`model_id`、`question_id/card_id`、`dashboard_id`。
   - 生成迁移记录，记录硬闸门结果、异常点、回滚信息。
7. 验收硬闸门
   - 检查 card 引用源是否为 `card__xxx` 而非小站表名。
   - 调用 `/api/card/<id>/query` 验证所有卡片可运行。
   - 抽样 3 至 5 个维度组合做数据一致性比对。
   - 检查 Dashboard 卡片数量、顺序、参数筛选器与主要图表类型。

## Outputs

- `raw_sql/<graph_id>.sql`
- `migration_plan.json` 或 `plans/<graph_id>.json`
- `target_collection.json`
- `asset_mapping.json`
- `migration_record.md` 或等价迁移记录
- KMB 侧资源 ID: `collection_id`, `model_id`, `question_id/card_id`, `dashboard_id`

## Failure Handling

- SQL 无法稳定拆成 Model 与 Question 时，停止自动迁移，回退到人工确认。
- 图表类型无法映射到 KMB 可视化配置时，停止该图表迁移并标记阻塞原因。
- 参数映射无法自动还原时，不要猜测配置，回退到人工确认。
- 数据一致性抽样失败时，整单迁移不可交付，必须保留差异说明并回滚或暂停。
- API 权限、网络、Collection 权限错误时，先记录失败阶段与输入，再中止后续创建动作。

## Do Not

- 不跳过 `kmb-sql-analyzer` 直接建 Model 或 Question。
- 不在 workflow 中手写新的重型 SDK。
- 不把复杂业务编排塞回原子 skill。
- 不在硬闸门失败时继续宣称迁移完成。

## Escalation / Hand-off

- 单个 graph 的 SQL 过于复杂时，可拆为人工复核子任务后继续。
- 发现目录策略、图表保留策略或数据一致性要求变化时，重新确认边界再继续。
