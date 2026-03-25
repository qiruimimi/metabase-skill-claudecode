#!/usr/bin/env python3
"""
Dashboard 139 报告生成器

生成 GA投放词分析的每日报告。
"""

import argparse
import json
import sys
import os
from datetime import datetime, timedelta
from urllib.request import Request, urlopen
from urllib.error import HTTPError

API_HOST = "https://kmb.qunhequnhe.com"
API_KEY = "mb_h5ddq58TgNTAZsV7e81myvAxMlMcqXWrx1y9TdqArl8="

# Dashboard 139 核心 Cards
CARD_IDS = {
    'keywords': 1724,      # 投放词列表
    'campaigns': 1726,     # Campaign列表
    'ltv_cac': 1732,       # LTV/CAC
    'roas_7d': 1731,       # ROAS 7天
    'roas_180d': 1750,     # ROAS 180天
}


def query_card(card_id: int, limit: int = 10000):
    """查询 Card 数据"""
    url = f"{API_HOST}/api/card/{card_id}/query"
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "parameters": [],
        "constraints": {"max-results": limit}
    }).encode('utf-8')

    req = Request(url, data=data, headers=headers, method='POST')

    try:
        with urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except HTTPError as e:
        print(f"Error querying card {card_id}: HTTP {e.code}", file=sys.stderr)
        return None


def generate_report(date_str: str = None):
    """生成报告"""
    if date_str is None:
        date_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    report_lines = [
        f"# Dashboard 139 日报 - {date_str}",
        "",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 数据概览",
        "",
    ]

    # 查询各 Card 数据
    for name, card_id in CARD_IDS.items():
        result = query_card(card_id)
        if result:
            row_count = result.get('row_count', 0)
            report_lines.append(f"- **{name}** (Card {card_id}): {row_count} 条数据")
        else:
            report_lines.append(f"- **{name}** (Card {card_id}): 查询失败")

    report_lines.extend([
        "",
        "## 详细数据",
        "",
        "(详细数据分析待补充)",
        "",
        "---",
        "",
        "*报告由 KMB Skill 自动生成*",
    ])

    return "\n".join(report_lines)


def main():
    parser = argparse.ArgumentParser(description='Dashboard 139 报告生成器')
    parser.add_argument('--date', help='报告日期 (YYYY-MM-DD)，默认昨天')
    parser.add_argument('--output', '-o', help='输出文件路径')

    args = parser.parse_args()

    # 生成报告
    report = generate_report(args.date)

    # 输出
    if args.output:
        os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"报告已保存到: {args.output}")
    else:
        print(report)


if __name__ == '__main__':
    main()
