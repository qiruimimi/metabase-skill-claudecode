---
name: kmb-metabase
description: |
  KMB (Metabase) 数据平台操作指南与自动化工具集。用于：
  (1) 查询和分析 Metabase Card/Dashboard 数据
  (2) 自动化日报/周报生成与播报
  (3) 数据探索与指标监控
  (4) API 调用与数据处理
  (5) 创建和管理 Metabase 资源
  适用于需要对 KMB 系统进行数据查询、报告生成或自动化操作的任务。
---

# KMB (Metabase) 数据平台 Skill

企业内部 Metabase 数据平台（KMB）的数据迁移与重构工具集。

> **定位**: 面向开发/数据工程师，专注于**小站数据迁移**和**Metabase 资源重构**（Model/Question/Dashboard）。
>
> **Iron Law（铁律）**: 只使用 curl 调用 API，禁止创建 SDK、库或复杂客户端。保持简洁、验证、交互三大原则。

## 与其他 Metabase Skill 的区别

| 维度 | 本 Skill | 通用 Metabase Skill |
|------|---------|-------------------|
| **目标用户** | 开发/数据工程师 | 业务分析人员 |
| **核心任务** | 数据迁移、资源重构、自动化 | 即席查询、数据探查 |
| **工作方式** | 脚本化、批量化、自动化 | 交互式、单点查询 |
| **SQL 策略** | 重构 SQL，创建可复用 Model | 直接查询，关注结果 |
| **输出成果** | Dashboard、Model、Question | 查询结果、数据报告 |

## 快速访问

| 资源 | 链接/位置 |
|------|----------|
| KMB 平台 | `https://kmb.qunhequnhe.com` |
| API 文档 | `references/api-reference.md` |
| **MBQL 最佳实践** | `references/mbql-best-practices.md` |
| Dashboard 配置 | `references/dashboard-configs.md` |
| **迁移指南 (完整版)** | `references/migration-guide.md` |
| **小站数据** | `space-data/` 目录 |
| 常用脚本 | `scripts/` 目录 |

## 核心配置

### API 认证
```bash
API_HOST="https://kmb.qunhequnhe.com"
API_KEY="mb_h5ddq58TgNTAZsV7e81myvAxMlMcqXWrx1y9TdqArl8="
```

### 常用 Dashboard
| Dashboard | ID | 用途 |
|-----------|-----|------|
| 投放词数据总览 | 139 | GA投放词分析 |
| COOHOM折扣体系 | 254 | 折扣转化分析 |
| Revenue用户分层（新）迁移 | 494 | 收入账单分层分析 |

---

## 使用场景

### 场景1: 查询 Card 数据

```bash
# 使用内置脚本查询 Card 数据
python3 ~/.claude/skills/kmb-metabase/scripts/query_card.py 3267

# 或使用 curl
curl -sL \
  -H "x-api-key: mb_h5ddq58TgNTAZsV7e81myvAxMlMcqXWrx1y9TdqArl8=" \
  -H "Content-Type: application/json" \
  -X POST "https://kmb.qunhequnhe.com/api/card/3267/query" \
  -d '{"parameters":[],"constraints":{"max-results":100}}'
```

### 场景2: Dashboard 操作 ⭐

#### 创建 Dashboard
```bash
curl -X POST "https://kmb.qunhequnhe.com/api/dashboard" \
  -H "X-API-Key: mb_xxx..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Dashboard",
    "description": "Dashboard description",
    "collection_id": 5,
    "parameters": []
  }'
```

#### 向 Dashboard 添加卡片
```bash
curl -X POST "https://kmb.qunhequnhe.com/api/dashboard/${dashboard_id}/cards" \
  -H "X-API-Key: mb_xxx..." \
  -H "Content-Type: application/json" \
  -d '{
    "cardId": 45,
    "row": 0,
    "col": 0,
    "sizeX": 6,
    "sizeY": 4,
    "parameter_mappings": [],
    "visualization_settings": {}
  }'
```

