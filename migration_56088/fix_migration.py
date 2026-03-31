#!/usr/bin/env python3
"""修复迁移 - 创建Questions并关联到Dashboard"""

import json
import urllib.request
import urllib.error

API_HOST = "https://kmb.qunhequnhe.com"
API_KEY = "mb_h5ddq58TgNTAZsV7e81myvAxMlMcqXWrx1y9TdqArl8="
COLLECTION_ID = 564
DATABASE_ID = 4
MODEL_ID = 13371409
DASHBOARD_ID = 621

def api_call(method, path, payload=None):
    url = f"{API_HOST}{path}"
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    data = json.dumps(payload).encode('utf-8') if payload else None

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        print(f"HTTP Error {e.code}: {body}")
        raise

# 创建 Questions
questions = [
    {
        "name": "【56088】每日打开弹窗UV",
        "collection_id": COLLECTION_ID,
        "display": "line",
        "dataset_query": {
            "database": DATABASE_ID,
            "query": {
                "source-table": f"card__{MODEL_ID}",
                "aggregation": [["aggregation-options", ["distinct", ["field", "userid", {"base-type": "type/Text"}]], {"name": "打开弹窗UV", "display-name": "打开弹窗UV"}]],
                "breakout": [["field", "event_date", {"base-type": "type/Date", "temporal-unit": "day"}]]
            },
            "type": "query"
        }
    },
    {
        "name": "【56088】每日支付成功UV",
        "collection_id": COLLECTION_ID,
        "display": "line",
        "dataset_query": {
            "database": DATABASE_ID,
            "query": {
                "source-table": f"card__{MODEL_ID}",
                "aggregation": [["aggregation-options", ["distinct", ["case", [[["=", ["field", "event_type", {"base-type": "type/Text"}], "pay.success"], ["field", "userid", {"base-type": "type/Text"}]]]]], {"name": "支付成功UV", "display-name": "支付成功UV"}]],
                "breakout": [["field", "event_date", {"base-type": "type/Date", "temporal-unit": "day"}]]
            },
            "type": "query"
        }
    },
    {
        "name": "【56088】每日支付金额",
        "collection_id": COLLECTION_ID,
        "display": "line",
        "dataset_query": {
            "database": DATABASE_ID,
            "query": {
                "source-table": f"card__{MODEL_ID}",
                "aggregation": [["aggregation-options", ["sum", ["field", "amount_usd", {"base-type": "type/Float"}]], {"name": "支付金额", "display-name": "支付金额(USD)"}]],
                "breakout": [["field", "event_date", {"base-type": "type/Date", "temporal-unit": "day"}]]
            },
            "type": "query"
        }
    },
    {
        "name": "【56088】弹窗版本对比",
        "collection_id": COLLECTION_ID,
        "display": "line",
        "dataset_query": {
            "database": DATABASE_ID,
            "query": {
                "source-table": f"card__{MODEL_ID}",
                "aggregation": [["aggregation-options", ["distinct", ["field", "userid", {"base-type": "type/Text"}]], {"name": "UV", "display-name": "UV"}]],
                "breakout": [
                    ["field", "event_date", {"base-type": "type/Date", "temporal-unit": "day"}],
                    ["field", "popup_version", {"base-type": "type/Text"}]
                ]
            },
            "type": "query"
        }
    },
    {
        "name": "【56088】用户付费分层",
        "collection_id": COLLECTION_ID,
        "display": "line",
        "dataset_query": {
            "database": DATABASE_ID,
            "query": {
                "source-table": f"card__{MODEL_ID}",
                "aggregation": [["aggregation-options", ["distinct", ["field", "userid", {"base-type": "type/Text"}]], {"name": "UV", "display-name": "UV"}]],
                "breakout": [
                    ["field", "event_date", {"base-type": "type/Date", "temporal-unit": "day"}],
                    ["field", "user_paid_level", {"base-type": "type/Text"}]
                ]
            },
            "type": "query"
        }
    }
]

print("创建 Questions...")
question_ids = []
for i, q in enumerate(questions, 1):
    print(f"  创建 Question {i}: {q['name']}...")
    try:
        resp = api_call("POST", "/api/card", q)
        qid = resp.get('id')
        question_ids.append(qid)
        print(f"    ✓ ID={qid}")
    except Exception as e:
        print(f"    ✗ 失败: {e}")
        question_ids.append(None)

print(f"\n创建完成: {question_ids}")

# 更新Dashboard卡片
print("\n更新 Dashboard 卡片...")
dashcards = [
    {"id": -1, "card_id": question_ids[0], "row": 0, "col": 0, "size_x": 12, "size_y": 8, "parameter_mappings": [{"parameter_id": "date_range", "card_id": question_ids[0], "target": ["dimension", ["field", "event_date", {"base-type": "type/Date"}], {"stage-number": 0}]}]},
    {"id": -2, "card_id": question_ids[1], "row": 0, "col": 12, "size_x": 12, "size_y": 8, "parameter_mappings": [{"parameter_id": "date_range", "card_id": question_ids[1], "target": ["dimension", ["field", "event_date", {"base-type": "type/Date"}], {"stage-number": 0}]}]},
    {"id": -3, "card_id": question_ids[2], "row": 8, "col": 0, "size_x": 24, "size_y": 8, "parameter_mappings": [{"parameter_id": "date_range", "card_id": question_ids[2], "target": ["dimension", ["field", "event_date", {"base-type": "type/Date"}], {"stage-number": 0}]}]},
    {"id": -4, "card_id": question_ids[3], "row": 16, "col": 0, "size_x": 12, "size_y": 8, "parameter_mappings": [{"parameter_id": "date_range", "card_id": question_ids[3], "target": ["dimension", ["field", "event_date", {"base-type": "type/Date"}], {"stage-number": 0}]}, {"parameter_id": "popup_version", "card_id": question_ids[3], "target": ["dimension", ["field", "popup_version", {"base-type": "type/Text"}], {"stage-number": 0}]}]},
    {"id": -5, "card_id": question_ids[4], "row": 16, "col": 12, "size_x": 12, "size_y": 8, "parameter_mappings": [{"parameter_id": "date_range", "card_id": question_ids[4], "target": ["dimension", ["field", "event_date", {"base-type": "type/Date"}], {"stage-number": 0}]}]}
]

try:
    api_call("PUT", f"/api/dashboard/{DASHBOARD_ID}", {"dashcards": dashcards})
    print("  ✓ Dashboard 更新完成")
except Exception as e:
    print(f"  ✗ 失败: {e}")

# 保存资产映射
with open('asset_mapping.json', 'w') as f:
    json.dump({
        "page_id": 56088,
        "page_name": "新版实验 - 支付弹窗转化",
        "collection_id": COLLECTION_ID,
        "model_id": MODEL_ID,
        "question_ids": question_ids,
        "dashboard_id": DASHBOARD_ID,
        "dashboard_url": f"{API_HOST}/dashboard/{DASHBOARD_ID}"
    }, f, indent=2)

print("\n✓ 迁移完成!")
print(f"Dashboard: {API_HOST}/dashboard/{DASHBOARD_ID}")
