import ast
from pathlib import Path
import unittest

DASHBOARD_ENDPOINT = Path(__file__).resolve().parents[1] / "app" / "api" / "v1" / "endpoints" / "dashboard.py"


class DashboardSyntaxTest(unittest.TestCase):
    def test_dashboard_response_calls_do_not_repeat_keywords(self):
        tree = ast.parse(DASHBOARD_ENDPOINT.read_text())
        duplicate_keywords = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if not isinstance(node.func, ast.Name) or node.func.id != "DashboardResponse":
                continue

            seen = set()
            for keyword in node.keywords:
                # **kwargs are represented with arg=None; this endpoint uses explicit args.
                if keyword.arg is None:
                    continue
                if keyword.arg in seen:
                    duplicate_keywords.append((keyword.arg, keyword.lineno))
                seen.add(keyword.arg)

        self.assertEqual([], duplicate_keywords)


if __name__ == "__main__":
    unittest.main()