#### 批量更新 Dashboard 卡片（推荐）
```bash
curl -X PUT "https://kmb.qunhequnhe.com/api/dashboard/${dashboard_id}/cards" \
  -H "X-API-Key: mb_xxx..." \
  -H "Content-Type: application/json" \
  -d '{
    "cards": [
      {
        "id": -1,
        "card_id": 45,
        "row": 0,
        "col": 0,
        "sizeX": 6,
        "sizeY": 4
      },
      {
        "id": -2,
        "card_id": 46,
        "row": 0,
        "col": 6,
        "sizeX": 12,
        "sizeY": 6
      }
    ]
  }'
```

#### 从 Dashboard 删除卡片
```bash
curl -X DELETE "https://kmb.qunhequnhe.com/api/dashboard/${dashboard_id}/cards/${dashcard_id}" \
  -H "X-API-Key: mb_xxx..."
```

#### 复制 Dashboard
```bash
curl -X POST "https://kmb.qunhequnhe.com/api/dashboard/${dashboard_id}/copy" \
  -H "X-API-Key: mb_xxx..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Copy of Dashboard",
    "description": "Copied dashboard",
    "collection_id": 5
  }'
```

### 场景3: 小站数据查询（离线分析）

使用 `space_sql_mapper.py` 分析小站导出的数据（目录树 → 页面 → SQL）：

```bash
cd ~/.claude/skills/kmb-metabase/scripts

# 1. 按关键词搜索页面
python3 space_sql_mapper.py search "Weekly Data"
# → pageId=34433

# 2. 查看页面详情（含图表列表）
python3 space_sql_mapper.py page 34433
# → 包含10个图表，如 graphId=41236

# 3. 查看图表 SQL 详情
python3 space_sql_mapper.py graph 41236

# 4. 只提取 SQL（可用于迁移到 KMB）
python3 space_sql_mapper.py sql 41236

# 5. 显示完整目录树
python3 space_sql_mapper.py tree
```

**数据规模**: 412个页面，1,738个图表/SQL查询

### 场景4: 生成日报/周报

```bash
# 执行 Dashboard 139 日报并写入报告文件
python3 ~/.claude/skills/kmb-metabase/scripts/generate_dashboard139_report.py \
  --output ~/.claude/skills/kmb-metabase/reports/dashboard139_$(date +%Y%m%d).md

# 查看生成的报告
cat ~/.claude/skills/kmb-metabase/reports/dashboard139_$(date +%Y%m%d).md
```

### 场景5: 小站 → KMB 数据迁移

> ⚠️ **这是一个复杂任务，需要 LLM 自主思考分阶段执行**

小站（Space）到 KMB 的迁移**不是简单脚本可以完成**的，涉及：
- SQL 语义理解 → MBQL 转换
- Model 分层设计（Table / SQL / Model）
- Metrics 业务抽象
- 可视化重建

**详细迁移指南**: `references/migration-guide.md`

**迁移流程**:
```bash
# 阶段 1: 提取并分析源 SQL
python3 scripts/space_sql_mapper.py graph <graphId>
# → LLM 分析 SQL 结构，确定迁移策略

# 阶段 2: 创建 Model（如需要）
# → 基于分析结果设计 Model SQL
# → POST /api/dataset

# 阶段 3: 创建 Metrics（如需要）
# → 识别可复用指标
# → POST /api/metric

# 阶段 4: 创建 MBQL Question
# → SQL → MBQL 转换
# → POST /api/card
```

**关键决策点**（LLM 需自主判断）:
1. 这个查询应该直接建 Question，还是新建 Model？
2. 哪些计算应该抽象为 Metrics？
3. SQL 中的聚合如何准确转换为 MBQL？

---

### 场景6: 探索数据

```bash
# 搜索相关内容
curl -sL \
  -H "x-api-key: mb_h5ddq58TgNTAZsV7e81myvAxMlMcqXWrx1y9TdqArl8=" \
  "https://kmb.qunhequnhe.com/api/search?q=转化" | jq '.data'
```

---

## MBQL 最佳实践

创建或编辑 Question 时，参考以下最佳实践：

### 🎯 核心原则：Model 层预处理，Question 层消费

