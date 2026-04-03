# KMB Skill - API 标准

## 认证方式

**必须使用**: `X-API-Key` Header
```bash
-H "X-API-Key: mb_xxx..."
```

**不要使用**:
- ❌ `X-Metabase-Session` (session token)
- ❌ Cookie 认证
- ❌ Basic Auth

## 常用端点速查

| 操作 | 方法 | 端点 |
|------|------|------|
| 验证连接 | GET | `/api/user/current` |
| 列出仪表板 | GET | `/api/dashboard` |
| 获取仪表板 | GET | `/api/dashboard/:id` |
| 创建仪表板 | POST | `/api/dashboard` |
| 更新仪表板（添加卡片） | PUT | `/api/dashboard/:id` |
| 列出数据库 | GET | `/api/database` |
| 执行查询 | POST | `/api/dataset` |
| 列出问题 | GET | `/api/card` |
| 获取问题 | GET | `/api/card/:id` |
| 创建/更新问题 | POST/PUT | `/api/card` |
| 运行问题 | POST | `/api/card/:id/query` |
| 列出 Collections | GET | `/api/collection` |
| 更新 Collection | PUT | `/api/collection/:id` |
| 获取 Collection 内容 | GET | `/api/collection/:id/items` |

## Collection 层级结构 ⭐

**重要发现**: Collection 使用 `location` 字段而非 `parent_id` 表示层级关系。

| 字段 | 说明 |
|------|------|
| `parent_id` | 通常为 `null`，**不能用于查询父子关系** |
| `location` | 表示完整路径，格式为 `/父ID1/父ID2/父ID3/` |

### 示例
```json
// 父 Collection
{
  "id": 168,
  "name": "Coohom事件集合",
  "location": "/70/23/"
}

// 子 Collection
{
  "id": 170,
  "name": "a.主站",
  "location": "/70/23/168/"
}
```

### 查询子 Collections 的正确方法

```bash
# 方法 1: 查询直接子 Collections
parent_location="/70/23/168/"
curl -sL "${HOST}/api/collection" \
  -H "X-API-Key: ${API_KEY}" | \
  jq -r '.[] | select(.location == "/70/23/168/") | "\(.id)|\(.name)"'

# 方法 2: 查询所有子孙 Collections
parent_id=168
curl -sL "${HOST}/api/collection" \
  -H "X-API-Key: ${API_KEY}" | \
  jq -r ".[] | select(.location | test(\"/168/\")) | \"\(.id)|\(.name)|\(.location)\""
```

### 清理误建 Collections

KMB 当前**不暴露** `DELETE /api/collection/:id`。清理误建目录时，使用 `PUT /api/collection/:id` 把 Collection 送进 Trash：

```bash
curl -X PUT "${HOST}/api/collection/${collection_id}" \
  -H "X-API-Key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Collection 名称",
    "archived": true
  }'
```

关键要点：
- ✅ `archived: true` 会把 Collection 移到 Trash，而不是永久删除
- ✅ 归档误建树时优先归档根 Collection，子 Collection 会随之脱离活动目录
- ⚠️ `GET /api/collection` 的活动候选判断应忽略已归档树

## Dashboard 卡片管理 ⭐

**CRITICAL**: 必须使用 PUT 方法更新整个 Dashboard，不能用 POST。

### 正确做法
```bash
curl -X PUT "${HOST}/api/dashboard/${dashboard_id}" \
  -H "X-API-Key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "dashcards": [
      {
        "id": -1,
        "card_id": 2095,
        "row": 0,
        "col": 0,
        "size_x": 6,
        "size_y": 4
      },
      {
        "id": -2,
        "card_id": 2093,
        "row": 0,
        "col": 6,
        "size_x": 12,
        "size_y": 6
      }
    ]
  }'
```

### 关键要点
- ✅ 使用 `PUT /api/dashboard/:id`，不是 POST
- ✅ 新卡片使用 **负数 ID**（-1, -2, -3...），Metabase 会自动分配正式 ID
- ✅ 必须包含 `id`, `card_id`, `row`, `col`, `size_x`, `size_y`
- ✅ `dashcards` 数组包含**所有**要显示的卡片（包括已有的和新增的）

### 字段说明
| 字段 | 说明 |
|------|------|
| `id` | 卡片在仪表板中的 ID（新卡片用负数） |
| `card_id` | 查询/问题的 ID |
| `row` | 垂直位置（从 0 开始） |
| `col` | 水平位置（从 0 开始） |
| `size_x` | 宽度（1-18 或 1-24） |
| `size_y` | 高度（建议 4-8） |

### 布局建议
- 全宽: `size_x: 18` (或 24)
- 半宽: `size_x: 9` (或 12)
- 三分之一: `size_x: 6` (或 8)
- 常见高度：数字卡片 `size_y: 4`，图表 `size_y: 6-8`，表格 `size_y: 8-12`

## 创建查询的最佳实践 ⭐

**原则：默认必须 Model + MBQL；禁止把原生 SQL 作为常规回退。`UNION ALL` 先拆分为多个 MBQL Question，动态时间优先增量数据 + Dashboard 筛选，缺字段先在 Model 预加工。仅在完全无法解决且已记录原因时，才允许原生 SQL 例外。**

