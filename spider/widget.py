"""
Spiderboy desktop pet.

A shared multi-monitor simulation with:
- Autonomous wandering
- Immediate click-to-follow
- Double-click escape
- A small context menu
- Autonomous corner-web construction
- Persistent webs for the current application session

Visual surfaces are click-through. Separate masked hitboxes
receive input only where Spiderboy is drawn.
"""

import math
import random

from dataclasses import dataclass

from PySide6.QtCore import (
    QElapsedTimer,
    QObject,
    QPoint,
    QPointF,
    QRect,
    QTimer,
    Qt,
)
from PySide6.QtGui import QCursor, QPainter, QRegion
from PySide6.QtWidgets import QApplication, QMenu, QWidget

from spider import settings
try:
    from spider.platform.kwin_cursor import KWinCursorBridge
except ImportError:
    KWinCursorBridge = None
from spider.renderer import draw_spider, draw_web


SPIDER_HALF_WIDTH = settings.SPIDER_HALF_WIDTH
SPIDER_HALF_HEIGHT = settings.SPIDER_HALF_HEIGHT

WEB_SIZE = settings.WEB_SIZE
WEB_BUILD_SECONDS = settings.WEB_BUILD_SECONDS


@dataclass
class SpiderWeb:
    """A web being built or already completed."""

    site_id: str
    screen_index: int
    corner: str
    anchor_x: int
    anchor_y: int
    progress: float = 0.0
    complete: bool = False


class SpiderVisualOverlay(QWidget):
    """Full-screen transparent drawing surface for one monitor."""

    def __init__(self, controller, screen):
        super().__init__()

        self.controller = controller
        self.screen = screen
        self.screen_rect = screen.geometry()

        self.setGeometry(self.screen_rect)
        self.setWindowTitle("Spiderboy Visuals")

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground,
            True,
        )
        self.setAttribute(
            Qt.WidgetAttribute.WA_NoSystemBackground,
            True,
        )
        self.setAttribute(
            Qt.WidgetAttribute.WA_ShowWithoutActivating,
            True,
        )
        self.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True,
        )

        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.WindowDoesNotAcceptFocus
            | Qt.WindowType.WindowTransparentForInput
        )

    def paintEvent(self, event):

        painter = QPainter(self)

        # Explicitly erase the invalidated area. This is important:
        # the old spider position must be cleared when he moves.
        painter.setCompositionMode(
            QPainter.CompositionMode.CompositionMode_Source
        )
        painter.fillRect(
            event.rect(),
            Qt.GlobalColor.transparent,
        )
        painter.setCompositionMode(
            QPainter.CompositionMode.CompositionMode_SourceOver
        )

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing,
            False,
        )

        # Draw the persistent corner webs first.
        for web in self.controller.webs:

            if web.screen_index != self.controller.screens.index(
                self.screen
            ):
                continue

            local_anchor = QPointF(
                web.anchor_x - self.screen_rect.left(),
                web.anchor_y - self.screen_rect.top(),
            )

            draw_web(
                painter,
                local_anchor,
                web.corner,
                web.progress,
                WEB_SIZE,
            )

        # The spider can overlap two monitors while crossing
        # their boundary, so draw him wherever his bounds intersect.
        global_bounds = self.controller.spider_bounds()

        if global_bounds.intersects(self.screen_rect):

            local_center = QPointF(
                self.controller.spider_x - self.screen_rect.left(),
                self.controller.spider_y - self.screen_rect.top(),
            )

            bob = (
                math.sin(self.controller.phase * 1.7)
                * self.controller.bob_amount
            )

            draw_spider(
                painter,
                QPointF(
                    local_center.x(),
                    local_center.y() + bob,
                ),
                self.controller.phase,
                self.controller.direction,
            )

        painter.end()


