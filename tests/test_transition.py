import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from fenix_nightlight.config import Settings
from fenix_nightlight.solar import SolarTimes
from fenix_nightlight.transition import target_state


class TransitionTests(unittest.TestCase):
    def setUp(self):
        self.tz = ZoneInfo("Europe/Warsaw")
        self.settings = Settings(
            location_name="Test",
            latitude=52.0,
            longitude=17.0,
            timezone="Europe/Warsaw",
            day_temp=4500,
            night_temp=4000,
            transition_minutes=30,
        )
        self.solar = SolarTimes(
            sunrise=datetime(2026, 10, 4, 7, 0, tzinfo=self.tz),
            sunset=datetime(2026, 10, 4, 18, 0, tzinfo=self.tz),
        )

    def test_day_target(self):
        state = target_state(datetime(2026, 10, 4, 12, 0, tzinfo=self.tz), self.settings, self.solar)
        self.assertEqual((state.temperature, state.phase), (4500, "day"))

    def test_night_target(self):
        state = target_state(datetime(2026, 10, 4, 23, 0, tzinfo=self.tz), self.settings, self.solar)
        self.assertEqual((state.temperature, state.phase), (4000, "night"))

    def test_evening_midpoint(self):
        state = target_state(datetime(2026, 10, 4, 18, 15, tzinfo=self.tz), self.settings, self.solar)
        self.assertEqual(state.phase, "evening-transition")
        self.assertEqual(state.temperature, 4250)

    def test_morning_midpoint(self):
        state = target_state(datetime(2026, 10, 4, 7, 15, tzinfo=self.tz), self.settings, self.solar)
        self.assertEqual(state.phase, "morning-transition")
        self.assertEqual(state.temperature, 4250)


if __name__ == "__main__":
    unittest.main()
