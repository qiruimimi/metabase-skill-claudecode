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

**原则：统一使用原生 SQL (type: "native")**

| 场景 | 推荐方式 |
|------|---------|
| 分区字段查询（如 ds） | 原生 SQL ✅ |
| 动态时间表达式 | 原生 SQL ✅ |
| 跨表 JOIN | 原生 SQL ✅ |
| CTE / 窗口函数 | 原生 SQL ✅ |
| 复杂逻辑 | 原生 SQL ✅ |

### 示例
```json
{
  "name": "查询名称",
  "dataset_query": {
    "type": "native",
    "database": 4,
    "native": {
      "query": "SELECT user_id, COUNT(*) as cnt FROM table_name WHERE ds = DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 1 DAY), '%Y%m%d') GROUP BY user_id"
    }
  },
  "display": "table",
  "collection_id": 299
}
```

### 注意事项
- ⚠️ 直接使用实际数据库表名
- ⚠️ 不要引用 `metabase.question_XXX` 格式
- ⚠️ 确保 SQL 语法与目标数据库兼容

### 验证查询是否正确
创建查询后，**必须**验证：
```bash
# 测试查询是否能正常运行
curl -X POST "${HOST}/api/card/${card_id}/query" \
  -H "X-API-Key: ${API_KEY}" \
  -H "Content-Type: application/json"
```

如果返回错误包含 "Unknown database 'metabase'" → 说明使用了错误的表名语法，检查 SQL 语句中的表名是否正确。

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

当在原生 SQL Question 中引用 Model 时，**必须使用子查询方式**:

```sql
-- ✅ 正确：使用子查询引用 Model
SELECT 
    pay_success_day,
    COUNT(DISTINCT user_id)
FROM (SELECT * FROM {{#model_id}}) AS model_data
GROUP BY pay_success_day
```

**注意事项**:
- `{{#model_id}}` 语法在原生 SQL 中无法直接解析
- 必须通过子查询包装 `(SELECT * FROM {{#model_id}}) AS alias`
- Model ID 是创建后返回的整数 ID

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
