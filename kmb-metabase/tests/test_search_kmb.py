import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import search_kmb


class SearchKmbTests(unittest.TestCase):
    def test_search_kmb_calls_get_json(self):
        expected = {"total": 0, "data": []}
        with patch("search_kmb.get_json", return_value=expected) as mocked:
            result = search_kmb.search_kmb("转化")

        self.assertEqual(result, expected)
        mocked.assert_called_once_with("/api/search", {"q": "转化"})

    def test_format_results_groups_by_model(self):
        payload = {
            "total": 2,
            "data": [
                {"model": "card", "id": 1, "name": "A"},
                {"model": "dashboard", "id": 2, "name": "B"},
            ],
        }

        stream = io.StringIO()
        with patch("sys.stdout", stream):
            search_kmb.format_results(payload)

        output = stream.getvalue()
        self.assertIn("找到 2 个结果", output)
        self.assertIn("【CARD】", output)
        self.assertIn("【DASHBOARD】", output)


if __name__ == "__main__":
    unittest.main()
