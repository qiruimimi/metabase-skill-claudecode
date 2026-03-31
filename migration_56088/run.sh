#!/bin/bash
# ============================================================
# Page 56088 迁移执行脚本
# 使用方式: API_KEY=xxx bash run.sh
# ============================================================

set -e

# 配置
API_HOST="https://kmb.qunhequnhe.com"
COLLECTION_ID=564
DATABASE_ID=4
MIGRATION_DIR="$(cd "$(dirname "$0")" && pwd)"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=============================================="
echo "Page 56088 迁移执行"
echo "=============================================="
echo ""

# 检查 API_KEY
if [ -z "$API_KEY" ]; then
    echo -e "${RED}错误: 请设置 API_KEY 环境变量${NC}"
    echo "使用方式: API_KEY=xxx bash run.sh"
    exit 1
fi

# Step 1: 创建 Model
echo -e "${YELLOW}[Step 1/5] 创建 Model...${NC}"
MODEL_SQL=$(cat "${MIGRATION_DIR}/model.sql" | sed 's/"/\\"/g' | tr '\n' ' ')

MODEL_RESPONSE=$(curl -s -X POST "${API_HOST}/api/card" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: ${API_KEY}" \
    -d "{
        \"name\": \"【P56088】支付弹窗事件明细\",
        \"type\": \"model\",
        \"collection_id\": ${COLLECTION_ID},
        \"display\": \"table\",
        \"visualization_settings\": {},
        \"dataset_query\": {
            \"database\": ${DATABASE_ID},
            \"type\": \"native\",
            \"native\": {
                \"query\": \"${MODEL_SQL}\"
            }
        }
    }" 2>/dev/null)

