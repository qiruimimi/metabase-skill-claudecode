#!/usr/bin/env python3
"""
Question Builder for Metabase

Creates MBQL Questions from Model.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "scripts" / "lib"))

from kmb import post_json, format_error


def create_question(
    name: str,
    model_id: int,
    breakout: list,
    aggregation: list,
    collection_id: int,
    database_id: int = 4,
    filters: list = None
):
    """Create a Metabase MBQL Question."""
    query = {
        "source-table": f"card__{model_id}",
        "breakout": breakout,
        "aggregation": aggregation
    }

    if filters:
        query["filter"] = filters

    payload = {
        "type": "question",
        "name": name,
        "collection_id": collection_id,
        "dataset_query": {
            "type": "query",
            "database": database_id,
            "query": query
        }
    }

    try:
        result = post_json("/api/card", payload)
        return result
    except Exception as e:
        print(f"Error creating question: {format_error(e)}", file=sys.stderr)
        raise


def parse_breakout(breakout_str: str) -> list:
    """Parse breakout string to MBQL format."""
    # Simple parsing: "field_name" -> ["field", "field_name"]
    # With temporal: "created_date:day" -> ["field", "created_date", {"temporal-unit": "day"}]
    if ":" in breakout_str:
        field, unit = breakout_str.split(":")
        return [["field", field.strip(), {"temporal-unit": unit.strip()}]]
    return [["field", breakout_str.strip()]]


def parse_aggregation(agg_str: str, agg_name: str = None) -> list:
    """Parse aggregation string to MBQL format."""
    # Format: "distinct field_name" or "sum field_name" or "count"
    parts = agg_str.split()
    func = parts[0].lower()

    if func == "count" and len(parts) == 1:
        inner = ["count"]
    elif func == "distinct" and len(parts) > 1:
        inner = ["distinct", ["field", parts[1]]]
    elif func in ["sum", "avg", "min", "max"] and len(parts) > 1:
        inner = [func, ["field", parts[1]]]
    else:
        raise ValueError(f"Unsupported aggregation: {agg_str}")

    name = agg_name or f"{func}_{parts[1] if len(parts) > 1 else 'count'}"
    return [["aggregation-options", inner, {"name": name, "display-name": name}]]


def main():
    parser = argparse.ArgumentParser(description="Create Metabase MBQL Question")
    parser.add_argument("--name", required=True, help="Question name")
    parser.add_argument("--model-id", type=int, required=True, help="Model ID")
    parser.add_argument("--config-file", help="Question config JSON")
    parser.add_argument("--breakout", help="Breakout field (e.g., 'created_date:day')")
    parser.add_argument("--aggregation", help="Aggregation (e.g., 'distinct user_id')")
    parser.add_argument("--collection", type=int, required=True, help="Collection ID")
    parser.add_argument("--database", type=int, default=4, help="Database ID")

    args = parser.parse_args()

    # Get config
    if args.config_file:
        with open(args.config_file) as f:
            config = json.load(f)
        breakout = config.get("breakout", [])
        aggregation = config.get("aggregation", [])
        name = config.get("name", args.name)
        filters = config.get("filter")
    else:
        if not args.breakout or not args.aggregation:
            print("Error: Provide --config-file or both --breakout and --aggregation", file=sys.stderr)
            sys.exit(1)
        breakout = parse_breakout(args.breakout)
        aggregation = parse_aggregation(args.aggregation, args.name)
        name = args.name
        filters = None

    # Create question
    print(f"Creating Question: {name}")
    print(f"Model ID: {args.model_id}")
    print(f"Collection: {args.collection}")
    print("-" * 40)

    try:
        result = create_question(
            name=name,
            model_id=args.model_id,
            breakout=breakout,
            aggregation=aggregation,
            collection_id=args.collection,
            database_id=args.database,
            filters=filters
        )
        question_id = result.get("id")

        print(f"\n✅ Question created successfully!")
        print(f"ID: {question_id}")
        print(f"Name: {result.get('name')}")

        output = {
            "id": question_id,
            "name": result.get("name"),
            "collection_id": result.get("collection_id"),
            "type": "question",
            "status": "created"
        }
        print(f"\n{json.dumps(output, indent=2)}")

    except Exception as e:
        print(f"\n❌ Failed to create question: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
