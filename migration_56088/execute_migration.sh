#!/bin/bash
# ============================================================
# Page 56088 迁移执行脚本
# 小站: 新版实验 - 支付弹窗转化 → KMB Collection 564
# ============================================================

set -e

# 配置
API_HOST="https://kmb.qunhequnhe.com"
COLLECTION_ID=564
DATABASE_ID=4
MIGRATION_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=============================================="
echo "Page 56088 迁移执行脚本"
echo "=============================================="
echo ""

# 检查环境
if [ -z "$API_KEY" ]; then
    echo "错误: 请设置 API_KEY 环境变量"
    exit 1
fi

# Step 1: 创建 Model
echo "[Step 1/5] 创建 Model..."
MODEL_RESPONSE=$(curl -s -X POST "${API_HOST}/api/card" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: ${API_KEY}" \
    -d @- << EOF
{
  "name": "【P56088】支付弹窗事件明细",
  "type": "model",
  "collection_id": ${COLLECTION_ID},
  "display": "table",
  "visualization_settings": {},
  "dataset_query": {
    "database": ${DATABASE_ID},
    "type": "native",
    "native": {
      "query": $(cat "${MIGRATION_DIR}/model.sql" | jq -Rs .)
    }
  }
}
EOF
)

MODEL_ID=$(echo "$MODEL_RESPONSE" | jq -r '.id')
if [ "$MODEL_ID" == "null" ] || [ -z "$MODEL_ID" ]; then
    echo "Model 创建失败:"
    echo "$MODEL_RESPONSE" | jq '.'
    exit 1
fi

echo "✅ Model 创建成功: ID=${MODEL_ID}"
echo ""

# Step 2: 创建 Questions
echo "[Step 2/5] 创建 Questions..."

QUESTION_IDS=()

