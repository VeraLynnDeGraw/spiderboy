"""
SPIDERBOY - PERSONALITY AND APPEARANCE SETTINGS

This is the easiest place to customize Spiderboy.

You can change these values without editing his movement
or drawing code. Save the file and restart Spiderboy
to see your changes.

Keep the quotation marks around colors.
Keep the decimal points on decimal numbers.
"""

# ============================================================
# 1. COLORS
# ============================================================
# These use hexadecimal color codes.
# You can find new colors using any online color picker.

BODY_COLOR = "#172A25"
BODY_LIGHT_COLOR = "#29483B"
LEG_COLOR = "#263C32"
LEG_ACCENT_COLOR = "#B44A83"

PINK_COLOR = "#F05A9D"
VIOLET_COLOR = "#9365C9"
EYE_COLOR = "#F6B6D4"

WEB_THREAD_COLOR = "#789080"
WEB_VIOLET_COLOR = "#9365C9"
WEB_PINK_COLOR = "#F05A9D"


# ============================================================
# 2. MOVEMENT
# ============================================================
# Higher speed numbers make Spiderboy move faster.

WANDER_SPEED = 110.0
FOLLOW_SPEED = 285.0
FLEE_SPEED = 530.0

# How close he likes to stay to your cursor.
# Smaller number = he follows more closely.

FOLLOW_DISTANCE = 55.0

# How long he runs after a double-click, in milliseconds.
# 1000 milliseconds = 1 second.

FLEE_DURATION_MS = 1800

# How quickly he accelerates and changes direction.
# Higher values feel more responsive.

MOVEMENT_RESPONSE = 8.0


# ============================================================
# 3. SPIDER SIZE AND SHAPE
# ============================================================
# These define the area needed to display and click Spiderboy.
# They are not the actual drawing dimensions.

SPIDER_HALF_WIDTH = 54
SPIDER_HALF_HEIGHT = 49

# Thickness of his legs.

LEG_STROKE_WIDTH = 3


# ============================================================
# 4. ABDOMEN WIGGLE
# ============================================================
# His signature little bum shake.
# You can adjust the speed, angle, and vertical movement.

ABDOMEN_WIGGLE_SPEED = 2.35
ABDOMEN_WIGGLE_ANGLE = 4.0
ABDOMEN_BOB_DISTANCE = 1.8


# ============================================================
# 5. SPIDER WEBS
# ============================================================
# Web size is measured in pixels.
# Longer weaving time makes him work more slowly.

WEB_SIZE = 150
WEB_BUILD_SECONDS = 6.0

# How long he waits before considering another web.
# 20000 milliseconds = 20 seconds.

FIRST_WEB_DELAY_MS = 10000
WEB_REST_INTERVAL_MS = 20000

# Shape of the curved web strands.
# Larger numbers make the web extend farther into the desktop.

WEB_RADII = (28, 50, 73, 97, 123)

# Number of strands extending from the corner.

WEB_SPOKE_COUNT = 7

# Number of small sections making up each curved strand.

WEB_SEGMENTS_PER_RING = 10
WEB_THREAD_WIDTH = 1

# Weaving animation movement.

WEAVING_WIGGLE_SPEED = 4.5
