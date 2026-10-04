import unittest
from datetime import date

from fenix_nightlight.solar import solar_times


class SolarTests(unittest.TestCase):
    def test_kornik_autumn_times_are_plausible(self):
        times = solar_times(date(2026, 10, 4), 52.2477, 17.0895, "Europe/Warsaw")
        self.assertEqual(times.sunrise.date(), date(2026, 10, 4))
        self.assertEqual(times.sunset.date(), date(2026, 10, 4))
        self.assertGreaterEqual(times.sunrise.hour, 6)
        self.assertLessEqual(times.sunrise.hour, 7)
        self.assertGreaterEqual(times.sunset.hour, 17)
        self.assertLessEqual(times.sunset.hour, 19)
        self.assertLess(times.sunrise, times.sunset)

    def test_summer_day_is_longer_than_winter_day(self):
        summer = solar_times(date(2026, 6, 21), 52.2477, 17.0895, "Europe/Warsaw")
        winter = solar_times(date(2026, 12, 21), 52.2477, 17.0895, "Europe/Warsaw")
        self.assertGreater(
            (summer.sunset - summer.sunrise).total_seconds(),
            (winter.sunset - winter.sunrise).total_seconds(),
        )

    def test_invalid_latitude_is_rejected(self):
        with self.assertRaises(ValueError):
            solar_times(date(2026, 10, 4), 95.0, 17.0, "Europe/Warsaw")


if __name__ == "__main__":
    unittest.main()
