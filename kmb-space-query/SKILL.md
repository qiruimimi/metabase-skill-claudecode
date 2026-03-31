---
name: kmb-space-query
description: |
  小站(Space)数据查询原子 skill。用于搜索页面、查看 page/graph 详情、
  提取 SQL 与浏览目录树，是迁移流程的上游数据获取模块。
origin: KMB-Skill
dependencies: []
---

# 小站数据查询 Skill

## When to Use

- 用户要搜索小站页面、查看 page 详情、查看 graph 配置或提取 SQL。
- 迁移流程需要先获取源页面结构与原始 SQL。

## Required Inputs

以下输入满足任一即可：

- `keyword`，用于 `search`
- `page_id`，用于 `page`
- `graph_id`，用于 `graph` 或 `sql`
- `tree` 查询意图，表示浏览目录树

## If Inputs Missing

- 如果用户明确给了 `page_id`，直接执行 `page`，不再追问。
- 如果用户明确给了 `graph_id`，根据意图执行 `graph` 或 `sql`，不再追问。
- 如果只有模糊关键词，默认先执行 `search`。
- 如果连关键词、`page_id`、`graph_id` 都没有，才询问用户要搜索什么。

## Execution Steps

1. 根据输入选择命令：
   - `search <keyword>`
   - `page <page_id>`
   - `graph <graph_id>`
   - `sql <graph_id>`
   - `tree`
2. 使用 `scripts/space_sql_mapper.py` 获取结果。
3. 返回时必须保留关键标识：
   - 页面查询返回 `page_id`、页面名、graph 列表
   - graph 查询返回 `graph_id`、graph 名称、graphType
   - SQL 查询返回完整 SQL，不能截断 `WHERE` 或参数逻辑
4. 若服务于迁移流程，同时产出可交接的数据文件或结构化结果。

## Outputs

- `search`: 候选页面列表，至少包含 `page_id` 与名称
- `page`: 页面详情与 graph 列表
- `graph`: 图表详情与类型
- `sql`: 可复用的完整 SQL 文本
- `tree`: 目录树结构

## Failure Handling

- `page_id` 或 `graph_id` 不存在时，返回明确的未命中结果，不猜测替代对象。
- SQL 提取为空或不完整时，标记失败，不把残缺 SQL 交给下游。
- 搜索结果过多时，返回最相关候选并建议用户缩小范围。

## Do Not

- 不在本 skill 中设计 Model、Question 或 Dashboard。
- 不把模糊搜索结果当作确定 page_id 自动继续迁移。
- 不省略 graph 名称、graphType 或 SQL 条件。

## Escalation / Hand-off

- 需要建模时，交给 `kmb-sql-analyzer`。
- 需要完整迁移时，交给 `kmb-migration`。