> **铁律：能用 SQL 在 Model 层解决的，不要在 Question 层用 MBQL 折腾！**

| 操作 | 正确做法（Model SQL） | 错误做法（Question MBQL） |
|------|---------------------|------------------------|
| **CASE WHEN 分类** | SQL 中预计算 `频道`、`频道排序` | 在 MBQL 用复杂的 `case` 表达式 |
| **日期转换** | `STR_TO_DATE(ds, '%Y%m%d') AS 所在日` | 在 MBQL 中动态转换 |
| **中文别名** | SQL 中直接用中文别名 | 在 MBQL 中维护字段映射 |
| **Group By** | SQL 中 `GROUP BY day, uri` | `breakout` 字段和 SQL 不一致 |
| **排序** | 预计算数字排序字段（1-8） | 在 MBQL 中写复杂排序逻辑 |

### 条件聚合 - 使用 `case` 而非 `if`
```json
// ✅ 正确
["sum", ["case", [[["=", ["field", 123], "A"], ["field", 456]]]]]

// ❌ 错误 - MBQL 不支持 if
["sum", ["expression", "if(category = 'A', amount, 0)"]]
```

### 转化率计算 - 在 aggregation 中直接除法
```json
// ✅ 正确 - 在 aggregation 层计算
{
  "aggregation": [
    ["/", ["sum", ["field", 100]], ["sum", ["field", 101]]]
  ]
}

// ❌ 错误 - 避免在 expression 中定义
{
  "expressions": {
    "conversion_rate": ["/", ["field", 100], ["field", 101]]
  }
}
```

### 时间字段 - Model 层预处理
- 在 Model 中定义 `week_start`, `month_start` 等字段
- Question 中直接使用预处理字段，避免重复转换

### 可视化设计 - 参考 Dashboard 700
- **精简指标**: 只展示 3-5 个核心指标
- **双 Y 轴**: 金额类左轴，比率类右轴
- **面积图**: 用于展示累积趋势或占比变化

完整最佳实践文档: `references/mbql-best-practices.md`

---

## API 调用规范

### 认证方式
**必须使用**: `X-API-Key` Header
```bash
-H "X-API-Key: mb_xxx..."
```

**不要使用**:
- ❌ `X-Metabase-Session` (session token)
- ❌ Cookie 认证
- ❌ Basic Auth

### Collection 层级结构 ⭐

**重要发现**: Collection 使用 `location` 字段而非 `parent_id` 表示层级关系。

| 字段 | 说明 |
|------|------|
| `parent_id` | 通常为 `null`，**不能用于查询父子关系** |
| `location` | 表示完整路径，格式为 `/父ID1/父ID2/父ID3/` |

**示例**:
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

**查询子 Collections 的正确方法**:
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

### Dashboard 卡片管理 ⭐

**CRITICAL**: 必须使用 PUT 方法更新整个 Dashboard，不能用 POST。

**正确做法**:
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

**关键要点**:
- ✅ 使用 `PUT /api/dashboard/:id`，不是 POST
- ✅ 新卡片使用 **负数 ID**（-1, -2, -3...），Metabase 会自动分配正式 ID
- ✅ 必须包含 `id`, `card_id`, `row`, `col`, `size_x`, `size_y`
- ✅ `dashcards` 数组包含**所有**要显示的卡片（包括已有的和新增的）

**布局建议**:
- 全宽: `size_x: 18` (或 24)
- 半宽: `size_x: 9` (或 12)
- 三分之一: `size_x: 6` (或 8)
- 常见高度：数字卡片 `size_y: 4`，图表 `size_y: 6-8`，表格 `size_y: 8-12`

### 创建查询的最佳实践 ⭐

**原则：统一使用原生 SQL (type: "native")**

| 场景 | 推荐方式 |
|------|---------|
| 分区字段查询（如 ds） | 原生 SQL ✅ |
| 动态时间表达式 | 原生 SQL ✅ |
| 跨表 JOIN | 原生 SQL ✅ |
| CTE / 窗口函数 | 原生 SQL ✅ |
| 复杂逻辑 | 原生 SQL ✅ |

