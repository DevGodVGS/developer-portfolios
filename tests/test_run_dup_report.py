import os
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src import run_dup_report


class TestRunDupReport(unittest.TestCase):
    def test_main_with_duplicates(self):
        sample = (
            "# Portfolios\n"
            "- [Alice](https://example.com)\n"
            "- [Bob](https://example.com/)\n"  # Duplicate URL
            "- [Carol](https://carol.dev)\n"
        )
        with tempfile.TemporaryDirectory() as td:
            cwd = os.getcwd()
            try:
                os.chdir(td)
                with open("README.md", "w", encoding="utf-8") as f:
                    f.write(sample)

                with patch("sys.stdout") as mock_stdout:
                    exit_code = run_dup_report.main()
                    self.assertEqual(exit_code, 0)
            finally:
                os.chdir(cwd)

    def test_main_readme_not_found(self):
        with tempfile.TemporaryDirectory() as td:
            cwd = os.getcwd()
            try:
                os.chdir(td)
                with patch("sys.stderr"):
                    exit_code = run_dup_report.main()
                    self.assertEqual(exit_code, 2)
            finally:
                os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()
