"""
SPIDERBOY - ARTWORK AND ANIMATION

This file draws Spiderboy and his webs.

For simple changes such as colors, leg thickness,
web dimensions, and wiggle settings, edit settings.py
instead of changing this file.
"""

import math

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QBrush, QPen, QPainter

from spider import settings


# ============================================================
# COLORS
# All colors come from spider/settings.py
# ============================================================

BODY = QColor(settings.BODY_COLOR)
BODY_LIGHT = QColor(settings.BODY_LIGHT_COLOR)
LEG = QColor(settings.LEG_COLOR)
LEG_ACCENT = QColor(settings.LEG_ACCENT_COLOR)

PINK = QColor(settings.PINK_COLOR)
VIOLET = QColor(settings.VIOLET_COLOR)
EYE = QColor(settings.EYE_COLOR)

WEB_THREAD = QColor(settings.WEB_THREAD_COLOR)
WEB_VIOLET = QColor(settings.WEB_VIOLET_COLOR)
WEB_PINK = QColor(settings.WEB_PINK_COLOR)


# ============================================================
# LEG SHAPE
# Attachment, knee, foot, alternating gait phase.
#
# Advanced contributors can edit these coordinates to
# experiment with different spider proportions.
# ============================================================

LEGS = [
    (-12, -7, -23, -17, -37, -25, 0.0),
    (-5, -10, -12, -23, -20, -38, math.pi),
    (5, -10, 14, -23, 23, -38, math.pi),
    (12, -7, 25, -17, 40, -25, 0.0),

    (-12, 7, -23, 17, -37, 25, math.pi),
    (-5, 10, -12, 23, -20, 38, 0.0),
    (5, 10, 14, 23, 23, 38, 0.0),
    (12, 7, 25, 17, 40, 25, math.pi),
]


# ============================================================
# DRAW SPIDER
# ============================================================

def draw_spider(painter, center, phase=0.0, direction="west"):
    """Draw Spiderboy facing one of four directions."""

    painter.save()

    cx = center.x()
    cy = center.y()

    rotations = {
        "west": 0,
        "north": 90,
        "east": 180,
        "south": 270,
    }

    painter.translate(cx, cy)
    painter.rotate(rotations.get(direction, 0))
    painter.translate(-cx, -cy)

    painter.setRenderHint(
        QPainter.RenderHint.Antialiasing,
        False,
    )

    def point(x, y):
        return QPointF(cx + x, cy + y)

    # --------------------------------------------------------
    # LEGS
    # --------------------------------------------------------

    for sx, sy, kx, ky, fx, fy, offset in LEGS:

        gait = phase + offset
        stride = math.sin(gait)
        lift = max(0.0, math.cos(gait)) * 2.5

        side = -1 if fy < 0 else 1

        animated_kx = kx + stride * 1.4
        animated_ky = ky - side * lift * 0.35

        animated_fx = fx + stride * 3.0
        animated_fy = fy - side * lift

        painter.setPen(
            QPen(
                LEG,
                settings.LEG_STROKE_WIDTH,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.SquareCap,
                Qt.PenJoinStyle.MiterJoin,
            )
        )

        painter.setBrush(Qt.BrushStyle.NoBrush)

        painter.drawLine(
            point(sx, sy),
            point(animated_kx, animated_ky),
        )

        painter.drawLine(
            point(animated_kx, animated_ky),
            point(animated_fx, animated_fy),
        )

        # Knee joints.
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(LEG_ACCENT))

        painter.drawRect(
            int(cx + animated_kx - 1),
            int(cy + animated_ky - 1),
            3,
            3,
        )

        # Little feet.
        painter.setBrush(QBrush(BODY_LIGHT))

        painter.drawRect(
            int(cx + animated_fx - 1),
            int(cy + animated_fy - 1),
            3,
            3,
        )

    # --------------------------------------------------------
    # ABDOMEN
    # His signature little bum wiggle.
    # It has its own animation independent of the legs.
    # --------------------------------------------------------

    wiggle = math.sin(
        phase * settings.ABDOMEN_WIGGLE_SPEED
    )

    wiggle_offset = math.sin(
        phase * settings.ABDOMEN_WIGGLE_SPEED
        + math.pi / 2
    ) * settings.ABDOMEN_BOB_DISTANCE

    painter.save()

    abdomen_x = cx + 16

    painter.translate(abdomen_x, cy)

    painter.rotate(
        wiggle * settings.ABDOMEN_WIGGLE_ANGLE
    )

    painter.translate(-abdomen_x, -cy)

    abdomen_center = point(16, wiggle_offset)

    painter.setPen(QPen(BODY_LIGHT, 2))
    painter.setBrush(QBrush(BODY))

    painter.drawEllipse(
        abdomen_center,
        21,
        17,
    )

    # Violet abdomen markings.
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(VIOLET))

    painter.drawRect(
        int(cx + 26),
        int(cy + wiggle_offset - 6),
        8,
        4,
    )

    painter.drawRect(
        int(cx + 26),
        int(cy + wiggle_offset + 3),
        8,
        4,
    )

    # Pink detail.
    painter.setBrush(QBrush(PINK))

    painter.drawRect(
        int(cx + 35),
        int(cy + wiggle_offset - 2),
        5,
        5,
    )

    painter.restore()

    # --------------------------------------------------------
    # HEAD AND BODY
    # --------------------------------------------------------

    painter.setPen(QPen(BODY_LIGHT, 2))
    painter.setBrush(QBrush(BODY_LIGHT))

    painter.drawEllipse(
        point(-10, 0),
        14,
        12,
    )

    # Head accent.
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(VIOLET))

    painter.drawRect(
        int(cx - 17),
        int(cy - 4),
        5,
        8,
    )

    # Eyes.
    painter.setBrush(QBrush(EYE))

    painter.drawRect(
        int(cx - 23),
        int(cy - 6),
        4,
        4,
    )

    painter.drawRect(
        int(cx - 23),
        int(cy + 2),
        4,
        4,
    )

    painter.setBrush(QBrush(PINK))

    painter.drawRect(
        int(cx - 27),
        int(cy - 2),
        3,
        3,
    )

    painter.restore()


