"""Tests for beginner-editable Spiderboy settings."""

import re
import unittest

from spider import settings
from spider import renderer


class SettingsTests(unittest.TestCase):

    def test_colors_use_valid_hex_format(self):

        names = (
            "BODY_COLOR",
            "BODY_LIGHT_COLOR",
            "LEG_COLOR",
            "LEG_ACCENT_COLOR",
            "PINK_COLOR",
            "VIOLET_COLOR",
            "EYE_COLOR",
            "WEB_THREAD_COLOR",
            "WEB_VIOLET_COLOR",
            "WEB_PINK_COLOR",
        )

        for name in names:

            with self.subTest(setting=name):

                value = getattr(settings, name)

                self.assertRegex(
                    value,
                    re.compile(r"^#[0-9A-Fa-f]{6}$"),
                )

    def test_renderer_uses_settings_colors(self):

        self.assertEqual(
            renderer.BODY.name(),
            settings.BODY_COLOR.lower(),
        )

        self.assertEqual(
            renderer.LEG.name(),
            settings.LEG_COLOR.lower(),
        )

        self.assertEqual(
            renderer.PINK.name(),
            settings.PINK_COLOR.lower(),
        )

        self.assertEqual(
            renderer.WEB_THREAD.name(),
            settings.WEB_THREAD_COLOR.lower(),
        )

    def test_movement_values_are_positive(self):

        self.assertGreater(settings.WANDER_SPEED, 0)
        self.assertGreater(settings.FOLLOW_SPEED, 0)
        self.assertGreater(settings.FLEE_SPEED, 0)
        self.assertGreater(settings.FOLLOW_DISTANCE, 0)

    def test_animation_values_are_positive(self):

        self.assertGreater(settings.ABDOMEN_WIGGLE_SPEED, 0)
        self.assertGreater(settings.ABDOMEN_WIGGLE_ANGLE, 0)
        self.assertGreater(settings.ABDOMEN_BOB_DISTANCE, 0)

    def test_web_values_are_valid(self):

        self.assertGreater(settings.WEB_SIZE, 0)
        self.assertGreater(settings.WEB_BUILD_SECONDS, 0)
        self.assertGreaterEqual(len(settings.WEB_RADII), 1)
        self.assertGreaterEqual(settings.WEB_SPOKE_COUNT, 2)
        self.assertGreaterEqual(settings.WEB_SEGMENTS_PER_RING, 1)

        self.assertEqual(
            tuple(sorted(settings.WEB_RADII)),
            settings.WEB_RADII,
        )


if __name__ == "__main__":
    unittest.main()
