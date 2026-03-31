#!/usr/bin/env python3
"""
Dashboard Creator for Metabase

Creates new Dashboards.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "scripts" / "lib"))

from kmb import post_json, format_error


def create_dashboard(name: str, collection_id: int, description: str = None, parameters: list = None):
    """Create a new Metabase Dashboard."""
    payload = {
        "name": name,
        "collection_id": collection_id
    }

    if description:
        payload["description"] = description

    if parameters:
        payload["parameters"] = parameters

    try:
        result = post_json("/api/dashboard", payload)
        return result
    except Exception as e:
        print(f"Error creating dashboard: {format_error(e)}", file=sys.stderr)
        raise


def main():
    parser = argparse.ArgumentParser(description="Create Metabase Dashboard")
    parser.add_argument("--name", required=True, help="Dashboard name")
    parser.add_argument("--collection", type=int, required=True, help="Collection ID")
    parser.add_argument("--description", help="Dashboard description")
    parser.add_argument("--parameters-file", help="Parameters config JSON file")

    args = parser.parse_args()

    parameters = None
    if args.parameters_file:
        with open(args.parameters_file) as f:
            parameters = json.load(f)

    print(f"Creating Dashboard: {args.name}")
    print(f"Collection: {args.collection}")
    print("-" * 40)

    try:
        result = create_dashboard(
            name=args.name,
            collection_id=args.collection,
            description=args.description,
            parameters=parameters
        )

        dashboard_id = result.get("id")

        print(f"\n✅ Dashboard created successfully!")
        print(f"ID: {dashboard_id}")
        print(f"Name: {result.get('name')}")
        print(f"Collection ID: {result.get('collection_id')}")

        output = {
            "id": dashboard_id,
            "name": result.get("name"),
            "collection_id": result.get("collection_id"),
            "status": "created"
        }
        print(f"\n{json.dumps(output, indent=2)}")

    except Exception as e:
        print(f"\n❌ Failed to create dashboard: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
