import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import space_sql_mapper


class SpaceSqlMapperTests(unittest.TestCase):
    def test_search_pages_is_case_insensitive(self):
        page_map = {
            "1": {"path": "Root/Weekly", "pageName": "Weekly Data"},
            "2": {"path": "Root/Daily", "pageName": "Daily Data"},
        }

        results = space_sql_mapper.search_pages(page_map, "weekly")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["pageName"], "Weekly Data")

    def test_show_sql_only_exits_when_missing_graph(self):
        stderr = io.StringIO()
        with patch("sys.stderr", stderr):
            with self.assertRaises(SystemExit) as ctx:
                space_sql_mapper.show_sql_only("999", {})

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("图表 999 不存在", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
