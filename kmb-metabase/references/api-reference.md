# KMB API 参考文档

完整的 Metabase API 参考，包含只读和部分写操作。

---

## 基础信息

| 属性 | 值 |
|------|-----|
| Host | `https://kmb.qunhequnhe.com` |
| 认证方式 | Header `x-api-key` |
| Content-Type | `application/json` |

## 认证

```bash
x-api-key: mb_xxx...
```

---

## Collection API

### 获取 Collection 详情

```http
GET /api/collection/{id}
```

**响应示例:**
```json
{
  "id": 396,
  "name": "COOHOM折扣体系",
  "parent_id": 45,
  "location": "/70/23/45/",
  "entity_id": "YkcNmfcqespln9Cvp1bd5"
}
```

### 获取 Collection Items

```http
GET /api/collection/{id}/items
```

返回 Collection 中的所有内容（Cards、Dashboards、Datasets 等）

**响应示例:**
```json
{
  "total": 8,
  "data": [
    {"id": 254, "name": "COOHOM折扣体系", "model": "dashboard"},
    {"id": 3228, "name": "有意向用户->支付成功 转化数据", "model": "card"},
    {"id": 3267, "name": "有意向用户->支付成功 转化数据 - 分场景", "model": "card"}
  ]
}
```

---

## Card API

### 获取 Card 详情

```http
GET /api/card/{id}
```

返回完整的 Card 配置，包括 SQL、可视化设置等。

**响应示例:**
```json
{
  "id": 3267,
  "name": "有意向用户->支付成功 转化数据 - 分场景",
  "collection_id": 396,
  "database_id": 4,
  "query_type": "native",
  "display": "combo",
  "dataset_query": {
    "database": 4,
    "type": "native",
    "native": {
      "query": "SELECT ...",
      "template-tags": {}
    }
  },
  "visualization_settings": {...}
}
```

### 查询 Card 数据

```http
POST /api/card/{id}/query
Content-Type: application/json

{
  "parameters": [],
  "constraints": {
    "max-results": 10000
  }
}
```

**响应示例:**
```json
{
  "data": {
    "rows": [["2026-03-02", "新签", 9457, 517, 0.0547]],
    "cols": [
      {"name": "stat_date", "base_type": "type/Text"},
      {"name": "user_type", "base_type": "type/Text"}
    ]
  },
  "row_count": 194,
  "status": "completed"
}
```

### 创建 Card (写操作)

```http
POST /api/card
Content-Type: application/json

{
  "name": "新 Card 名称",
  "display": "table",
  "dataset_query": {
    "database": 4,
    "type": "native",
    "native": {
      "query": "SELECT * FROM table WHERE date = {{date}}"
    }
  },
  "collection_id": 396,
  "visualization_settings": {}
}
```

---

## Dashboard API

### 获取 Dashboard 详情

```http
GET /api/dashboard/{id}
```

**响应示例:**
```json
{
  "id": 254,
  "name": "COOHOM折扣体系",
  "collection_id": 396,
  "ordered_cards": [],
  "parameters": []
}
```

### 更新 Dashboard (含 dashcards)

```http
PUT /api/dashboard/{id}
Content-Type: application/json

{
  "width": "full",
  "parameters": [
    {
      "name": "日期范围",
      "slug": "date_range",
      "id": "param_date",
      "type": "date/range"
    }
  ],
  "dashcards": [
    {
      "id": 123,
      "card_id": 456,
      "dashboard_tab_id": 1,
      "row": 0,
      "col": 0,
      "size_x": 12,
      "size_y": 8,
      "parameter_mappings": [
        {
          "parameter_id": "param_date",
          "card_id": 456,
          "target": ["dimension", ["field", "created_date", {"base-type": "type/Date"}], {"stage-number": 0}]
        }
      ]
    }
  ]
}
```

**⚠️ parameter_mappings target 格式**:
```json
[
  "dimension",
  ["field", "field_name", {"base-type": "type/Date"}],
  {"stage-number": 0}
]
```

| 元素 | 说明 | 示例 |
|------|------|------|
| 第1个 | 类型标识 | `"dimension"` |
| 第2个 | field 定义 | `["field", "created_date", {"base-type": "type/Date"}]` |
| 第3个 | stage 信息 | `{"stage-number": 0}` |

### 获取 Dashboard 数据

```http
POST /api/dashboard/{id}/dashcard/{dashcard_id}/card/{card_id}/query
```

用于获取 Dashboard 中特定 Card 的数据。

---

## Database API

### 获取数据库列表

```http
GET /api/database
```

**响应示例:**
```json
{
  "data": [
    {"id": 4, "name": "Hive_prod", "engine": "hive-like"},
    {"id": 5, "name": "datacool-dim", "engine": "mysql"}
  ]
}
```

### 获取数据库详情

```http
GET /api/database/{id}
```

### 获取数据库 Schema

```http
GET /api/database/{id}/schemas
```

### 获取数据库表

```http
GET /api/database/{id}/tables
```

### 获取表字段

```http
GET /api/table/{id}/fields
```

---

## 搜索 API

### 搜索内容

```http
GET /api/search?q={keyword}
```

**示例:**
```bash
curl -H "x-api-key: $API_KEY" \
  "https://kmb.qunhequnhe.com/api/search?q=转化"
```

**返回:** Cards、Dashboards、Collections 等匹配结果

---

## 用户与权限 API

### 获取当前用户信息

```http
GET /api/user/current
```

### 获取权限组

```http
GET /api/permissions/group
```

---

## 错误码参考

| 状态码 | 错误 | 说明 |
|--------|------|------|
| 401 | Unauthorized | API Key 无效 |
| 403 | Forbidden | 无权限访问该资源 |
| 404 | Not Found | Card/Collection 不存在 |
| 422 | Unprocessable Entity | 请求参数错误 |

---

## 常用 curl 示例

### 获取 Card 配置
```bash
#!/bin/bash
API_KEY="mb_xxx..."
CARD_ID=3267

curl -sL \
  -H "x-api-key: $API_KEY" \
  "https://kmb.qunhequnhe.com/api/card/$CARD_ID" | jq '.'
```

### 查询 Card 数据
```bash
#!/bin/bash
API_KEY="mb_xxx..."
CARD_ID=3267

curl -sL \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -X POST "https://kmb.qunhequnhe.com/api/card/$CARD_ID/query" \
  -d '{"parameters":[],"constraints":{"max-results":100}}' | jq '.data.rows'
```

### 获取 Collection 所有 Cards
```bash
#!/bin/bash
API_KEY="mb_xxx..."
COLLECTION_ID=396

curl -sL \
  -H "x-api-key: $API_KEY" \
  "https://kmb.qunhequnhe.com/api/collection/$COLLECTION_ID/items" | \
  jq '.data | map(select(.model == "card") | {id: .id, name: .name})'
```

---

*最后更新: 2026-03-19 - 新增 Dashboard parameter_mappings 格式说明*