# Question 01: 每日打开弹窗UV
echo "  - 创建 Question 01: 每日打开弹窗UV..."
Q01_CONFIG=$(cat "${MIGRATION_DIR}/questions/01_open_uv.json" | jq --arg model_id "card__${MODEL_ID}" '. + {"source-table": $model_id}')
Q01_RESPONSE=$(curl -s -X POST "${API_HOST}/api/card" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: ${API_KEY}" \
    -d "$Q01_CONFIG")
Q01_ID=$(echo "$Q01_RESPONSE" | jq -r '.id')
QUESTION_IDS+=("$Q01_ID")
echo "    ✅ ID=${Q01_ID}"

# Question 02: 每日支付成功UV
echo "  - 创建 Question 02: 每日支付成功UV..."
Q02_CONFIG=$(cat "${MIGRATION_DIR}/questions/02_pay_uv.json" | jq --arg model_id "card__${MODEL_ID}" '. + {"source-table": $model_id}')
Q02_RESPONSE=$(curl -s -X POST "${API_HOST}/api/card" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: ${API_KEY}" \
    -d "$Q02_CONFIG")
Q02_ID=$(echo "$Q02_RESPONSE" | jq -r '.id')
QUESTION_IDS+=("$Q02_ID")
echo "    ✅ ID=${Q02_ID}"

# Question 03: 每日支付金额
echo "  - 创建 Question 03: 每日支付金额..."
Q03_CONFIG=$(cat "${MIGRATION_DIR}/questions/03_revenue.json" | jq --arg model_id "card__${MODEL_ID}" '. + {"source-table": $model_id}')
Q03_RESPONSE=$(curl -s -X POST "${API_HOST}/api/card" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: ${API_KEY}" \
    -d "$Q03_CONFIG")
Q03_ID=$(echo "$Q03_RESPONSE" | jq -r '.id')
QUESTION_IDS+=("$Q03_ID")
echo "    ✅ ID=${Q03_ID}"

# Question 04: 弹窗版本对比
echo "  - 创建 Question 04: 弹窗版本对比..."
Q04_CONFIG=$(cat "${MIGRATION_DIR}/questions/04_funnel_comparison.json" | jq --arg model_id "card__${MODEL_ID}" '. + {"source-table": $model_id}')
Q04_RESPONSE=$(curl -s -X POST "${API_HOST}/api/card" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: ${API_KEY}" \
    -d "$Q04_CONFIG")
Q04_ID=$(echo "$Q04_RESPONSE" | jq -r '.id')
QUESTION_IDS+=("$Q04_ID")
echo "    ✅ ID=${Q04_ID}"

# Question 05: 用户付费分层
echo "  - 创建 Question 05: 用户付费分层..."
Q05_CONFIG=$(cat "${MIGRATION_DIR}/questions/05_paid_level.json" | jq --arg model_id "card__${MODEL_ID}" '. + {"source-table": $model_id}')
Q05_RESPONSE=$(curl -s -X POST "${API_HOST}/api/card" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: ${API_KEY}" \
    -d "$Q05_CONFIG")
Q05_ID=$(echo "$Q05_RESPONSE" | jq -r '.id')
QUESTION_IDS+=("$Q05_ID")
echo "    ✅ ID=${Q05_ID}"

echo ""

# Step 3: 配置可视化 (更新 Question 配置)
echo "[Step 3/5] 配置可视化..."

# 为 Question 02 和 03 配置 MixLineBar
echo "  - 配置 MixLineBar 可视化..."
VIZ_CONFIG=$(cat "${MIGRATION_DIR}/viz/mixlinebar_funnel.json")

# 更新 Q02 (支付成功UV + 转化率)
curl -s -X PUT "${API_HOST}/api/card/${Q02_ID}" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: ${API_KEY}" \
    -d "$VIZ_CONFIG" > /dev/null
echo "    ✅ Question ${Q02_ID} 可视化配置完成"

echo ""

# Step 4: 创建 Dashboard
echo "[Step 4/5] 创建 Dashboard..."

DASHBOARD_RESPONSE=$(curl -s -X POST "${API_HOST}/api/dashboard" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: ${API_KEY}" \
    -d @- << EOF
{
  "name": "【P56088】支付弹窗转化",
  "collection_id": ${COLLECTION_ID},
  "description": "小站 page/56088 迁移版本 - 支付弹窗漏斗分析"
}
EOF
)

DASHBOARD_ID=$(echo "$DASHBOARD_RESPONSE" | jq -r '.id')
if [ "$DASHBOARD_ID" == "null" ] || [ -z "$DASHBOARD_ID" ]; then
    echo "Dashboard 创建失败:"
    echo "$DASHBOARD_RESPONSE" | jq '.'
    exit 1
fi

echo "✅ Dashboard 创建成功: ID=${DASHBOARD_ID}"
echo ""

# Step 5: 添加卡片到 Dashboard
echo "[Step 5/5] 添加卡片到 Dashboard..."

# 构建 dashcards 配置
DASHCARDS_CONFIG=$(cat "${MIGRATION_DIR}/dashboard.json" | jq --arg q01 "$Q01_ID" --arg q02 "$Q02_ID" --arg q03 "$Q03_ID" --arg q04 "$Q04_ID" --arg q05 "$Q05_ID" '
  .dashcards |
  map(.card_id = if .card_id == "{question_01_id}" then $q01
    elif .card_id == "{question_02_id}" then $q02
    elif .card_id == "{question_03_id}" then $q03
    elif .card_id == "{question_04_id}" then $q04
    elif .card_id == "{question_05_id}" then $q05
    else .card_id end) |
  map(.parameter_mappings = map(.card_id = if .card_id == "{question_01_id}" then $q01
    elif .card_id == "{question_02_id}" then $q02
    elif .card_id == "{question_03_id}" then $q03
    elif .card_id == "{question_04_id}" then $q04
    elif .card_id == "{question_05_id}" then $q05
    else .card_id end))
')

curl -s -X PUT "${API_HOST}/api/dashboard/${DASHBOARD_ID}" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: ${API_KEY}" \
    -d "{\"dashcards\": ${DASHCARDS_CONFIG}}" > /dev/null

echo "✅ Dashboard 卡片添加完成"
echo ""

# 输出结果
echo "=============================================="
echo "迁移完成！"
echo "=============================================="
echo ""
echo "创建的资源:"
echo "  - Model ID: ${MODEL_ID}"
echo "  - Question 01 (打开弹窗UV): ${Q01_ID}"
echo "  - Question 02 (支付成功UV): ${Q02_ID}"
echo "  - Question 03 (支付金额): ${Q03_ID}"
echo "  - Question 04 (版本对比): ${Q04_ID}"
echo "  - Question 05 (付费分层): ${Q05_ID}"
echo "  - Dashboard ID: ${DASHBOARD_ID}"
echo ""
echo "Dashboard URL: ${API_HOST}/dashboard/${DASHBOARD_ID}"
echo ""

# 保存映射关系到文件
cat > "${MIGRATION_DIR}/asset_mapping.json" << EOF
{
  "migration_timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "source": {
    "space_page_id": 56088,
    "space_page_name": "新版实验 - 支付弹窗转化"
  },
  "target": {
    "collection_id": ${COLLECTION_ID}
  },
  "assets": {
    "model": {
      "id": ${MODEL_ID},
      "name": "【P56088】支付弹窗事件明细"
    },
    "questions": [
      {"id": ${Q01_ID}, "name": "【56088】每日打开弹窗UV", "graph_id": 73731},
      {"id": ${Q02_ID}, "name": "【56088】每日支付成功UV", "graph_id": 73732},
      {"id": ${Q03_ID}, "name": "【56088】每日支付金额", "graph_id": 73733},
      {"id": ${Q04_ID}, "name": "【56088】弹窗版本对比", "graph_id": 73734},
      {"id": ${Q05_ID}, "name": "【56088】用户付费分层", "graph_id": 73735}
    ],
    "dashboard": {
      "id": ${DASHBOARD_ID},
      "name": "【P56088】支付弹窗转化",
      "url": "${API_HOST}/dashboard/${DASHBOARD_ID}"
    }
  }
}
EOF

echo "资源映射已保存到: ${MIGRATION_DIR}/asset_mapping.json"
