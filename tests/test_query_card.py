import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import query_card


class QueryCardTests(unittest.TestCase):
    def test_query_card_calls_post_json(self):
        expected = {"ok": True}
        with patch("query_card.post_json", return_value=expected) as mocked:
            result = query_card.query_card(3267, 100)

        self.assertEqual(result, expected)
        mocked.assert_called_once_with(
            "/api/card/3267/query",
            {"parameters": [], "constraints": {"max-results": 100}},
        )

    def test_format_as_csv_outputs_header_and_rows(self):
        payload = {
            "data": {
                "cols": [{"name": "name"}, {"name": "count"}],
                "rows": [["A", 1], ["B", 2]],
            }
        }

        stream = io.StringIO()
        with patch("sys.stdout", stream):
            query_card.format_as_csv(payload)

        output = stream.getvalue()
        self.assertIn("name,count", output)
        self.assertIn("A,1", output)
        self.assertIn("B,2", output)


if __name__ == "__main__":
    unittest.main()
