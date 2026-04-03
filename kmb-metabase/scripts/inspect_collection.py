#!/usr/bin/env python3
"""
Inspect a KMB collection and summarize card/dashboard structure.

Usage:
    python3 inspect_collection.py 114
    python3 inspect_collection.py 31 --json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

from kmb import get_json, format_error


def _summarize_card(card: dict, listed_model: str) -> dict:
    dataset_query = card.get("dataset_query", {})
    query = dataset_query.get("query", {}) or {}
    native = dataset_query.get("native", {}) or {}
    query_type = dataset_query.get("type", "unknown")
    source_table = query.get("source-table")

    return {
        "id": card.get("id"),
        "name": card.get("name"),
        "listed_model": listed_model,
        "query_type": query_type,
        "display": card.get("display"),
        "is_dataset_item": listed_model == "dataset",
        "source_table": source_table,
        "source_table_kind": (
            "card__id" if isinstance(source_table, str) and source_table.startswith("card__") else
            "table" if source_table else
            None
        ),
        "has_source_query": bool(query.get("source-query")),
        "has_joins": bool(query.get("joins")),
        "has_expressions": bool(query.get("expressions")),
        "has_template_tags": bool(native.get("template-tags")),
    }


def inspect_collection(collection_id: int) -> dict:
    collection = get_json(f"/api/collection/{collection_id}")
    items = get_json(f"/api/collection/{collection_id}/items").get("data", [])

    item_counts = Counter(item.get("model", "unknown") for item in items)
    card_summaries = []
    dashboard_summaries = []

    card_query_types = Counter()
    display_types = Counter()
    source_patterns = Counter()
    query_features = Counter()
    dashboard_param_types = Counter()
    dashboard_mapping_target_types = Counter()
    text_dashcards = 0

    for item in items:
        model = item.get("model")
        if model in {"card", "dataset"}:
            card = get_json(f"/api/card/{item['id']}")
            summary = _summarize_card(card, model)
            card_summaries.append(summary)

            card_query_types[summary["query_type"]] += 1
            display_types[summary["display"] or "none"] += 1

            if summary["source_table_kind"]:
                source_patterns[summary["source_table_kind"]] += 1
            if summary["has_source_query"]:
                query_features["source-query"] += 1
            if summary["has_joins"]:
                query_features["joins"] += 1
            if summary["has_expressions"]:
                query_features["expressions"] += 1
            if summary["has_template_tags"]:
                query_features["template-tags"] += 1

        elif model == "dashboard":
            dashboard = get_json(f"/api/dashboard/{item['id']}")
            dashcards = dashboard.get("dashcards", [])
            parameters = dashboard.get("parameters", [])

            for parameter in parameters:
                dashboard_param_types[parameter.get("type") or "unknown"] += 1

            for dashcard in dashcards:
                if dashcard.get("card_id") is None:
                    text_dashcards += 1
                for mapping in dashcard.get("parameter_mappings", []):
                    target = mapping.get("target", [])
                    dashboard_mapping_target_types[target[0] if target else "unknown"] += 1

            dashboard_summaries.append(
                {
                    "id": dashboard.get("id"),
                    "name": dashboard.get("name"),
                    "dashcards": len(dashcards),
                    "parameter_count": len(parameters),
                    "has_text_dashcards": any(d.get("card_id") is None for d in dashcards),
                }
            )

    return {
        "collection": {
            "id": collection.get("id"),
            "name": collection.get("name"),
            "location": collection.get("location"),
        },
        "item_counts": dict(item_counts),
        "card_query_types": dict(card_query_types),
        "display_types": dict(display_types),
        "source_patterns": dict(source_patterns),
        "query_features": dict(query_features),
        "dashboard_param_types": dict(dashboard_param_types),
        "dashboard_mapping_target_types": dict(dashboard_mapping_target_types),
        "text_dashcards": text_dashcards,
        "cards": card_summaries,
        "dashboards": dashboard_summaries,
    }


def main():
    parser = argparse.ArgumentParser(description="Inspect KMB collection structure")
    parser.add_argument("collection_id", type=int, help="Collection ID")
    parser.add_argument("--json", action="store_true", help="Output raw JSON summary")
    args = parser.parse_args()

    try:
        summary = inspect_collection(args.collection_id)
    except Exception as error:
        print(f"❌ Failed to inspect collection: {format_error(error)}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return

    collection = summary["collection"]
    print(f"Collection: {collection['name']} (ID: {collection['id']})")
    print(f"Location: {collection['location']}")
    print("-" * 40)
    print(f"Item counts: {json.dumps(summary['item_counts'], ensure_ascii=False)}")
    print(f"Card query types: {json.dumps(summary['card_query_types'], ensure_ascii=False)}")
    print(f"Display types: {json.dumps(summary['display_types'], ensure_ascii=False)}")
    print(f"Source patterns: {json.dumps(summary['source_patterns'], ensure_ascii=False)}")
    print(f"Query features: {json.dumps(summary['query_features'], ensure_ascii=False)}")
    print(f"Dashboard parameter types: {json.dumps(summary['dashboard_param_types'], ensure_ascii=False)}")
    print(
        "Dashboard mapping target types: "
        f"{json.dumps(summary['dashboard_mapping_target_types'], ensure_ascii=False)}"
    )
    print(f"Text dashcards: {summary['text_dashcards']}")

    if summary["cards"]:
        print("\nSample cards:")
        for card in summary["cards"][:10]:
            print(
                f"  [{card['id']}] {card['name']} | {card['query_type']} | "
                f"display={card['display']} | source={card['source_table'] or '-'}"
            )

    if summary["dashboards"]:
        print("\nDashboards:")
        for dashboard in summary["dashboards"]:
            print(
                f"  [{dashboard['id']}] {dashboard['name']} | "
                f"dashcards={dashboard['dashcards']} | "
                f"parameters={dashboard['parameter_count']} | "
                f"text_blocks={dashboard['has_text_dashcards']}"
            )


if __name__ == "__main__":
    main()
