"""Automated tests for Spiderboy and his webs."""

import unittest

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtWidgets import QApplication

from spider.renderer import draw_spider, draw_web
from spider.widget import SpiderWidget, SpiderWeb


class SpiderTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.app = (
            QApplication.instance()
            or QApplication([])
        )

        cls.app.setQuitOnLastWindowClosed(False)

    def setUp(self):
        self.spider = SpiderWidget()

    def tearDown(self):
        self.spider.shutdown()

    def test_starts_in_wander_mode(self):
        self.assertEqual(self.spider.mode, "wander")

    def test_follow_activates_immediately(self):

        self.spider.activate_follow()

        self.assertEqual(self.spider.mode, "follow")

        for overlay in self.spider.overlays:
            self.assertFalse(hasattr(overlay, "click_timer"))

    def test_double_click_escape_activates_flee(self):

        self.spider.activate_follow()

        cursor = QPoint(
            round(self.spider.spider_x - 150),
            round(self.spider.spider_y),
        )

        self.spider.activate_flee(cursor)

        self.assertEqual(self.spider.mode, "flee")
        self.assertEqual(self.spider.direction, "east")

    def test_follow_moves_toward_cursor_cardinally(self):

        self.spider.activate_follow()

        cursor = QPoint(
            round(self.spider.spider_x + 500),
            round(self.spider.spider_y + 20),
        )

        vx, vy = self.spider.desired_velocity(
            cursor,
            self.spider.clock.elapsed(),
        )

        self.assertGreater(vx, 0)
        self.assertEqual(vy, 0)

    def test_follow_uses_fresh_platform_cursor_position(self):

        if self.spider.cursor_bridge is None:
            self.skipTest("QtDBus cursor adapter unavailable")

        self.spider.activate_follow()
        self.spider.cursor_bridge.updatePosition(4321, 876)
        self.assertEqual(
            self.spider.cursor_position_for_behavior(),
            QPoint(4321, 876),
        )

    def test_platform_cursor_position_expires_when_stale(self):

        if self.spider.cursor_bridge is None:
            self.skipTest("QtDBus cursor adapter unavailable")

        bridge = self.spider.cursor_bridge
        bridge.updatePosition(4321, 876)
        self.assertIsNone(bridge.cursor_position(max_age_ms=-1))

    def test_follow_respects_personal_space(self):

        self.spider.activate_follow()

        cursor = QPoint(
            round(
                self.spider.spider_x
                + self.spider.follow_distance
                - 20
            ),
            round(self.spider.spider_y),
        )

        vx, vy = self.spider.desired_velocity(
            cursor,
            self.spider.clock.elapsed(),
        )

        self.assertEqual(vx, 0)
        self.assertEqual(vy, 0)

    def test_menu_contains_expected_commands(self):

        menu = self.spider.overlays[0].menu

        labels = [
            action.text()
            for action in menu.actions()
            if not action.isSeparator()
        ]

        expected = (
            "SPIDERBOY",
            "Follow me",
            "Wander",
            "Scurry away",
            "Build a web",
            "Clear webs",
            "Pause",
            "Quit Spiderboy",
        )

        for label in expected:
            self.assertIn(label, labels)

    def test_menu_follow_action(self):

        self.spider.overlays[0].follow_action.trigger()

        self.assertEqual(self.spider.mode, "follow")

    def test_menu_wander_action(self):

        self.spider.activate_follow()
        self.spider.overlays[0].wander_action.trigger()

        self.assertEqual(self.spider.mode, "wander")

    def test_menu_flee_action(self):

        self.spider.overlays[0].flee_action.trigger()

        self.assertEqual(self.spider.mode, "flee")

    def test_pause_and_resume(self):

        self.spider.activate_follow()
        self.spider.toggle_pause()

        self.assertEqual(self.spider.mode, "paused")

        self.spider.toggle_pause()

        self.assertEqual(self.spider.mode, "follow")

    def test_one_visual_and_hitbox_per_monitor(self):

        count = len(self.app.screens())

        self.assertEqual(len(self.spider.visuals), count)
        self.assertEqual(len(self.spider.overlays), count)

        for visual, hitbox, screen in zip(
            self.spider.visuals,
            self.spider.overlays,
            self.app.screens(),
        ):
            self.assertEqual(visual.geometry(), screen.geometry())
            self.assertEqual(hitbox.geometry(), screen.geometry())

    def test_visual_surfaces_are_click_through(self):

        for visual in self.spider.visuals:

            flags = visual.windowFlags()

            self.assertTrue(
                flags & Qt.WindowType.WindowTransparentForInput
            )

    def test_four_directions_are_supported(self):

        cases = (
            (100, 0, "east"),
            (-100, 0, "west"),
            (0, -100, "north"),
            (0, 100, "south"),
        )

        for dx, dy, expected in cases:

            self.spider.choose_direction(dx, dy)

            self.assertEqual(
                self.spider.direction,
                expected,
            )

    def test_corner_sites_are_available(self):

        self.assertGreater(
            len(self.spider.corner_sites),
            0,
        )

        for site in self.spider.corner_sites:

            self.assertIn(
                site["corner"],
                (
                    "top-left",
                    "top-right",
                    "bottom-left",
                    "bottom-right",
                ),
            )

    def test_build_web_starts_corner_trip(self):

        started = self.spider.start_next_web(force=True)

        self.assertTrue(started)
        self.assertEqual(self.spider.mode, "to_web")
        self.assertIsNotNone(self.spider.active_site)

    def test_web_weaving_creates_progressive_web(self):

        self.assertTrue(
            self.spider.start_next_web(force=True)
        )

        self.spider._begin_weaving()

        self.assertEqual(self.spider.mode, "weave")
        self.assertIsNotNone(self.spider.active_web)
        self.assertEqual(self.spider.active_web.progress, 0.0)

        self.spider.active_web.progress = 0.5

        self.assertEqual(
            self.spider.active_web.progress,
            0.5,
        )

    def test_completed_web_is_recorded(self):

        site = self.spider.corner_sites[0]

        web = SpiderWeb(
            site_id=site["id"],
            screen_index=site["screen_index"],
            corner=site["corner"],
            anchor_x=site["anchor_x"],
            anchor_y=site["anchor_y"],
            progress=1.0,
            complete=True,
        )

        self.spider.webs.append(web)
        self.spider.built_site_ids.add(site["id"])

        self.assertIn(site["id"], self.spider.built_site_ids)
        self.assertIn(web, self.spider.webs)

    def test_clear_webs_removes_active_and_completed_webs(self):

        self.assertTrue(
            self.spider.start_next_web(force=True)
        )

        self.spider._begin_weaving()

        self.spider.clear_webs()

        self.assertEqual(self.spider.webs, [])
        self.assertIsNone(self.spider.active_web)
        self.assertIsNone(self.spider.active_site)
        self.assertEqual(self.spider.mode, "wander")

    def test_web_renderer_draws_pixels(self):

        image = QImage(
            180,
            180,
            QImage.Format.Format_ARGB32,
        )

        image.fill(Qt.GlobalColor.transparent)

        painter = QPainter(image)

        draw_web(
            painter,
            image.rect().topLeft(),
            "top-left",
            progress=1.0,
            size=150,
        )

        painter.end()

        pixels = sum(
            1
            for y in range(image.height())
            for x in range(image.width())
            if image.pixelColor(x, y).alpha() > 0
        )

        self.assertGreater(pixels, 0)

    def test_spider_renderer_draws_pixels(self):

        image = QImage(
            128,
            128,
            QImage.Format.Format_ARGB32,
        )

        image.fill(Qt.GlobalColor.transparent)

        painter = QPainter(image)

        draw_spider(
            painter,
            image.rect().center(),
            phase=1.25,
            direction="west",
        )

        painter.end()

        pixels = sum(
            1
            for y in range(image.height())
            for x in range(image.width())
            if image.pixelColor(x, y).alpha() > 0
        )

        self.assertGreater(pixels, 0)


if __name__ == "__main__":
    unittest.main()
