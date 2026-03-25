# KMB Skill - 错误处理与诊断

## HTTP 401 - 认证失败

```
API key 无效或已过期
```

### 诊断步骤
1. 检查 API key 是否正确拷贝（注意空格）
2. 在 Metabase 设置中验证 API key 状态
3. 尝试重新生成 API key
4. 更新配置中的 API key

### 修复命令
```bash
# 测试 API key 是否有效
curl -X GET "https://kmb.qunhequnhe.com/api/user/current" \
  -H "X-API-Key: mb_xxx..."
```

---

## HTTP 403 - 权限不足

```
当前 API key 没有执行此操作的权限
```

### 诊断步骤
1. 检查 Metabase 中该 API key 的权限设置
2. 确认操作是否需要管理员权限
3. 考虑使用具有更高权限的 API key

---

## HTTP 404 - 资源不存在

```
资源不存在（Dashboard ID: 123）
```

### 诊断步骤
1. 验证 ID 是否正确
2. 该资源可能已被删除
3. 运行列表命令查看现有资源

### 修复命令
```bash
# 列出所有仪表板
curl -X GET "https://kmb.qunhequnhe.com/api/dashboard" \
  -H "X-API-Key: mb_xxx..."

# 列出所有问题
curl -X GET "https://kmb.qunhequnhe.com/api/card" \
  -H "X-API-Key: mb_xxx..."
```

---

## HTTP 500 - 服务器错误

```
Metabase 服务器错误
```

### 诊断步骤
1. 检查 Metabase 服务器日志
2. 稍后重试
3. 如果持续失败，联系 Metabase 管理员

---

## 连接失败

```
无法连接到 Metabase
```

### 诊断步骤
1. 检查 URL 是否正确（https://kmb.qunhequnhe.com，无尾部斜杠）
2. 确认 Metabase 服务正在运行
3. 测试网络连接

### 修复命令
```bash
# 测试连接
curl -I https://kmb.qunhequnhe.com
```

---

## 查询错误

### 错误：Unknown database 'metabase'

**原因**: 在原生 SQL 中使用了错误的表名引用格式

**错误示例**:
```sql
-- ❌ 错误
SELECT * FROM metabase.question_2059
```

**正确做法**:
```sql
-- ✅ 正确：使用实际表名
SELECT * FROM actual_table_name

-- 或在 MBQL 中使用
"source-table": "card__2059"
```

---

## 数据为空

### 可能原因
1. Card ID 不正确
2. 日期参数范围错误
3. Dashboard 过滤器设置不正确
4. SQL 查询条件过于严格

### 诊断步骤
1. 检查 Card ID 是否正确
2. 确认日期参数范围
3. 检查 Dashboard 过滤器设置
4. 简化 SQL 条件，逐步排查

---

## Dashboard 卡片添加失败

### 错误：404 Not Found
**原因**: 使用了错误的端点

**错误示例**:
```bash
# ❌ 错误 - 此端点不存在
curl -X POST "${HOST}/api/dashboard/${id}/cards"
```

**正确做法**:
```bash
# ✅ 正确 - 使用 PUT 更新整个 Dashboard
curl -X PUT "${HOST}/api/dashboard/${id}" \
  -d '{"dashcards": [...]}'
```

---

## Collection 查询不到子项

### 可能原因
使用了 `parent_id` 字段查询，但 Metabase 使用 `location` 字段表示层级关系

### 正确做法
```bash
# 使用 location 字段查询
curl -sL "${HOST}/api/collection" \
  -H "X-API-Key: ${API_KEY}" | \
  jq -r '.[] | select(.location == "/父ID/") | "\(.id)|\(.name)"'
```