**示例**:
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

**注意事项**:
- ⚠️ 直接使用实际数据库表名
- ⚠️ 不要引用 `metabase.question_XXX` 格式
- ⚠️ 确保 SQL 语法与目标数据库兼容

---

## API 参考

详细 API 文档请参阅：`references/api-reference.md`

### 常用端点速查

#### Card API
| 操作 | 端点 | 方法 |
|------|------|------|
| 获取 Card 详情 | `/api/card/{id}` | GET |
| 查询 Card 数据 | `/api/card/{id}/query` | POST |
| 创建 Card | `/api/card` | POST |
| 更新 Card | `/api/card/{id}` | PUT |
| 删除 Card | `/api/card/{id}` | DELETE |

#### Dashboard API ⭐
| 操作 | 端点 | 方法 |
|------|------|------|
| 列出所有 Dashboard | `/api/dashboard` | GET |
| 获取 Dashboard 详情 | `/api/dashboard/{id}` | GET |
| 创建 Dashboard | `/api/dashboard` | POST |
| 更新 Dashboard | `/api/dashboard/{id}` | PUT |
| 删除 Dashboard | `/api/dashboard/{id}` | DELETE |
| 复制 Dashboard | `/api/dashboard/{id}/copy` | POST |
| **添加卡片到 Dashboard** | `/api/dashboard/{id}/cards` | POST |
| **批量更新 Dashboard 卡片** | `/api/dashboard/{id}/cards` | PUT |
| 从 Dashboard 删除卡片 | `/api/dashboard/{dashboardId}/cards/{dashcardId}` | DELETE |
| 获取 Dashboard 修订历史 | `/api/dashboard/{id}/revisions` | GET |
| 恢复 Dashboard 版本 | `/api/dashboard/{id}/revert` | POST |
| 创建公共分享链接 | `/api/dashboard/{id}/public_link` | POST |
| 删除公共分享链接 | `/api/dashboard/{id}/public_link` | DELETE |

#### Collection API
| 操作 | 端点 | 方法 |
|------|------|------|
| 列出所有 Collections | `/api/collection` | GET |
| 获取 Collection 内容 | `/api/collection/{id}/items` | GET |
| 获取 Collection 详情 | `/api/collection/{id}` | GET |
| **创建子 Collection** | `/api/collection` | POST |

**创建子 Collection 示例**:
```bash
curl -X POST "https://kmb.qunhequnhe.com/api/collection" \
  -H "X-API-Key: mb_xxx..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "子集合名称",
    "description": "描述",
    "parent_id": 485
  }'
```

#### 其他 API
| 操作 | 端点 | 方法 |
|------|------|------|
| 搜索 | `/api/search?q={keyword}` | GET |
| 获取当前用户 | `/api/user/current` | GET |
| 列出数据库 | `/api/database` | GET |
| 执行查询 | `/api/dataset` | POST |

---

## 脚本工具

### query_card.py
查询指定 Card 的数据。
```bash
python3 scripts/query_card.py <card_id> [--limit 100] [--output json|csv|table]
```

### space_sql_mapper.py
**小站数据查询工具** - 分析离线导出的小站数据，建立目录树 → 页面 → SQL 的映射。

```bash
# 搜索页面
python3 scripts/space_sql_mapper.py search <关键词>

# 查看页面详情
python3 scripts/space_sql_mapper.py page <pageId>

# 查看图表/SQL详情
python3 scripts/space_sql_mapper.py graph <graphId>

# 只输出SQL（可用于迁移）
python3 scripts/space_sql_mapper.py sql <graphId>

# 显示完整目录树
python3 scripts/space_sql_mapper.py tree
```

**数据文件位置**: `space-data/` 目录

### 其他脚本
- `search_kmb.py` - 搜索 KMB 内容
- `get_collection_cards.py` - 获取 Collection 下所有 Cards

---

## 扩展指南

### 添加新的 Dashboard 支持

1. 在 `references/dashboard-configs.md` 中添加 Dashboard 配置
2. 创建对应的报告生成脚本 `scripts/generate_<name>_report.py`
3. 更新本 SKILL.md 的快速访问表格

