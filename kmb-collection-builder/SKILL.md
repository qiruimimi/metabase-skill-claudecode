---
name: kmb-collection-builder
description: |
  Metabase Collection 原子 skill。提供 Collection 创建、更新、查询与资源列举，
  不承担目录映射等业务编排。
origin: KMB-Skill
dependencies: []
---

# Collection 构建 Skill

## When to Use

- 用户要求创建或更新 Collection。
- 迁移流程需要准备目标 Collection。

## Required Inputs

- 创建时: `name`
- 可选: `parent_id`, `description`
- 更新时: `collection_id`

## If Inputs Missing

- 创建缺 `name` 时必须询问。
- `parent_id` 缺失时默认创建到根目录，但迁移场景下应优先由 workflow 决定，不在本 skill 内自行猜层级。
- 更新缺 `collection_id` 时必须询问。

## Execution Steps

1. 判断是创建、更新、查询详情还是列举资源。
2. 创建时优先使用脚本 `scripts/create_collection.py`；必要时直接调用 API。
3. 迁移场景命名优先采用 `【P<pageId>】<页面名>`。
4. 已存在场景使用 `--skip-if-exists` 或 `--update-if-exists` 实现幂等。

## Outputs

- `collection_id`
- Collection 详情 JSON
- 资源列表

## Failure Handling

- 名称冲突时，优先使用幂等参数，不重复创建。
- 权限不足时返回失败原因，不尝试绕过 parent 权限。

## Do Not

- 不处理小站目录树到 Collection 层级的业务映射。
- 不批量创建多级结构而不返回中间 ID。

## Escalation / Hand-off

- 需要根据页面结构决定 Collection 策略时，交给 `kmb-migration`。