class SpiderHitbox(QWidget):
    """A transparent, selectively clickable Spiderboy region."""

    def __init__(self, controller, screen):
        super().__init__()

        self.controller = controller
        self.screen = screen
        self.screen_rect = screen.geometry()

        self.setGeometry(self.screen_rect)
        self.setWindowTitle("Spiderboy Controls")

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground,
            True,
        )
        self.setAttribute(
            Qt.WidgetAttribute.WA_NoSystemBackground,
            True,
        )
        self.setAttribute(
            Qt.WidgetAttribute.WA_ShowWithoutActivating,
            True,
        )

        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )

        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.last_mask = QRect()

        self._build_menu()

    def _build_menu(self):

        self.menu = QMenu(self)
        self.menu.setWindowFlag(
            Qt.WindowType.WindowStaysOnTopHint, True
        )

        self.menu.setStyleSheet("""
            QMenu {
                background-color: #14251F;
                color: #E8E4DF;
                border: 1px solid #9365C9;
                padding: 5px;
            }

            QMenu::item {
                padding: 7px 22px;
                border-radius: 3px;
            }

            QMenu::item:selected {
                background-color: #713B68;
                color: #FFFFFF;
            }

            QMenu::item:disabled {
                color: #F05A9D;
                font-weight: bold;
            }

            QMenu::separator {
                height: 1px;
                background: #405347;
                margin: 5px 8px;
            }
        """)

        heading = self.menu.addAction("SPIDERBOY")
        heading.setEnabled(False)

        self.menu.addSeparator()

        self.follow_action = self.menu.addAction("Follow me")
        self.follow_action.triggered.connect(
            lambda checked=False:
                self.controller.activate_follow()
        )

        self.wander_action = self.menu.addAction("Wander")
        self.wander_action.triggered.connect(
            lambda checked=False:
                self.controller.activate_wander()
        )

        self.flee_action = self.menu.addAction("Scurry away")
        self.flee_action.triggered.connect(
            lambda checked=False:
                self.controller.activate_flee(QCursor.pos())
        )

        self.menu.addSeparator()

        self.build_action = self.menu.addAction("Build a web")
        self.build_action.triggered.connect(
            lambda checked=False:
                self.controller.start_next_web(force=True)
        )

        self.clear_action = self.menu.addAction("Clear webs")
        self.clear_action.triggered.connect(
            lambda checked=False:
                self.controller.clear_webs()
        )

        self.menu.addSeparator()

        self.pause_action = self.menu.addAction("Pause")
        self.pause_action.triggered.connect(
            lambda checked=False:
                self.controller.toggle_pause()
        )

        self.menu.addSeparator()

        self.quit_action = self.menu.addAction("Quit Spiderboy")
        self.quit_action.triggered.connect(
            lambda checked=False:
                QApplication.quit()
        )

        self.menu.aboutToShow.connect(self._menu_opening)
        self.menu.aboutToHide.connect(self.controller.menu_closed)

    def _menu_opening(self):

        self.pause_action.setText(
            "Resume"
            if self.controller.mode == "paused"
            else "Pause"
        )

        self.build_action.setEnabled(
            bool(self.controller.available_web_sites())
        )

        self.clear_action.setEnabled(
            bool(self.controller.webs)
            or self.controller.active_site is not None
        )

        self.controller.menu_opened()

    def sync(self, global_bounds):

        local_bounds = global_bounds.translated(
            -self.screen_rect.left(),
            -self.screen_rect.top(),
        ).intersected(
            QRect(
                0,
                0,
                self.screen_rect.width(),
                self.screen_rect.height(),
            )
        )

        if local_bounds.isEmpty():

            if self.isVisible():
                print(
                    f"[Spider Boy hitbox] Hiding; empty bounds. "
                    f"screen={self.screen_rect}",
                    flush=True,
                )
                self.hide()

            return

        if local_bounds != self.last_mask:
            self.setMask(QRegion(local_bounds))
            self.last_mask = QRect(local_bounds)
            print(
                f"[Spider Boy hitbox] Mask updated: "
                f"local={local_bounds}, screen={self.screen_rect}",
                flush=True,
            )

        if not self.isVisible():
            self.show()
            self.raise_()
            print(
                f"[Spider Boy hitbox] Shown: "
                f"geometry={self.geometry()}, "
                f"visible={self.isVisible()}",
                flush=True,
            )

    def mousePressEvent(self, event):

        if event.button() in (
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.RightButton,
        ):
            print(
                f"[Spider Boy hitbox] Mouse press: "
                f"button={event.button()}, "
                f"position={event.position().toPoint()}",
                flush=True,
            )
            event.accept()
            return

        event.ignore()

    def mouseDoubleClickEvent(self, event):

        # Left-click now opens the menu. Escape is available
        # through the Scurry away menu command.
        event.accept()

    def mouseReleaseEvent(self, event):

        if event.button() in (
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.RightButton,
        ):
            global_position = self.mapToGlobal(
                event.position().toPoint()
            )

            print(
                f"[Spider Boy hitbox] Mouse release: "
                f"button={event.button()}, "
                f"global={global_position}; scheduling menu",
                flush=True,
            )

            # Wait until Qt finishes processing the click release
            # before opening the popup.
            QTimer.singleShot(
                0,
                lambda position=global_position:
                    self.menu.popup(position),
            )

            event.accept()
            return

        event.ignore()


