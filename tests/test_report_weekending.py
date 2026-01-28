import json
import unittest
from datetime import datetime
from pathlib import Path


class TestReportWeekEnding(unittest.TestCase):
    def test_report_week_ending_is_sunday(self):
        p = Path('data') / 'contributions_2026.json'
        self.assertTrue(p.exists(), f"{p} not found")
        with p.open() as f:
            data = json.load(f)
        rwe = data.get('reportWeekEnding')
        self.assertIsNotNone(rwe, 'reportWeekEnding missing')
        try:
            dt = datetime.fromisoformat(rwe)
        except Exception:
            dt = datetime.fromisoformat(rwe.split('Z')[0])
        self.assertEqual(dt.weekday(), 6, f"reportWeekEnding {rwe} is not a Sunday")


if __name__ == '__main__':
    unittest.main()
