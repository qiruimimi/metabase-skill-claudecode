#!/bin/bash
# 手动创建 Questions - 复制到终端逐行执行

export API_KEY="mb_h5ddq58TgNTAZsV7e81myvAxMlMcqXWrx1y9TdqArl8="
export API_HOST="https://kmb.qunhequnhe.com"
export MODEL_ID=13371409
export COLLECTION_ID=564

echo "创建 Question 1: 每日打开弹窗UV..."
Q01=$(curl -s -X POST "${API_HOST}/api/card" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "name": "【56088】每日打开弹窗UV",
    "collection_id": '${COLLECTION_ID}',
    "display": "line",
    "dataset_query": {
      "database": 4,
      "query": {
        "source-table": "card__'${MODEL_ID}'",
        "aggregation": [["aggregation-options", ["distinct", ["field", "userid", {"base-type": "type/Text"}]], {"name": "打开弹窗UV", "display-name": "打开弹窗UV"}]],
        "breakout": [["field", "event_date", {"base-type": "type/Date", "temporal-unit": "day"}]]
      },
      "type": "query"
    }
  }' | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)
echo "Q01 ID: $Q01"

echo "创建 Question 2: 每日支付成功UV..."
Q02=$(curl -s -X POST "${API_HOST}/api/card" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "name": "【56088】每日支付成功UV",
    "collection_id": '${COLLECTION_ID}',
    "display": "line",
    "dataset_query": {
      "database": 4,
      "query": {
        "source-table": "card__'${MODEL_ID}'",
        "aggregation": [["aggregation-options", ["distinct", ["case", [[["=", ["field", "event_type", {"base-type": "type/Text"}], "pay.success"], ["field", "userid", {"base-type": "type/Text"}]]]]], {"name": "支付成功UV", "display-name": "支付成功UV"}]],
        "breakout": [["field", "event_date", {"base-type": "type/Date", "temporal-unit": "day"}]]
      },
      "type": "query"
    }
  }' | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)
echo "Q02 ID: $Q02"

echo "创建 Question 3: 每日支付金额..."
Q03=$(curl -s -X POST "${API_HOST}/api/card" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "name": "【56088】每日支付金额",
    "collection_id": '${COLLECTION_ID}',
    "display": "line",
    "dataset_query": {
      "database": 4,
      "query": {
        "source-table": "card__'${MODEL_ID}'",
        "aggregation": [["aggregation-options", ["sum", ["field", "amount_usd", {"base-type": "type/Float"}]], {"name": "支付金额", "display-name": "支付金额(USD)"}]],
        "breakout": [["field", "event_date", {"base-type": "type/Date", "temporal-unit": "day"}]]
      },
      "type": "query"
    }
  }' | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)
echo "Q03 ID: $Q03"

echo "创建 Question 4: 弹窗版本对比..."
Q04=$(curl -s -X POST "${API_HOST}/api/card" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "name": "【56088】弹窗版本对比",
    "collection_id": '${COLLECTION_ID}',
    "display": "line",
    "dataset_query": {
      "database": 4,
      "query": {
        "source-table": "card__'${MODEL_ID}'",
        "aggregation": [["aggregation-options", ["distinct", ["field", "userid", {"base-type": "type/Text"}]], {"name": "UV", "display-name": "UV"}]],
        "breakout": [
          ["field", "event_date", {"base-type": "type/Date", "temporal-unit": "day"}],
          ["field", "popup_version", {"base-type": "type/Text"}]
        ]
      },
      "type": "query"
    }
  }' | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)
echo "Q04 ID: $Q04"

echo "创建 Question 5: 用户付费分层..."
Q05=$(curl -s -X POST "${API_HOST}/api/card" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "name": "【56088】用户付费分层",
    "collection_id": '${COLLECTION_ID}',
    "display": "line",
    "dataset_query": {
      "database": 4,
      "query": {
        "source-table": "card__'${MODEL_ID}'",
        "aggregation": [["aggregation-options", ["distinct", ["field", "userid", {"base-type": "type/Text"}]], {"name": "UV", "display-name": "UV"}]],
        "breakout": [
          ["field", "event_date", {"base-type": "type/Date", "temporal-unit": "day"}],
          ["field", "user_paid_level", {"base-type": "type/Text"}]
        ]
      },
      "type": "query"
    }
  }' | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)
echo "Q05 ID: $Q05"

echo ""
echo "更新 Dashboard 621 卡片..."
curl -s -X PUT "${API_HOST}/api/dashboard/621" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "dashcards": [
      {"id": -1, "card_id": '$Q01', "row": 0, "col": 0, "size_x": 12, "size_y": 8, "parameter_mappings": [{"parameter_id": "date_range", "card_id": '$Q01', "target": ["dimension", ["field", "event_date", {"base-type": "type/Date"}], {"stage-number": 0}]}]},
      {"id": -2, "card_id": '$Q02', "row": 0, "col": 12, "size_x": 12, "size_y": 8, "parameter_mappings": [{"parameter_id": "date_range", "card_id": '$Q02', "target": ["dimension", ["field", "event_date", {"base-type": "type/Date"}], {"stage-number": 0}]}]},
      {"id": -3, "card_id": '$Q03', "row": 8, "col": 0, "size_x": 24, "size_y": 8, "parameter_mappings": [{"parameter_id": "date_range", "card_id": '$Q03', "target": ["dimension", ["field", "event_date", {"base-type": "type/Date"}], {"stage-number": 0}]}]},
      {"id": -4, "card_id": '$Q04', "row": 16, "col": 0, "size_x": 12, "size_y": 8, "parameter_mappings": [{"parameter_id": "date_range", "card_id": '$Q04', "target": ["dimension", ["field", "event_date", {"base-type": "type/Date"}], {"stage-number": 0}]}, {"parameter_id": "popup_version", "card_id": '$Q04', "target": ["dimension", ["field", "popup_version", {"base-type": "type/Text"}], {"stage-number": 0}]}]},
      {"id": -5, "card_id": '$Q05', "row": 16, "col": 12, "size_x": 12, "size_y": 8, "parameter_mappings": [{"parameter_id": "date_range", "card_id": '$Q05', "target": ["dimension", ["field", "event_date", {"base-type": "type/Date"}], {"stage-number": 0}]}]}
    ]
  }'

echo ""
echo "✓ 完成!"
echo "Dashboard: https://kmb.qunhequnhe.com/dashboard/621"