class SpiderWidget(QObject):
    """Shared simulation and behavior controller."""

    def __init__(self):
        super().__init__()

        self.screens = QApplication.screens()

        if not self.screens:
            raise RuntimeError("No displays were detected.")

        primary = QApplication.primaryScreen()

        start_screen = (
            primary if primary in self.screens
            else self.screens[0]
        )

        start_rect = start_screen.geometry()

        self.spider_x = float(start_rect.center().x())
        self.spider_y = float(start_rect.center().y())

        self.velocity_x = 0.0
        self.velocity_y = 0.0

        self.direction = "west"
        self.mode = "wander"
        self.previous_mode = "wander"

        self.wander_speed = settings.WANDER_SPEED
        self.follow_speed = settings.FOLLOW_SPEED
        self.flee_speed = settings.FLEE_SPEED
        self.follow_distance = settings.FOLLOW_DISTANCE
        self.flee_duration = settings.FLEE_DURATION_MS

        self.flee_until = 0
        self.waypoints = []

        self.phase = 0.0
        self.bob_amount = 0.65
        self.menu_open = False

        self.clock = QElapsedTimer()
        self.clock.start()

        self.last_elapsed = self.clock.elapsed()

        self.webs = []
        self.built_site_ids = set()
        self.active_site = None
        self.active_web = None

        self.weave_duration = WEB_BUILD_SECONDS
        self.web_size = WEB_SIZE
        self.web_interval = settings.WEB_REST_INTERVAL_MS

        self.corner_sites = self._find_corner_sites()
        self.next_web_check = self.clock.elapsed() + 10000

        # Full-screen visual surfaces are created first.
        self.visuals = [
            SpiderVisualOverlay(self, screen)
            for screen in self.screens
        ]

        # Selective hitboxes are separate from the visual surfaces.
        self.overlays = [
            SpiderHitbox(self, screen)
            for screen in self.screens
        ]

        self.animation_timer = QTimer(self)
        self.animation_timer.setInterval(16)
        self.animation_timer.timeout.connect(self.advance)

        self.choose_destination()

        # KDE global cursor diagnostics are independent of movement.
        self.cursor_bridge = (
            KWinCursorBridge(self)
            if KWinCursorBridge is not None
            else None
        )
        if self.cursor_bridge is not None:
            self.cursor_bridge.positionChanged.connect(
                self._record_global_cursor
            )
        self._last_cursor_diagnostic = -1000

    def _record_global_cursor(self, x, y):

        elapsed = self.clock.elapsed()

        # Keep diagnostic output readable: at most one line per second.
        if elapsed - self._last_cursor_diagnostic < 1000:
            return

        self._last_cursor_diagnostic = elapsed

        print(
            f"[Spider Boy cursor diagnostic] x={x}, y={y}",
            flush=True,
        )

    def cursor_position_for_behavior(self):
        """Use fresh platform coordinates for Follow when available."""
        if self.mode == "follow" and self.cursor_bridge is not None:
            position = self.cursor_bridge.cursor_position()
            if position is not None:
                return position
        return QCursor.pos()

    def show(self):

        if self.cursor_bridge is not None:
            self.cursor_bridge.start()

        for visual in self.visuals:
            visual.show()

        self.sync_overlays()
        self.animation_timer.start()

    def shutdown(self):

        self.animation_timer.stop()
        if self.cursor_bridge is not None:
            self.cursor_bridge.shutdown()

        for overlay in self.overlays:
            overlay.menu.close()
            overlay.close()

        for visual in self.visuals:
            visual.close()

    def spider_bounds(self):

        return QRect(
            round(self.spider_x) - SPIDER_HALF_WIDTH,
            round(self.spider_y) - SPIDER_HALF_HEIGHT,
            SPIDER_HALF_WIDTH * 2 + 1,
            SPIDER_HALF_HEIGHT * 2 + 1,
        )

    def sync_overlays(self, dirty_global=None):

        bounds = self.spider_bounds()

        if dirty_global is None:
            dirty_global = bounds

        for visual in self.visuals:

            rect = visual.screen_rect

            local_dirty = dirty_global.translated(
                -rect.left(),
                -rect.top(),
            ).intersected(
                QRect(0, 0, rect.width(), rect.height())
            )

            if not local_dirty.isEmpty():
                visual.update(local_dirty)

        for overlay in self.overlays:
            overlay.sync(bounds)

    def screen_index_for_position(self):

        point = QPoint(
            round(self.spider_x),
            round(self.spider_y),
        )

        for index, screen in enumerate(self.screens):

            if screen.geometry().contains(point):
                return index

        distances = []

        for index, screen in enumerate(self.screens):

            rect = screen.geometry()

            dx = max(
                rect.left() - point.x(),
                0,
                point.x() - rect.right(),
            )

            dy = max(
                rect.top() - point.y(),
                0,
                point.y() - rect.bottom(),
            )

            distances.append((dx * dx + dy * dy, index))

        return min(distances)[1]

    def choose_direction(self, dx, dy):

        if abs(dx) >= abs(dy):

            if dx:
                self.direction = "east" if dx > 0 else "west"

        elif dy:
            self.direction = "south" if dy > 0 else "north"

    def _screen_margin(self, rect):

        return min(
            90,
            max(20, min(rect.width(), rect.height()) // 8),
        )

    def _crossing_waypoints(self, source_index, target_index):

        source = self.screens[source_index].geometry()
        target = self.screens[target_index].geometry()

        margin = self._screen_margin(source)
        target_margin = self._screen_margin(target)

        overlap_top = max(
            source.top() + margin,
            target.top() + target_margin,
        )

        overlap_bottom = min(
            source.bottom() - margin,
            target.bottom() - target_margin,
        )

        overlap_left = max(
            source.left() + margin,
            target.left() + target_margin,
        )

        overlap_right = min(
            source.right() - margin,
            target.right() - target_margin,
        )

        gap_east = target.left() - source.right() - 1
        gap_west = source.left() - target.right() - 1

        gap_south = target.top() - source.bottom() - 1
        gap_north = source.top() - target.bottom() - 1

        if (
            target.center().x() > source.center().x()
            and -40 <= gap_east <= 160
            and overlap_top <= overlap_bottom
        ):

            crossing_y = self._clamp(
                self.spider_y,
                overlap_top,
                overlap_bottom,
            )

            entry_x = target.left() + target_margin

            return [
                (self.spider_x, crossing_y),
                (entry_x, crossing_y),
            ]

        if (
            target.center().x() < source.center().x()
            and -40 <= gap_west <= 160
            and overlap_top <= overlap_bottom
        ):

            crossing_y = self._clamp(
                self.spider_y,
                overlap_top,
                overlap_bottom,
            )

            entry_x = target.right() - target_margin

            return [
                (self.spider_x, crossing_y),
                (entry_x, crossing_y),
            ]

        if (
            target.center().y() > source.center().y()
            and -40 <= gap_south <= 160
            and overlap_left <= overlap_right
        ):

            crossing_x = self._clamp(
                self.spider_x,
                overlap_left,
                overlap_right,
            )

            entry_y = target.top() + target_margin

            return [
                (crossing_x, self.spider_y),
                (crossing_x, entry_y),
            ]

        if (
            target.center().y() < source.center().y()
            and -40 <= gap_north <= 160
            and overlap_left <= overlap_right
        ):

            crossing_x = self._clamp(
                self.spider_x,
                overlap_left,
                overlap_right,
            )

            entry_y = target.bottom() - target_margin

            return [
                (crossing_x, self.spider_y),
                (crossing_x, entry_y),
            ]

        return None

    def _set_route(self, target_screen, target_x, target_y):

        source_screen = self.screen_index_for_position()

        if source_screen == target_screen:
            route = []
        else:
            route = self._crossing_waypoints(
                source_screen,
                target_screen,
            )

            if route is None:
                return False

        self.waypoints = list(route)
        self.waypoints.append((target_x, target_y))

        return True

    def choose_destination(self):

        source_screen = self.screen_index_for_position()

        candidates = list(range(len(self.screens)))
        random.shuffle(candidates)

        for target_screen in candidates:

            rect = self.screens[target_screen].geometry()
            margin = self._screen_margin(rect)

            target_x = random.uniform(
                rect.left() + margin,
                rect.right() - margin,
            )

            target_y = random.uniform(
                rect.top() + margin,
                rect.bottom() - margin,
            )

            if self._set_route(
                target_screen,
                target_x,
                target_y,
            ):
                return

        rect = self.screens[source_screen].geometry()
        margin = self._screen_margin(rect)

        self.waypoints = [
            (
                random.uniform(
                    rect.left() + margin,
                    rect.right() - margin,
                ),
                random.uniform(
                    rect.top() + margin,
                    rect.bottom() - margin,
                ),
            )
        ]

    def _find_corner_sites(self):

        sites = []

        corners = (
            ("top-left", "left", "top"),
            ("top-right", "right", "top"),
            ("bottom-left", "left", "bottom"),
            ("bottom-right", "right", "bottom"),
        )

        exclusion = self.web_size // 2

        for index, screen in enumerate(self.screens):

            rect = screen.geometry()

            for name, horizontal, vertical in corners:

                anchor_x = (
                    rect.left()
                    if horizontal == "left"
                    else rect.right()
                )

                anchor_y = (
                    rect.top()
                    if vertical == "top"
                    else rect.bottom()
                )

                anchor = QPoint(anchor_x, anchor_y)

                # Do not build in corners covered or nearly
                # joined to another display.
                joined_to_other = False

                for other_index, other_screen in enumerate(self.screens):

                    if other_index == index:
                        continue

                    other_rect = other_screen.geometry().adjusted(
                        -exclusion,
                        -exclusion,
                        exclusion,
                        exclusion,
                    )

                    if other_rect.contains(anchor):
                        joined_to_other = True
                        break

                if joined_to_other:
                    continue

                inward_x = 1 if horizontal == "left" else -1
                inward_y = 1 if vertical == "top" else -1

                sites.append({
                    "id": f"{index}:{name}",
                    "screen_index": index,
                    "corner": name,
                    "anchor_x": anchor_x,
                    "anchor_y": anchor_y,
                    "target_x": anchor_x + inward_x * 62,
                    "target_y": anchor_y + inward_y * 58,
                })

        return sites

    def available_web_sites(self):

        active_id = (
            self.active_site["id"]
            if self.active_site is not None
            else None
        )

        return [
            site
            for site in self.corner_sites
            if site["id"] not in self.built_site_ids
            and site["id"] != active_id
        ]

    def _web_bounds(self, web):

        left = (
            web.anchor_x
            if web.corner.endswith("left")
            else web.anchor_x - self.web_size
        )

        top = (
            web.anchor_y
            if web.corner.startswith("top")
            else web.anchor_y - self.web_size
        )

        return QRect(
            left,
            top,
            self.web_size + 1,
            self.web_size + 1,
        )

    def _cancel_build(self):

        dirty = None

        if self.active_web is not None:

            dirty = self._web_bounds(self.active_web)

            if self.active_web in self.webs:
                self.webs.remove(self.active_web)

        self.active_web = None
        self.active_site = None

        return dirty

    def start_next_web(self, force=False):

        if self.active_site is not None:
            return False

        candidates = self.available_web_sites()
        random.shuffle(candidates)

        self._cancel_build()

        for site in candidates:

            if self._set_route(
                site["screen_index"],
                site["target_x"],
                site["target_y"],
            ):

                self.active_site = site
                self.mode = "to_web"

                self.velocity_x = 0.0
                self.velocity_y = 0.0

                return True

        self.next_web_check = (
            self.clock.elapsed() + 60000
        )

        return False

    def _begin_weaving(self):

        if self.active_site is None:
            self.mode = "wander"
            self.choose_destination()
            return

        site = self.active_site

        if site["corner"].startswith("top"):
            self.direction = "north"
        else:
            self.direction = "south"

        self.active_web = SpiderWeb(
            site_id=site["id"],
            screen_index=site["screen_index"],
            corner=site["corner"],
            anchor_x=site["anchor_x"],
            anchor_y=site["anchor_y"],
        )

        self.webs.append(self.active_web)
        self.mode = "weave"

    def _waypoint_velocity(self):

        while self.waypoints:

            target_x, target_y = self.waypoints[0]

            dx = target_x - self.spider_x
            dy = target_y - self.spider_y

            # Cardinal movement keeps his turns deliberate.
            if abs(dx) > 8:

                self.direction = "east" if dx > 0 else "west"

                return (
                    self.wander_speed if dx > 0
                    else -self.wander_speed,
                    0.0,
                )

            if abs(dy) > 8:

                self.direction = "south" if dy > 0 else "north"

                return (
                    0.0,
                    self.wander_speed if dy > 0
                    else -self.wander_speed,
                )

            self.waypoints.pop(0)

        if self.mode == "to_web":
            self._begin_weaving()
            return 0.0, 0.0

        self.choose_destination()
        return 0.0, 0.0

    def activate_follow(self):

        dirty = self._cancel_build()

        self.mode = "follow"
        self.velocity_x = 0.0
        self.velocity_y = 0.0

        if dirty is not None:
            self.sync_overlays(dirty)

    def activate_wander(self):

        dirty = self._cancel_build()

        self.mode = "wander"
        self.velocity_x = 0.0
        self.velocity_y = 0.0

        self.choose_destination()
        self.next_web_check = (
            self.clock.elapsed() + 10000
        )

        if dirty is not None:
            self.sync_overlays(dirty)

    def activate_flee(self, cursor_position):

        dirty = self._cancel_build()

        self.mode = "flee"
        self.flee_until = (
            self.clock.elapsed() + self.flee_duration
        )

        dx = self.spider_x - cursor_position.x()
        dy = self.spider_y - cursor_position.y()

        if math.hypot(dx, dy) < 8:

            self.direction = random.choice(
                ("north", "south", "east", "west")
            )

        else:
            self.choose_direction(dx, dy)

        self.velocity_x = 0.0
        self.velocity_y = 0.0

        if dirty is not None:
            self.sync_overlays(dirty)

    def toggle_pause(self):

        if self.mode == "paused":
            self.mode = self.previous_mode
        else:
            self.previous_mode = self.mode
            self.mode = "paused"

        self.velocity_x = 0.0
        self.velocity_y = 0.0

    def clear_webs(self):

        dirty = None

        for web in self.webs:

            bounds = self._web_bounds(web)

            dirty = (
                bounds if dirty is None
                else dirty.united(bounds)
            )

        active_dirty = self._cancel_build()

        if active_dirty is not None:
            dirty = (
                active_dirty if dirty is None
                else dirty.united(active_dirty)
            )

        self.webs.clear()
        self.built_site_ids.clear()

        if self.mode in ("to_web", "weave"):
            self.mode = "wander"
            self.choose_destination()

        elif self.mode == "paused" and self.previous_mode in (
            "to_web",
            "weave",
        ):
            self.previous_mode = "wander"

        self.next_web_check = (
            self.clock.elapsed() + 10000
        )

        if dirty is not None:
            self.sync_overlays(dirty)

    def menu_opened(self):

        self.menu_open = True

        # Keep the full-screen drawing windows behind the popup.
        for visual in self.visuals:
            visual.lower()

    def menu_closed(self):

        self.menu_open = False
        self.last_elapsed = self.clock.elapsed()

        # Restore the artwork and clickable spider surface.
        for visual in self.visuals:
            visual.raise_()

        for overlay in self.overlays:
            overlay.raise_()

    def desired_velocity(self, cursor_position, elapsed):

        if self.mode in ("wander", "to_web"):
            return self._waypoint_velocity()

        if self.mode == "weave":
            return 0.0, 0.0

        if self.mode == "flee":

            if self.direction == "east":
                return self.flee_speed, 0.0

            if self.direction == "west":
                return -self.flee_speed, 0.0

            if self.direction == "south":
                return 0.0, self.flee_speed

            return 0.0, -self.flee_speed

        if self.mode == "follow":

            dx = cursor_position.x() - self.spider_x
            dy = cursor_position.y() - self.spider_y

            distance = math.hypot(dx, dy)

            if distance <= self.follow_distance:
                return 0.0, 0.0

            self.choose_direction(dx, dy)

            speed = min(
                self.follow_speed,
                max(
                    85.0,
                    (distance - self.follow_distance) * 3.0,
                ),
            )

            if self.direction == "east":
                return speed, 0.0

            if self.direction == "west":
                return -speed, 0.0

            if self.direction == "south":
                return 0.0, speed

            return 0.0, -speed

        return 0.0, 0.0

    def _clamp(self, value, lower, upper):
        return max(lower, min(upper, value))

    def _keep_on_desktop(self):

        point = QPoint(
            round(self.spider_x),
            round(self.spider_y),
        )

        for screen in self.screens:

            rect = screen.geometry().adjusted(
                -SPIDER_HALF_WIDTH,
                -SPIDER_HALF_HEIGHT,
                SPIDER_HALF_WIDTH,
                SPIDER_HALF_HEIGHT,
            )

            if rect.contains(point):
                return

        candidates = []

        for screen in self.screens:

            rect = screen.geometry()
            margin = self._screen_margin(rect)

            x = self._clamp(
                self.spider_x,
                rect.left() + margin,
                rect.right() - margin,
            )

            y = self._clamp(
                self.spider_y,
                rect.top() + margin,
                rect.bottom() - margin,
            )

            distance = (
                (x - self.spider_x) ** 2
                + (y - self.spider_y) ** 2
            )

            candidates.append((distance, x, y))

        _, nearest_x, nearest_y = min(candidates)

        if abs(nearest_x - self.spider_x) > 0.1:
            self.velocity_x = 0.0

        if abs(nearest_y - self.spider_y) > 0.1:
            self.velocity_y = 0.0

        self.spider_x = nearest_x
        self.spider_y = nearest_y

    def advance(self):

        elapsed = self.clock.elapsed()

        delta_time = min(
            (elapsed - self.last_elapsed) / 1000.0,
            0.05,
        )

        self.last_elapsed = elapsed

        if delta_time <= 0:
            return

        if self.menu_open or self.mode == "paused":
            return

        if (
            self.mode == "flee"
            and elapsed >= self.flee_until
        ):
            self.activate_wander()

        if (
            self.mode == "wander"
            and elapsed >= self.next_web_check
        ):
            self.start_next_web()

        old_bounds = self.spider_bounds()

        if self.mode == "weave" and self.active_web is not None:

            self.active_web.progress = min(
                1.0,
                self.active_web.progress
                + delta_time / self.weave_duration,
            )

            # He gets especially enthusiastic about the bum wiggle
            # while weaving. The renderer keeps it independent.
            self.phase += delta_time * 4.5
            self.bob_amount = 0.35

            if self.active_web.progress >= 1.0:

                self.active_web.complete = True

                self.built_site_ids.add(
                    self.active_web.site_id
                )

                self.active_web = None
                self.active_site = None

                self.mode = "wander"
                self.choose_destination()

                self.next_web_check = (
                    elapsed + self.web_interval
                )

        else:

            desired_x, desired_y = self.desired_velocity(
                self.cursor_position_for_behavior(),
                elapsed,
            )

            response = min(1.0, delta_time * 8.0)

            self.velocity_x += (
                desired_x - self.velocity_x
            ) * response

            self.velocity_y += (
                desired_y - self.velocity_y
            ) * response

            self.spider_x += self.velocity_x * delta_time
            self.spider_y += self.velocity_y * delta_time

            self._keep_on_desktop()

            speed = math.hypot(
                self.velocity_x,
                self.velocity_y,
            )

            self.phase += delta_time * (
                1.7 + min(speed, 530.0) * 0.019
            )

            self.bob_amount = (
                0.45 + min(speed / 180.0, 1.0) * 0.75
            )

        new_bounds = self.spider_bounds()
        dirty = old_bounds.united(new_bounds)

        # Web strands must repaint while being constructed.
        if self.active_web is not None:
            dirty = dirty.united(
                self._web_bounds(self.active_web)
            )

        self.sync_overlays(dirty)
