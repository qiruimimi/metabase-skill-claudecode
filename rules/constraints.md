# KMB Skill - 工具约束（Iron Law）

## Iron Law（铁律）

```
只使用 curl 调用 API
禁止创建 SDK、库、Python/Node 客户端
禁止创建多个辅助文件

违反 = 删除所有代码，重新开始
```

## 核心原则

- **简洁**: 使用 curl 进行 API 调用
- **验证**: 验证所有输入和输出
- **交互**: 提供友好的交互式对话

## 工具使用限制

### ✅ 允许的工具

- `curl`: 用于所有 API 调用
- `python3`: 用于脚本逻辑（迁移脚本、数据处理）
- `jq`: 用于 JSON 解析和格式化

### ❌ 禁止的操作

- 创建 SDK 或库
- 创建 Python/Node 复杂客户端
- 创建多个辅助文件
- 使用复杂的框架或工具

## 违反后果

如果违反 Iron Law，将导致：
- 代码被删除
- 重新开始实现
- 浪费时间和资源

## 原因说明

Iron Law 的存在是因为：
- **简化维护**: 只使用基础工具，易于理解和维护
- **避免复杂**: 不引入额外的依赖和复杂性
- **统一风格**: 保持代码风格一致
- **快速迭代**: 简单的实现更容易修改和扩展

## 示例

### ✅ 正确：使用 curl
```bash
curl -X GET "${HOST}/api/dashboard" \
  -H "X-API-Key: ${API_KEY}"
```

### ❌ 错误：创建复杂 SDK
```python
# 禁止这样做
class MetabaseClient:
    def __init__(self, host, api_key):
        self.host = host
        self.api_key = api_key
    
    def get_dashboard(self, id):
        # ... 复杂封装
```