# ============================================================
# DRAW WEB
# Corner anchor, radial strands, and curved cross-strands.
# The web appears progressively as it is being woven.
# ============================================================

def draw_web(
    painter,
    anchor,
    corner,
    progress=1.0,
    size=settings.WEB_SIZE,
):
    """Draw a progressively constructed corner web."""

    progress = max(0.0, min(1.0, progress))

    if progress <= 0:
        return

    sx = 1 if corner.endswith("left") else -1
    sy = 1 if corner.startswith("top") else -1

    ax = anchor.x()
    ay = anchor.y()

    def web_point(radius, angle):
        return QPointF(
            ax + sx * math.cos(angle) * radius,
            ay + sy * math.sin(angle) * radius,
        )

    painter.save()

    # --------------------------------------------------------
    # RADIAL STRANDS
    # --------------------------------------------------------

    spoke_count = settings.WEB_SPOKE_COUNT

    visible_spokes = min(
        spoke_count,
        math.ceil(
            (progress / 0.52) * spoke_count
        ),
    )

    for index in range(visible_spokes):

        angle = (
            (math.pi / 2) * index
            / max(1, spoke_count - 1)
        )

        color = (
            WEB_VIOLET
            if index in (2, 4)
            else WEB_THREAD
        )

        painter.setPen(
            QPen(
                color,
                settings.WEB_THREAD_WIDTH,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.SquareCap,
            )
        )

        painter.drawLine(
            QPointF(ax, ay),
            web_point(size, angle),
        )

    # --------------------------------------------------------
    # CURVED CROSS-STRANDS
    # --------------------------------------------------------

    ring_progress = max(
        0.0,
        min(1.0, (progress - 0.52) / 0.48),
    )

    radii = settings.WEB_RADII
    segments = settings.WEB_SEGMENTS_PER_RING

    total_segments = len(radii) * segments

    visible_segments = math.ceil(
        ring_progress * total_segments
    )

    for ring_index, radius in enumerate(radii):

        for segment in range(segments):

            absolute_index = (
                ring_index * segments + segment
            )

            if absolute_index >= visible_segments:
                break

            angle_a = (
                (math.pi / 2) * segment / segments
            )

            angle_b = (
                (math.pi / 2) * (segment + 1) / segments
            )

            if segment == 4 and ring_index == len(radii) - 1:
                color = WEB_PINK
            elif ring_index == 2:
                color = WEB_VIOLET
            else:
                color = WEB_THREAD

            painter.setPen(
                QPen(
                    color,
                    settings.WEB_THREAD_WIDTH,
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.SquareCap,
                )
            )

            painter.drawLine(
                web_point(radius, angle_a),
                web_point(radius, angle_b),
            )

    # Tiny pink anchor detail.
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(WEB_PINK))

    painter.drawRect(
        int(ax + sx * 8 - 1),
        int(ay + sy * 8 - 1),
        3,
        3,
    )

    painter.restore()
