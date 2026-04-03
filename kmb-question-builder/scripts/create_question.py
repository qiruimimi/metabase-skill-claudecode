#!/usr/bin/env python3
"""
Question Builder for Metabase

Creates MBQL Questions from Model.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "kmb-metabase" / "scripts" / "lib"))

from kmb import post_json, format_error


def create_question(
    name: str,
    query_config: dict,
    collection_id: int,
    database_id: int = 4,
    display: str = "table",
    visualization_settings: dict | None = None,
    model_id: int | None = None,
    source_card_id: int | None = None,
):
    """Create a Metabase MBQL Question."""
    query = dict(query_config)

    if "source-table" not in query and "source-query" not in query:
        base_card_id = source_card_id or model_id
        if base_card_id is None:
            raise ValueError(
                "Question config must provide `source-table`/`source-query`, "
                "or pass --model-id / --source-card-id."
            )
        query["source-table"] = f"card__{base_card_id}"

    payload = {
        "type": "question",
        "name": name,
        "collection_id": collection_id,
        "display": display,
        "visualization_settings": visualization_settings or {},
        "dataset_query": {
            "type": "query",
            "database": database_id,
            "query": query
        },
    }

    try:
        result = post_json("/api/card", payload)
        return result
    except Exception as e:
        print(f"Error creating question: {format_error(e)}", file=sys.stderr)
        raise


def verify_question(question_id: int):
    """Verify question can be queried."""
    try:
        result = post_json(f"/api/card/{question_id}/query", {})
        return True, result
    except Exception as e:
        return False, str(e)


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


def normalize_query_config(config: dict, fallback_name: str) -> tuple[str, dict, str, dict]:
    """Normalize top-level or nested question config into a single query payload."""
    name = config.get("name", fallback_name)
    display = config.get("display", "table")
    visualization_settings = config.get("visualization_settings", {})

    if "query" in config:
        query = dict(config["query"])
    else:
        query_meta_keys = {"name", "display", "visualization_settings"}
        query = {key: value for key, value in config.items() if key not in query_meta_keys}

    return name, query, display, visualization_settings


def main():
    parser = argparse.ArgumentParser(description="Create Metabase MBQL Question")
    parser.add_argument("--name", required=True, help="Question name")
    parser.add_argument("--model-id", type=int, help="Model ID used as the default card__ source")
    parser.add_argument(
        "--source-card-id",
        type=int,
        help="Base card ID used as the default card__ source when building a derived MBQL question",
    )
    parser.add_argument("--config-file", help="Question config JSON")
    parser.add_argument("--breakout", help="Breakout field (e.g., 'created_date:day')")
    parser.add_argument("--aggregation", help="Aggregation (e.g., 'distinct user_id')")
    parser.add_argument("--collection", type=int, required=True, help="Collection ID")
    parser.add_argument("--database", type=int, default=4, help="Database ID")
    parser.add_argument("--verify", action="store_true", help="Verify after creation")

    args = parser.parse_args()

    # Get config
    if args.config_file:
        with open(args.config_file) as f:
            config = json.load(f)
        name, query_config, display, visualization_settings = normalize_query_config(config, args.name)
    else:
        if not args.breakout or not args.aggregation:
            print("Error: Provide --config-file or both --breakout and --aggregation", file=sys.stderr)
            sys.exit(1)
        name = args.name
        query_config = {
            "breakout": parse_breakout(args.breakout),
            "aggregation": parse_aggregation(args.aggregation, args.name),
        }
        display = "table"
        visualization_settings = {}

    # Create question
    print(f"Creating Question: {name}")
    if args.source_card_id:
        print(f"Source Card ID: {args.source_card_id}")
    elif args.model_id:
        print(f"Model ID: {args.model_id}")
    else:
        print("Source: query config")
    print(f"Collection: {args.collection}")
    print("-" * 40)

    try:
        result = create_question(
            name=name,
            query_config=query_config,
            collection_id=args.collection,
            database_id=args.database,
            display=display,
            visualization_settings=visualization_settings,
            model_id=args.model_id,
            source_card_id=args.source_card_id,
        )
        question_id = result.get("id")

        print(f"\n✅ Question created successfully!")
        print(f"ID: {question_id}")
        print(f"Name: {result.get('name')}")

        if args.verify and question_id:
            print(f"\nVerifying question (ID: {question_id})...")
            ok, verify_result = verify_question(question_id)
            if ok:
                print("✅ Question query verification passed")
            else:
                print(f"❌ Question query verification failed: {verify_result}")

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
