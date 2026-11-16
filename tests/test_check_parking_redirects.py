import os
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src import check_parking_redirects


class TestCheckParkingRedirects(unittest.TestCase):
    def test_is_parking_domain(self):
        self.assertTrue(check_parking_redirects._is_parking_domain("http://sedoparking.com"))
        self.assertTrue(check_parking_redirects._is_parking_domain("https://sub.dan.com"))
        self.assertFalse(check_parking_redirects._is_parking_domain("https://github.com"))
        self.assertFalse(check_parking_redirects._is_parking_domain("https://example.com"))

    def test_has_gambling_title(self):
        html_spam = "<html><head><title>Situs Slot Gacor Hari Ini</title></head><body></body></html>"
        matched, phrase = check_parking_redirects._has_gambling_title(html_spam)
        self.assertTrue(matched)
        self.assertIn("slot gacor", phrase)

        html_clean = "<html><head><title>John Doe - Portfolio</title></head><body></body></html>"
        matched, phrase = check_parking_redirects._has_gambling_title(html_clean)
        self.assertFalse(matched)
        self.assertEqual(phrase, "")

    def test_has_parking_content(self):
        text_parked = "Welcome! This domain is for sale. Buy this domain now."
        matched, phrase = check_parking_redirects._has_parking_content(text_parked)
        self.assertTrue(matched)

        text_clean = "Welcome to my software engineering portfolio."
        matched, phrase = check_parking_redirects._has_parking_content(text_clean)
        self.assertFalse(matched)

    def test_build_markdown_empty(self):
        self.assertEqual(check_parking_redirects.build_markdown([]), "")

    def test_build_markdown_flagged(self):
        flagged = [{
            "line_idx": 4,
            "name": "Jane | Dev",
            "url": "https://parked-domain.com",
            "reason": "HEAD redirects to parking domain: sedoparking.com"
        }]
        md = check_parking_redirects.build_markdown(flagged)
        self.assertIn("## Ad/Parking Redirect Report", md)
        self.assertIn("Jane \\| Dev", md)
        self.assertIn("https://parked-domain.com", md)
        self.assertIn("Line", md)

    def test_main_no_flagged_removes_or_skips_output_file(self):
        with tempfile.TemporaryDirectory() as td:
            readme_path = os.path.join(td, "README.md")
            output_path = os.path.join(td, "parking-report.md")

            with open(readme_path, "w", encoding="utf-8") as f:
                f.write("- [John](https://example.com)\n")

            # Create a pre-existing dummy report to test cleanup
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("old report content")

            with patch.object(check_parking_redirects, "scan", return_value=[]):
                code = check_parking_redirects.main(["--readme", readme_path, "--output", output_path])
                self.assertEqual(code, 0)
                # Output file should be removed when there are no flagged items
                self.assertFalse(os.path.exists(output_path))


if __name__ == "__main__":
    unittest.main()
