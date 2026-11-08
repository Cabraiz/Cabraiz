"""Run from the repo root: python -m unittest discover tests"""

import datetime as dt
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import stats  # noqa: E402


class Readme(unittest.TestCase):
    def test_recent_markers_are_present(self):
        text = (ROOT / "README.md").read_text("utf-8")
        self.assertIn("<!-- recent:start -->", text)
        self.assertIn("<!-- recent:end -->", text)

    def test_local_images_exist(self):
        text = (ROOT / "README.md").read_text("utf-8")
        paths = re.findall(r'(?:src|srcset)="(assets/[^"]+)"', text)
        self.assertTrue(paths)
        for path in paths:
            self.assertTrue((ROOT / path).exists(), path)


class Stats(unittest.TestCase):
    def test_streaks_tolerate_a_quiet_today(self):
        days = [("2026-01-01", 1), ("2026-01-02", 0), ("2026-01-03", 2), ("2026-01-04", 3), ("2026-01-05", 0)]
        self.assertEqual(stats.streaks(days, dt.date(2026, 1, 5)), (2, 2))
        self.assertEqual(stats.streaks(days, dt.date(2026, 1, 6)), (0, 2))

    def test_private_repositories_never_reach_the_recent_table(self):
        user = {
            "contributionsCollection": {"contributionCalendar": {"totalContributions": 3, "weeks": []}},
            "repositories": {"nodes": [
                {"name": "secret", "url": "u", "isPrivate": True, "pushedAt": "2026-10-01", "primaryLanguage": {"name": "Go", "color": "#000"}},
                {"name": "public", "url": "u", "isPrivate": False, "pushedAt": "2026-09-01", "primaryLanguage": None},
            ]},
        }
        summary = stats.summarise(user, True, dt.date(2026, 11, 1))
        self.assertEqual(summary["languages"][0][0], "Go")
        self.assertNotIn("secret", stats.recent_markdown(summary))
        self.assertNotIn("secret", stats.card(summary, "dark"))
        public_only = stats.summarise(user, False, dt.date(2026, 11, 1))
        self.assertEqual(public_only["languages"], [])

    def test_3d_crop_shrinks_the_canvas_only(self):
        svg = '<svg xmlns="x" width="1280" height="850" viewBox="0 0 1280 850"><rect height="850"/></svg>'
        cropped = stats.crop_3d(svg)
        self.assertIn('viewBox="0 0 1280 780"', cropped)
        self.assertIn('<svg xmlns="x" width="1280" height="780"', cropped)
        self.assertIn('<rect height="850"/>', cropped)


if __name__ == "__main__":
    unittest.main()


class Labels(unittest.TestCase):
    def test_one_day_is_singular(self):
        self.assertEqual(stats.plural_days(1), "1 day")
        self.assertEqual(stats.plural_days(0), "0 days")
        self.assertEqual(stats.plural_days(9), "9 days")
