#!/usr/bin/env python3
"""
Dashboard Cards Adder for Metabase

Adds/updates cards in a Dashboard using PUT /api/dashboard/:id
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "kmb-metabase" / "scripts" / "lib"))

from kmb import get_json, put_json, format_error


def add_cards(dashboard_id: int, cards_config: list):
    """Add cards to dashboard using PUT method."""
    # Get current dashboard
    try:
        dashboard = get_json(f"/api/dashboard/{dashboard_id}")
    except Exception as e:
        print(f"Error getting dashboard {dashboard_id}: {format_error(e)}", file=sys.stderr)
        raise

    # Build dashcards array
    # Keep existing cards (with positive IDs) and add new ones (with negative IDs)
    existing_cards = [c for c in dashboard.get("dashcards", []) if c.get("id", 0) > 0]

    # Prepare new cards
    new_cards = []
    for i, card in enumerate(cards_config):
        new_card = {
            "id": card.get("id", -(i + 1)),  # Use negative ID for new cards
            "card_id": card["card_id"],
            "row": card.get("row", 0),
            "col": card.get("col", 0),
            "size_x": card.get("size_x", 12),
            "size_y": card.get("size_y", 8),
            "parameter_mappings": card.get("parameter_mappings", [])
        }
        new_cards.append(new_card)

    # Combine existing and new cards
    all_cards = existing_cards + new_cards

    # PUT update
    payload = {
        "dashcards": all_cards
    }

    try:
        result = put_json(f"/api/dashboard/{dashboard_id}", payload)
        return result, len(new_cards)
    except Exception as e:
        print(f"Error adding cards: {format_error(e)}", file=sys.stderr)
        raise


def main():
    parser = argparse.ArgumentParser(description="Add cards to Metabase Dashboard")
    parser.add_argument("--dashboard-id", type=int, required=True, help="Dashboard ID")
    parser.add_argument("--config-file", required=True, help="Cards config JSON file")

    args = parser.parse_args()

    # Load cards config
    with open(args.config_file) as f:
        cards_config = json.load(f)

    print(f"Adding cards to Dashboard {args.dashboard_id}")
    print(f"Cards to add: {len(cards_config)}")
    print("-" * 40)

    try:
        result, added_count = add_cards(args.dashboard_id, cards_config)

        print(f"\n✅ Cards added successfully!")
        print(f"Added: {added_count} cards")
        print(f"Total cards in dashboard: {len(result.get('dashcards', []))}")

        # Show summary
        print("\nCards layout:")
        for card in result.get("dashcards", []):
            card_id = card.get("card_id")
            row = card.get("row")
            col = card.get("col")
            size_x = card.get("size_x")
            size_y = card.get("size_y")
            print(f"  Card {card_id}: row={row}, col={col}, size={size_x}x{size_y}")

    except Exception as e:
        print(f"\n❌ Failed to add cards: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