MODEL_ID=$(echo "$MODEL_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)

if [ -z "$MODEL_ID" ]; then
    echo -e "${RED}Model 创建失败${NC}"
    echo "$MODEL_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✓ Model 创建成功: ID=${MODEL_ID}${NC}"
echo ""

# Step 2: 创建 Questions
echo -e "${YELLOW}[Step 2/5] 创建 Questions...${NC}"

Q_IDS=()
Q_NAMES=("每日打开弹窗UV" "每日支付成功UV" "每日支付金额" "弹窗版本对比" "用户付费分层")
Q_FILES=("01_open_uv.json" "02_pay_uv.json" "03_revenue.json" "04_funnel_comparison.json" "05_paid_level.json")

for i in {0..4}; do
    echo "  创建 Question $((i+1)): ${Q_NAMES[$i]}..."

    # 读取并修改配置，添加 source-table
    Q_CONFIG=$(cat "${MIGRATION_DIR}/questions/${Q_FILES[$i]}" | \
        sed "s/\"collection_id\": 564/\"collection_id\": ${COLLECTION_ID}/" | \
        sed 's/}$/, "source-table": "card__'${MODEL_ID}'"}/')

    Q_RESPONSE=$(curl -s -X POST "${API_HOST}/api/card" \
        -H "Content-Type: application/json" \
        -H "X-API-Key: ${API_KEY}" \
        -d "$Q_CONFIG" 2>/dev/null)

    Q_ID=$(echo "$Q_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)
    Q_IDS+=($Q_ID)

    echo -e "    ${GREEN}✓ ID=${Q_ID}${NC}"
done

echo ""

# Step 3: 配置可视化
echo -e "${YELLOW}[Step 3/5] 配置可视化...${NC}"
echo "  MixLineBar 双轴配置..."

# 更新 Q02 和 Q03 的可视化
VIZ_CONFIG='{
  "display": "line",
  "graph.dimensions": ["event_date"],
  "graph.metrics": ["打开弹窗UV", "支付成功UV", "转化率"],
  "graph.show_values": true,
  "series_settings": {
    "打开弹窗UV": {"axis": "left", "display": "bar"},
    "支付成功UV": {"axis": "left", "display": "bar"},
    "转化率": {"axis": "right", "display": "line"}
  },
  "column_settings": {
    "[\\"name\\",\\"转化率\\"]": {"number_style": "percent", "decimals": 2}
  }
}'

curl -s -X PUT "${API_HOST}/api/card/${Q_IDS[1]}" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: ${API_KEY}" \
    -d "$VIZ_CONFIG" > /dev/null 2>&1

echo -e "  ${GREEN}✓ 可视化配置完成${NC}"
echo ""

# Step 4: 创建 Dashboard
echo -e "${YELLOW}[Step 4/5] 创建 Dashboard...${NC}"

DASHBOARD_RESPONSE=$(curl -s -X POST "${API_HOST}/api/dashboard" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: ${API_KEY}" \
    -d "{
        \"name\": \"【P56088】支付弹窗转化\",
        \"collection_id\": ${COLLECTION_ID},
        \"description\": \"小站 page/56088 迁移版本 - 支付弹窗漏斗分析\"
    }" 2>/dev/null)

DASHBOARD_ID=$(echo "$DASHBOARD_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)

echo -e "${GREEN}✓ Dashboard 创建成功: ID=${DASHBOARD_ID}${NC}"
echo ""

# Step 5: 添加卡片
echo -e "${YELLOW}[Step 5/5] 添加卡片到 Dashboard...${NC}"

DASHCARMS=$(cat <<EOF
[
  {"id": -1, "card_id": ${Q_IDS[0]}, "row": 0, "col": 0, "size_x": 12, "size_y": 8, "parameter_mappings": [{"parameter_id": "date_range", "card_id": ${Q_IDS[0]}, "target": ["dimension", ["field", "event_date", {"base-type": "type/Date"}], {"stage-number": 0}]}]},
  {"id": -2, "card_id": ${Q_IDS[1]}, "row": 0, "col": 12, "size_x": 12, "size_y": 8, "parameter_mappings": [{"parameter_id": "date_range", "card_id": ${Q_IDS[1]}, "target": ["dimension", ["field", "event_date", {"base-type": "type/Date"}], {"stage-number": 0}]}]},
  {"id": -3, "card_id": ${Q_IDS[2]}, "row": 8, "col": 0, "size_x": 24, "size_y": 8, "parameter_mappings": [{"parameter_id": "date_range", "card_id": ${Q_IDS[2]}, "target": ["dimension", ["field", "event_date", {"base-type": "type/Date"}], {"stage-number": 0}]}]},
  {"id": -4, "card_id": ${Q_IDS[3]}, "row": 16, "col": 0, "size_x": 12, "size_y": 8, "parameter_mappings": [{"parameter_id": "date_range", "card_id": ${Q_IDS[3]}, "target": ["dimension", ["field", "event_date", {"base-type": "type/Date"}], {"stage-number": 0}]}, {"parameter_id": "popup_version", "card_id": ${Q_IDS[3]}, "target": ["dimension", ["field", "popup_version", {"base-type": "type/Text"}], {"stage-number": 0}]}]},
  {"id": -5, "card_id": ${Q_IDS[4]}, "row": 16, "col": 12, "size_x": 12, "size_y": 8, "parameter_mappings": [{"parameter_id": "date_range", "card_id": ${Q_IDS[4]}, "target": ["dimension", ["field", "event_date", {"base-type": "type/Date"}], {"stage-number": 0}]}]}
]
EOF
)

curl -s -X PUT "${API_HOST}/api/dashboard/${DASHBOARD_ID}" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: ${API_KEY}" \
    -d "{\"dashcards\": ${DASHCARMS}}" > /dev/null 2>&1

echo -e "${GREEN}✓ Dashboard 卡片添加完成${NC}"
echo ""

# 输出结果
echo "=============================================="
echo -e "${GREEN}迁移完成！${NC}"
echo "=============================================="
echo ""
echo "资产映射:"
echo "  Model ID: ${MODEL_ID}"
echo "  Question 01 (打开弹窗UV): ${Q_IDS[0]}"
echo "  Question 02 (支付成功UV): ${Q_IDS[1]}"
echo "  Question 03 (支付金额): ${Q_IDS[2]}"
echo "  Question 04 (版本对比): ${Q_IDS[3]}"
echo "  Question 05 (付费分层): ${Q_IDS[4]}"
echo "  Dashboard ID: ${DASHBOARD_ID}"
echo ""
echo "访问链接: ${API_HOST}/dashboard/${DASHBOARD_ID}"
echo ""

# 保存映射
cat > "${MIGRATION_DIR}/asset_mapping.json" << EOF
{
  "page_id": 56088,
  "page_name": "新版实验 - 支付弹窗转化",
  "collection_id": ${COLLECTION_ID},
  "model_id": ${MODEL_ID},
  "question_ids": [${Q_IDS[0]}, ${Q_IDS[1]}, ${Q_IDS[2]}, ${Q_IDS[3]}, ${Q_IDS[4]}],
  "dashboard_id": ${DASHBOARD_ID},
  "dashboard_url": "${API_HOST}/dashboard/${DASHBOARD_ID}"
}
EOF

echo "资产映射已保存到: asset_mapping.json"
