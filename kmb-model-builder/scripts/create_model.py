#!/usr/bin/env python3
"""
Model Builder for Metabase

Creates Metabase Model from SQL.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Add shared lib to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "kmb-metabase" / "scripts" / "lib"))

from kmb import post_json, format_error


S_TABLE_T_PLUS_ONE_PATTERNS = [
    re.compile(
        r"ds\s*=\s*date_format\s*\(\s*date_sub\s*\(\s*current_date\s*\(?\s*\)?\s*,\s*interval\s+1\s+day\s*\)\s*,\s*'%Y%m%d'\s*\)",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"ds\s*=\s*date_format\s*\(\s*current_date\s*\(?\s*\)?\s*-\s*interval\s+1\s+day\s*,\s*'%Y%m%d'\s*\)",
        re.IGNORECASE | re.DOTALL,
    ),
]


def extract_source_tables(sql: str) -> list[str]:
    return re.findall(r"\b(?:from|join)\s+([a-zA-Z0-9_.]+)", sql, re.IGNORECASE)


def validate_model_sql(sql: str) -> list[str]:
    errors: list[str] = []
    tables = extract_source_tables(sql)
    s_tables = [table for table in tables if table.lower().endswith("_s_d")]

    if not s_tables:
        return errors

    if not re.search(
        r"str_to_date\s*\(\s*ds\s*,\s*'%Y%m%d'\s*\)\s+as\s+ds_time\b",
        sql,
        re.IGNORECASE | re.DOTALL,
    ):
        errors.append(
            "S表 Model must expose `STR_TO_DATE(ds, '%Y%m%d') AS ds_time`."
        )

    if not any(pattern.search(sql) for pattern in S_TABLE_T_PLUS_ONE_PATTERNS):
        errors.append(
            "S表 Model must filter `ds` to the T+1 snapshot: "
            "DATE_FORMAT(DATE_SUB(CURRENT_DATE, INTERVAL 1 DAY), '%Y%m%d')."
        )

    return errors


def create_model(name: str, sql: str, collection_id: int, database_id: int = 4):
    """Create a Metabase Model."""
    payload = {
        "type": "model",
        "name": name,
        "collection_id": collection_id,
        "display": "table",
        "visualization_settings": {},
        "dataset_query": {
            "type": "native",
            "native": {
                "query": sql,
                "template-tags": {}
            },
            "database": database_id
        }
    }

    try:
        result = post_json("/api/card", payload)
        return result
    except Exception as e:
        print(f"Error creating model: {format_error(e)}", file=sys.stderr)
        raise


def verify_model(model_id: int):
    """Verify model can be queried."""
    from kmb import post_json
    try:
        result = post_json(f"/api/card/{model_id}/query", {})
        return True, result
    except Exception as e:
        return False, str(e)


def main():
    parser = argparse.ArgumentParser(description="Create Metabase Model")
    parser.add_argument("--name", required=True, help="Model name")
    parser.add_argument("--sql", help="SQL string")
    parser.add_argument("--sql-file", help="SQL file path")
    parser.add_argument("--config-file", help="Migration plan JSON from analyze_sql.py")
    parser.add_argument("--collection", type=int, required=True, help="Collection ID")
    parser.add_argument("--database", type=int, default=4, help="Database ID")
    parser.add_argument("--verify", action="store_true", help="Verify after creation")
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Run SQL preflight checks only, do not create the model",
    )

    args = parser.parse_args()

    # Get SQL
    if args.config_file:
        with open(args.config_file) as f:
            config = json.load(f)
        sql = config["model"]["sql"]
        name = args.name
    elif args.sql_file:
        with open(args.sql_file) as f:
            sql = f.read()
        name = args.name
    elif args.sql:
        sql = args.sql
        name = args.name
    else:
        print("Error: Provide --sql, --sql-file, or --config-file", file=sys.stderr)
        sys.exit(1)

    validation_errors = validate_model_sql(sql)
    if validation_errors:
        print("❌ Model SQL validation failed:", file=sys.stderr)
        for error in validation_errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)

    if args.validate_only:
        print("✅ Model SQL validation passed")
        sys.exit(0)

    # Create model
    print(f"Creating Model: {name}")
    print(f"Collection: {args.collection}")
    print(f"Database: {args.database}")
    print("-" * 40)

    try:
        result = create_model(name, sql, args.collection, args.database)
        model_id = result.get("id")

        print(f"\n✅ Model created successfully!")
        print(f"ID: {model_id}")
        print(f"Name: {result.get('name')}")
        print(f"Collection ID: {result.get('collection_id')}")

        # Verify
        if args.verify and model_id:
            print(f"\nVerifying model (ID: {model_id})...")
            ok, verify_result = verify_model(model_id)
            if ok:
                print("✅ Model query verification passed")
            else:
                print(f"❌ Model query verification failed: {verify_result}")

        # Output JSON
        output = {
            "id": model_id,
            "name": result.get("name"),
            "collection_id": result.get("collection_id"),
            "type": "model",
            "status": "created"
        }
        print(f"\n{json.dumps(output, indent=2)}")

    except Exception as e:
        print(f"\n❌ Failed to create model: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
