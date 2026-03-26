# KMB Skill - 工具约束（Iron Law）

## Iron Law（铁律）

```
默认优先直接调用 Metabase API（curl）
允许使用仓库内现有 scripts/ 与 scripts/core 进行自动化
禁止新建重型 SDK、通用客户端框架或多层封装

违反 = 回退到最小可运行实现，删除过度抽象
```

## 核心原则

- **简洁**: 能直接调用 API 就不额外封装。
- **验证**: 每次关键写操作前后都要验证（如 `/api/user/current`、`/api/card/:id/query`）。
- **交互**: 输出面向执行，包含必要诊断信息。

## 工具使用边界

### ✅ 允许的工具

- `curl`: 直接 API 调用与验证
- `python3`: 现有脚本执行、批处理、格式化输出
- `jq`: JSON 过滤和结构检查

### ❌ 禁止的操作

- 新建独立 Metabase SDK（Python/Node/TS 等）
- 引入复杂客户端框架或生成式 API client
- 为一次性任务拆分大量“辅助库”文件
- 在无必要时增加额外抽象层

## 为什么这样约束

- **降低维护成本**: 优先直连 API，可快速定位问题
- **避免架构漂移**: 自动化脚本可复用，但不演化为平台级 SDK
- **保持一致性**: 围绕 `scripts/core` 统一配置/HTTP/错误处理

## 选择策略

1. **一次性操作/调试**：优先 `curl`
2. **重复操作/报表生成**：复用 `scripts/*.py`
3. **跨脚本共用能力**：仅在 `scripts/core/*` 扩展最小公共能力

## 示例

### ✅ 正确：直接调用 API
```bash
curl -X GET "${HOST}/api/dashboard" \
  -H "X-API-Key: ${API_KEY}"
```

### ✅ 正确：复用现有脚本内核
```python
from core.http import get_json

def get_dashboard(dashboard_id: int):
    return get_json(f"/api/dashboard/{dashboard_id}")
```

### ❌ 错误：新建重型 SDK
```python
# 禁止这样做
class MetabaseClient:
    def __init__(self, host, api_key):
        self.host = host
        self.api_key = api_key

    def get_dashboard(self, dashboard_id):
        # 过度封装 + 框架化扩张
        ...
```
