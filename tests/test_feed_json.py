#!/usr/bin/env python3
"""
Test the feed.json generation functionality
"""

import json
import os
import re
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src.alphabetical import extract_portfolio_data


class TestFeedJson(unittest.TestCase):
    def test_extract_portfolio_data(self):
        """Test portfolio data extraction from markdown lines"""
        test_lines = [
            "- [Alice Smith](https://alice.com) [Full Stack Developer]\n",
            "- [Bob Jones](https://bob.dev)\n",
            "- [Carol White](https://carol.io) [UI/UX Designer | Frontend Dev]\n",
            "## Some Header\n",
            "Not a portfolio line\n",
            "- [Dave Brown](https://dave.com) []\n",  # Empty tagline
            "- [Eve Adams](https://eve.com)\n",
            "  [Security Engineer]\n",  # Indented multiline tagline
        ]

        portfolios = extract_portfolio_data(test_lines)

        self.assertEqual(len(portfolios), 5)

        # Test first entry with tagline
        self.assertEqual(portfolios[0]['name'], "Alice Smith")
        self.assertEqual(portfolios[0]['url'], "https://alice.com")
        self.assertEqual(portfolios[0]['tagline'], "Full Stack Developer")

        # Test entry without tagline
        self.assertEqual(portfolios[1]['name'], "Bob Jones")
        self.assertEqual(portfolios[1]['url'], "https://bob.dev")
        self.assertNotIn('tagline', portfolios[1])

        # Test entry with complex tagline
        self.assertEqual(portfolios[2]['name'], "Carol White")
        self.assertEqual(portfolios[2]['tagline'], "UI/UX Designer | Frontend Dev")

        # Test entry with empty tagline (should not include tagline key)
        self.assertEqual(portfolios[3]['name'], "Dave Brown")
        self.assertNotIn('tagline', portfolios[3])

        # Test multiline tagline continuation
        self.assertEqual(portfolios[4]['name'], "Eve Adams")
        self.assertEqual(portfolios[4]['tagline'], "Security Engineer")

    def test_feed_json_structure(self):
        """Test that feed.json has valid structure"""
        feed_path = os.path.join(REPO_ROOT, 'feed.json')
        self.assertTrue(os.path.exists(feed_path), f"feed.json not found at {feed_path}")

        with open(feed_path, 'r', encoding='utf-8') as f:
            portfolios = json.load(f)

        self.assertIsInstance(portfolios, list)
        self.assertGreater(len(portfolios), 0)

        for i, portfolio in enumerate(portfolios):
            self.assertIn('name', portfolio, f"Entry {i} missing 'name' field")
            self.assertIn('url', portfolio, f"Entry {i} missing 'url' field")
            self.assertIsInstance(portfolio['name'], str, f"Entry {i} name should be string")
            self.assertIsInstance(portfolio['url'], str, f"Entry {i} url should be string")

            if 'tagline' in portfolio:
                self.assertIsInstance(portfolio['tagline'], str, f"Entry {i} tagline should be string")

    def test_feed_in_sync_with_readme(self):
        """Test that feed.json is strictly in sync with README.md entries and header count"""
        readme_path = os.path.join(REPO_ROOT, 'README.md')
        feed_path = os.path.join(REPO_ROOT, 'feed.json')

        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_lines = f.readlines()
        extracted = extract_portfolio_data(readme_lines)

        with open(feed_path, 'r', encoding='utf-8') as f:
            feed = json.load(f)

        self.assertEqual(len(extracted), len(feed), f"Count mismatch: README has {len(extracted)} entries, feed.json has {len(feed)}")

        for i, (r_entry, f_entry) in enumerate(zip(extracted, feed)):
            self.assertEqual(r_entry, f_entry, f"Entry {i} mismatch")

        header_pattern = re.compile(r"^##\s+Current\s+Portfolio\s+Count:\s+(\d+)")
        header_count = None
        for line in readme_lines:
            m = header_pattern.match(line.strip())
            if m:
                header_count = int(m.group(1))
                break

        self.assertEqual(header_count, len(extracted), f"Header count {header_count} does not match actual count {len(extracted)}")


if __name__ == "__main__":
    unittest.main()
