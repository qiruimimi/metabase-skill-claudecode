import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import generate_dashboard139_report as report
from core.errors import KMBError


class GenerateDashboardReportTests(unittest.TestCase):
    def test_query_card_calls_post_json(self):
        expected = {"row_count": 10}
        with patch("generate_dashboard139_report.post_json", return_value=expected) as mocked:
            result = report.query_card(1724, 200)

        self.assertEqual(result, expected)
        mocked.assert_called_once_with(
            "/api/card/1724/query",
            {"parameters": [], "constraints": {"max-results": 200}},
        )

    def test_generate_report_marks_failed_card_when_exception(self):
        def side_effect(card_id):
            if card_id == report.CARD_IDS["keywords"]:
                raise KMBError("failed")
            return {"row_count": 1}

        with patch("generate_dashboard139_report.query_card", side_effect=side_effect):
            text = report.generate_report("2026-03-25")

        self.assertIn("# Dashboard 139 日报 - 2026-03-25", text)
        self.assertIn("查询失败", text)


if __name__ == "__main__":
    unittest.main()