| 场景 | 推荐方式 |
|------|---------|
| 常规分析查询（Model 已具备字段） | Model + MBQL ✅ |
| 简单聚合（count/distinct/sum/case） | Model + MBQL ✅ |
| `UNION ALL` / 多段逻辑 | 拆分为多个 MBQL Question，并在 Dashboard 组合 ✅ |
| 动态时间需求 | 增量数据 + Dashboard 页面筛选（date 类型字段）✅ |
| Model 缺字段 | 先在 Model 预加工补齐字段，再做 MBQL ✅ |
| 复杂 JOIN / CTE / 窗口函数 | 先做 Model 分层拆解 + MBQL；仅在无法落地时进入例外评审 ⚠️ |
| 聚合指标命名 | `aggregation-options` 必须同时设置 `name` 与 `display-name` 且保持一致 ✅ |

### 原生 SQL 例外（最后手段）
仅当满足以下条件，才允许 `type: "native"`：
1. 已尝试 Model 预加工与 MBQL 拆分方案；
2. `UNION ALL` 已评估过“拆分多 Question + Dashboard 组合”不可行；
3. 动态时间已评估过“增量模型 + Dashboard 筛选”不可行；
4. 例外原因写入迁移记录（不可只写“复杂”）。

### MBQL 示例（简单聚合）
```json
{
  "name": "按天统计用户数",
  "dataset_query": {
    "type": "query",
    "database": 4,
    "query": {
      "source-table": 6080,
      "aggregation": [["distinct", ["field", "user_id", {"base-type": "type/BigInteger"}]]],
      "breakout": [["field", "ds_time", {"base-type": "type/Date"}]]
    }
  },
  "display": "line",
  "collection_id": 299
}
```

### 注意事项
- ⚠️ 优先把复杂计算下沉到 Model，Question 负责聚合与展示
- ⚠️ `UNION ALL` 先拆成多张 MBQL Question，不直接回退原生 SQL
- ⚠️ 动态时间优先使用 Dashboard 筛选器，不依赖 native `template-tags`
- ⚠️ 不要引用 `metabase.question_XXX` 格式
- ⚠️ `aggregation-options` 必须同时写 `name` 与 `display-name`（值保持一致）
- ⚠️ 仅在例外评审通过后使用原生 SQL

### 参数来源优先级（强约束）
- Dashboard 参数、默认值、筛选器映射的权威来源：**Tesseract MCP live 配置**。
- 仅当 MCP 不可用或 live 返回缺失时，才允许使用 `space-data` 离线 JSON 兜底。
- 使用离线兜底时，必须在迁移记录中写明：
  1) MCP 不可用/缺失的具体原因；
  2) 使用的离线文件与 pageId/graphId；
  3) 最终映射到 KMB 的默认值。

### 验证查询是否正确
创建查询后，**必须**验证：
```bash
# 测试查询是否能正常运行
curl -X POST "${HOST}/api/card/${card_id}/query" \
  -H "X-API-Key: ${API_KEY}" \
  -H "Content-Type: application/json"
```

如果返回错误包含 "Unknown database 'metabase'" → 说明使用了错误的表名语法，检查 SQL 语句中的表名是否正确。

同时必须检查响应中的 `status`：
- ✅ 仅 `status: "completed"` 视为通过
- ❌ `status: "failed"` 必须视为创建失败，即使响应里仍带有 `data`、`error`、`native_form` 或其他调试信息

## 响应展示

### 简洁摘要原则
只显示关键信息：
```
✓ 找到 5 个仪表板:
  - Sales Dashboard (ID: 12)
  - Marketing Analytics (ID: 15)
  - User Metrics (ID: 23)
```

不要显示完整 JSON 除非用户明确要求。

---

## Model 引用规范 ⭐

### 在 Question 中引用 Model

在 MBQL Question 中，统一通过 `source-table: "card__{model_id}"` 引用 Model：

```json
{
  "dataset_query": {
    "type": "query",
    "database": 4,
    "query": {
      "source-table": "card__6122",
      "breakout": [["field", "pay_success_time", {"base-type": "type/Date"}]],
      "aggregation": [["count"]]
    }
  }
}
```

**注意事项**:
- 默认不在 Question 层写原生 SQL；
- 复杂逻辑优先在 Model 预加工后再由 MBQL 消费；
- 仅在“原生 SQL 例外（最后手段）”条件满足时，才允许创建 native Question。

### 创建 Model 的完整参数

```json
{
  "type": "model",
  "name": "Model名称",
  "description": "描述",
  "collection_id": 123,
  "display": "table",
  "dataset_query": {
    "type": "native",
    "native": {
      "query": "SELECT ...",
      "template-tags": {}
    },
    "database": 4
  },
  "visualization_settings": {}
}
```

**关键字段**:
- `display`: 必需，Model 通常用 `"table"`
- `visualization_settings`: 必需，可为空对象 `{}`

---

## Collection 管理

### 创建子 Collection

```bash
curl -X POST "${HOST}/api/collection" \
  -H "X-API-Key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "子集合名称",
    "description": "描述",
    "parent_id": 485
  }'
```

**响应**:
```json
{
  "id": 490,
  "name": "子集合名称",
  "location": "/485/490/",
  "parent_id": null
}
```

**注意**: `parent_id` 在 API 中传，但响应中可能为 `null`，实际层级通过 `location` 判断
