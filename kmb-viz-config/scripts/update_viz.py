#!/usr/bin/env python3
"""
Visualization Configurator for Metabase

Updates card visualization settings.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "kmb-metabase" / "scripts" / "lib"))

from kmb import get_json, put_json, format_error


def update_visualization(card_id: int, viz_settings: dict):
    """Update card visualization settings."""
    # First get current card to preserve other fields
    try:
        card = get_json(f"/api/card/{card_id}")
    except Exception as e:
        print(f"Error getting card {card_id}: {format_error(e)}", file=sys.stderr)
        raise

    # Update only visualization_settings
    payload = {
        "visualization_settings": viz_settings
    }

    try:
        result = put_json(f"/api/card/{card_id}", payload)
        return result
    except Exception as e:
        print(f"Error updating visualization: {format_error(e)}", file=sys.stderr)
        raise


def build_viz_config(
    display: str,
    dimensions: list,
    metrics: list,
    series_settings: dict = None,
    column_settings: dict = None
) -> dict:
    """Build visualization config."""
    config = {
        "display": display,
        "graph.dimensions": dimensions,
        "graph.metrics": metrics
    }

    if series_settings:
        config["series_settings"] = series_settings
    else:
        # Auto-generate empty series_settings for each metric
        config["series_settings"] = {m: {} for m in metrics}

    if column_settings:
        config["column_settings"] = column_settings

    return config


def main():
    parser = argparse.ArgumentParser(description="Update Metabase visualization settings")
    parser.add_argument("--card-id", type=int, required=True, help="Card ID")
    parser.add_argument("--config-file", help="Visualization config JSON file")
    parser.add_argument("--display", choices=["line", "bar", "pie", "table", "scalar"],
                        help="Chart type")
    parser.add_argument("--dimensions", help="Dimensions JSON array")
    parser.add_argument("--metrics", help="Metrics JSON array")
    parser.add_argument("--series-settings", help="Series settings JSON file")

    args = parser.parse_args()

    # Get config
    if args.config_file:
        with open(args.config_file) as f:
            viz_config = json.load(f)
    else:
        if not args.display or not args.dimensions or not args.metrics:
            print("Error: Provide --config-file or all of --display, --dimensions, --metrics",
                  file=sys.stderr)
            sys.exit(1)

        dimensions = json.loads(args.dimensions)
        metrics = json.loads(args.metrics)

        series_settings = None
        if args.series_settings:
            with open(args.series_settings) as f:
                series_settings = json.load(f)

        viz_config = build_viz_config(
            display=args.display,
            dimensions=dimensions,
            metrics=metrics,
            series_settings=series_settings
        )

    # Update visualization
    print(f"Updating visualization for card {args.card_id}")
    print(f"Config: {json.dumps(viz_config, indent=2, ensure_ascii=False)}")
    print("-" * 40)

    try:
        result = update_visualization(args.card_id, viz_config)
        print(f"\n✅ Visualization updated successfully!")
        print(f"Card ID: {args.card_id}")

    except Exception as e:
        print(f"\n❌ Failed to update visualization: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
