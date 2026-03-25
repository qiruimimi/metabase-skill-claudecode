# KMB Skill - Red Flags（危险信号）

## 🚨 立即停止并重新思考

以下情况出现时，**必须**停止当前操作，删除代码，重新开始：

---

## 危险信号清单

### 1. 创建客户端/库/SDK

**❌ 危险信号**:
```python
# 不要这样做！
class MetabaseClient:
    def __init__(self, host, api_key):
        self.host = host
        self.api_key = api_key
    
    def get_dashboard(self, id):
        return requests.get(...)
```

**✅ 正确做法**:
```bash
# 直接用 curl
curl -X GET "${HOST}/api/dashboard/${id}" \
  -H "X-API-Key: ${API_KEY}"
```

**为什么**: 违反 Iron Law（铁律），引入不必要的复杂性

---

### 2. 绕过确认流程

**❌ 危险信号**:
- 直接使用用户提供的信息而不确认
- 不验证配置直接保存
- 不测试查询是否能运行

**✅ 正确做法**:
- 逐步确认用户提供的信息
- 验证配置：调用 `/api/user/current`
- 测试查询：调用 `/api/card/:id/query`

---

### 3. 使用错误的 API 端点

**❌ 危险信号**:
```bash
# 不要这样做！
curl -X POST "${HOST}/api/dashboard/${id}/cards"
```

**✅ 正确做法**:
```bash
# 正确做法
curl -X PUT "${HOST}/api/dashboard/${id}" \
  -d '{"dashcards": [...]}'
```

---

### 4. 使用 Query Builder 而非原生 SQL

**❌ 危险信号**:
```json
{
  "dataset_query": {
    "type": "query",
    "query": {
      "source-table": "card__2059"
    }
  }
}
```

**✅ 正确做法**:
```json
{
  "dataset_query": {
    "type": "native",
    "native": {
      "query": "SELECT ... FROM actual_table"
    }
  }
}
```

**为什么**: Query Builder 不支持分区字段、动态时间表达式等

---

### 5. 添加 Dashboard 卡片时使用正数 ID

**❌ 危险信号**:
```json
{
  "dashcards": [
    {"id": 1, "card_id": 100}  // ❌ 错误
  ]
}
```

**✅ 正确做法**:
```json
{
  "dashcards": [
    {"id": -1, "card_id": 100}  // ✅ 正确：负数 ID
  ]
}
```

**为什么**: 新卡片必须使用负数 ID，Metabase 会自动分配正式 ID

---

### 6. 使用错误的表名引用

**❌ 危险信号**:
```sql
-- 不要这样做！
SELECT * FROM metabase.question_2059
```

**✅ 正确做法**:
```sql
-- 正确做法
SELECT * FROM actual_database.actual_table
```

---

### 7. 不验证就直接使用配置

**❌ 危险信号**:
- 读取配置文件后直接使用，不验证连接
- 不检查 API key 是否有效

**✅ 正确做法**:
```bash
# 验证配置
curl -X GET "${HOST}/api/user/current" \
  -H "X-API-Key: ${API_KEY}"
```

---

## 处理流程

当发现危险信号时：

1. **立即停止**: 不要再继续当前操作
2. **删除代码**: 清除所有已编写的代码
3. **重新思考**: 回顾 SKILL.md 和 rules/
4. **重新开始**: 按照正确的方式重新实现

## 记住

> **Iron Law**: 只使用 curl 调用 API，保持简洁、验证、交互三大原则。

违反 = 删除所有代码，重新开始