### 添加新的 Card 查询

1. 确定 Card ID 和所需参数
2. 使用 `query_card.py` 测试查询
3. 如需定制化输出，创建新的脚本

---

## 故障排查

### 401 Unauthorized
- 检查 API Key 是否有效
- 确认请求头格式正确

### 403 Forbidden
- 确认有权限访问该资源
- 联系管理员确认权限配置

### 数据为空
- 检查 Card ID 是否正确
- 确认日期参数范围
- 检查 Dashboard 过滤器设置

---

## 错误处理与诊断

### HTTP 401 - 认证失败
```
API key 无效或已过期
诊断步骤：
→ 检查 API key 是否正确拷贝（注意空格）
→ 在 Metabase 设置中验证 API key 状态
→ 尝试重新生成 API key
```

### HTTP 403 - 权限不足
```
当前 API key 没有执行此操作的权限
诊断步骤：
→ 检查 Metabase 中该 API key 的权限设置
→ 确认操作是否需要管理员权限
→ 考虑使用具有更高权限的 API key
```

### HTTP 404 - 资源不存在
```
资源不存在（Dashboard ID: 123）
诊断步骤：
→ 验证 ID 是否正确
→ 该资源可能已被删除
→ 运行列表命令查看现有资源
```

### HTTP 500 - 服务器错误
```
Metabase 服务器错误
诊断步骤：
→ 检查 Metabase 服务器日志
→ 稍后重试
→ 如果持续失败，联系 Metabase 管理员
```

### 连接失败
```
无法连接到 Metabase
诊断步骤：
→ 检查 URL 是否正确（https://kmb.qunhequnhe.com，无尾部斜杠）
→ 确认 Metabase 服务正在运行
→ 测试网络连接: curl -I ${HOST}
```

---

## 反模式（常见错误）

| ❌ 错误 | 为什么错 | ✅ 正确做法 |
|--------|---------|-----------|
| 使用 Query Builder (type: "query") | 不支持分区字段（如 ds）、不支持动态时间表达式 | 始终使用原生 SQL (type: "native") |
| 引用错误: `metabase.question_XXX` | 数据库名错误，导致查询失败 | 使用实际表名（原生 SQL）或 `card__ID` |
| POST 到 `/api/dashboard/:id/cards` | 此端点不存在，API 会返回 404 | 使用 PUT `/api/dashboard/:id` 更新 dashcards 数组 |
| 添加卡片时使用正数或省略 ID | 验证错误，Metabase 无法识别新卡片 | 新卡片必须使用负数 ID (-1, -2, -3...) |
| 创建 Python/Node SDK | 违反工具约束（Iron Law） | 直接用 curl |
| 不验证配置 | 无效配置会导致后续所有操作失败 | 必须调用 `/api/user/current` 验证 |
| 不验证查询是否能运行 | 创建后才发现错误 | 创建后立即用 `/api/card/:id/query` 测试 |
| 显示完整 JSON | 信息过载 | 简洁摘要关键字段 |
| 使用 Session token | API key 更安全、无需登录 | 使用 X-API-Key header |
| 一次问所有问题 | 不友好 | 逐步交互式对话 |
| 只说"权限错误" | 不够 helpful | 提供 2-3 个诊断步骤 |

---

## 参考资料

- `references/api-reference.md` - 完整 API 文档
- `references/mbql-best-practices.md` - **MBQL 编写最佳实践**
- `references/dashboard-configs.md` - Dashboard 配置详情
- `references/card-catalog.md` - 常用 Card 目录
- `references/migration-guide.md` - **小站 → KMB 迁移指南**
- `rules/constraints.md` - **工具约束（Iron Law）**
- `rules/api-standards.md` - **API 调用标准**
- `rules/error-handling.md` - **错误处理与诊断**
- `rules/red-flags.md` - **危险信号（Red Flags）**
- `space-data/` - **小站离线数据**（目录树映射、SQL查询）
- `scripts/` - 可执行脚本集合
