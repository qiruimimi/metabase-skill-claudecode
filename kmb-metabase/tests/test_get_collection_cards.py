import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import get_collection_cards
from core.errors import KMBError


class GetCollectionCardsTests(unittest.TestCase):
    def test_get_collection_items_calls_get_json(self):
        expected = {"data": []}
        with patch("get_collection_cards.get_json", return_value=expected) as mocked:
            result = get_collection_cards.get_collection_items(396)

        self.assertEqual(result, expected)
        mocked.assert_called_once_with("/api/collection/396/items")

    def test_get_collection_info_returns_none_when_error(self):
        with patch("get_collection_cards.get_json", side_effect=KMBError("boom")):
            result = get_collection_cards.get_collection_info(396)

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
