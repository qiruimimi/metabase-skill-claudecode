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
# 一次性操作优先直接调用 API
curl -X GET "${HOST}/api/dashboard/${id}" \
  -H "X-API-Key: ${API_KEY}"
```

或复用仓库内已有 `scripts/` 与 `scripts/core/`，不要新建重型 SDK。

**为什么**: 防止过度封装和架构漂移，保持最小可维护实现

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

### 4. 过早回退原生 SQL（未完成 MBQL 拆解）

**❌ 危险信号**:
```json
{
  "dataset_query": {
    "type": "native",
    "native": {
      "query": "SELECT ..."
    }
  }
}
```
在尚未完成以下动作前就直接回退：
- `UNION ALL` 未拆分为多个 MBQL Question；
- 动态时间未改为“增量数据 + Dashboard 日期筛选”；
- Model 缺字段未先补齐预加工。

**✅ 正确做法**:
```json
{
  "dataset_query": {
    "type": "query",
    "query": {
      "source-table": "card__model_id",
      "aggregation": [["count"]]
    }
  }
}
```

**边界说明**:
- 默认必须 Model + MBQL；
- 复杂逻辑先做 Model 分层与 Question 拆分；
- 原生 SQL 仅在完全无法解决且已记录原因时允许例外。

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

> **Iron Law**: 默认优先直接调用 API（curl），必要时复用仓库现有脚本；禁止新建重型 SDK。

违反 = 删除所有代码，重新开始
