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

---

## 删除 Collection 返回 404

### 错误：`DELETE /api/collection/{id}` → `API endpoint does not exist.`

**原因**: KMB 当前不暴露 Collection DELETE 端点。

**错误示例**:
```bash
# ❌ 错误
curl -X DELETE "${HOST}/api/collection/${id}" \
  -H "X-API-Key: ${API_KEY}"
```

**正确做法**:
```bash
# ✅ 正确 - 使用 PUT 将 Collection 移到 Trash
curl -X PUT "${HOST}/api/collection/${id}" \
  -H "X-API-Key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Collection 名称",
    "archived": true
  }'
```

补充说明：
- 这不是永久删除，而是移到 Trash
- 清理误建迁移目录时，优先归档整棵错误树的根 Collection

---

## Card 查询返回了 JSON，但其实失败了

### 错误：`/api/card/{id}/query` 有响应体，但 `status` 是 `failed`

**原因**: 不能只看“是否返回 JSON”来判断查询成功；失败响应也可能包含 `data`、`native_form`、SQL 片段或调试信息。

### 正确做法
验证时必须显式检查：
- `status == "completed"` 才算成功
- `status == "failed"` 一律算失败

### 常见根因
1. SQL 中存在未全限定的表名
2. Model 底层 native SQL 仍有运行时错误
3. 参数默认值或字段映射不合法

---

## 脚本运行时错误输出（重构后）

当前脚本统一使用以下错误输出风格：

- 标准格式：`Error: <具体错误信息>`
- 输出位置：`stderr`
- 退出码：失败时返回非 0

示例：
```text
Error: HTTP 404 - Not Found
Error: Connection failed: timed out
Error: 图表 999 不存在
```
