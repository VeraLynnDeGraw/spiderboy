# Customize Spiderboy

Welcome! This guide shows you how to personalize Spiderboy.

You do not need to understand all of his Python code.
Most everyday changes can be made in one file:

`spider/settings.py`

Open it using your preferred text editor.

## 1. Change his colors

Find the COLORS section.

Example:

    BODY_COLOR = "#172A25"
    PINK_COLOR = "#F05A9D"
    VIOLET_COLOR = "#9365C9"

Colors use hexadecimal color codes.

Keep the quotation marks around each color.

You can use an online color picker to find new colors.

## 2. Change how fast he moves

Find the MOVEMENT section.

| Setting | What it changes |
|---|---|
| `WANDER_SPEED` | How fast he explores |
| `FOLLOW_SPEED` | How fast he follows you |
| `FLEE_SPEED` | How fast he runs away |
| `FOLLOW_DISTANCE` | How close he approaches your cursor |
| `FLEE_DURATION_MS` | How long he stays in escape mode |
| `MOVEMENT_RESPONSE` | How quickly he accelerates |

Higher speed numbers make him move faster.

A smaller following distance makes him approach you more closely.

Time values ending in `_MS` are milliseconds.

1000 milliseconds equals one second.

## 3. Adjust his little bum wiggle

Find the ABDOMEN WIGGLE section.

| Setting | What it changes |
|---|---|
| `ABDOMEN_WIGGLE_SPEED` | How quickly his abdomen wiggles |
| `ABDOMEN_WIGGLE_ANGLE` | How much his abdomen rotates |
| `ABDOMEN_BOB_DISTANCE` | How much his abdomen moves vertically |

Experiment with these values to give him his own personality.

## 4. Customize his webs

Find the SPIDER WEBS section.

| Setting | What it changes |
|---|---|
| `WEB_SIZE` | Overall web size |
| `WEB_BUILD_SECONDS` | How long he takes to weave |
| `FIRST_WEB_DELAY_MS` | Initial waiting time before web building |
| `WEB_REST_INTERVAL_MS` | Waiting time between web-building attempts |
| `WEB_RADII` | Distances of the curved web strands |
| `WEB_SPOKE_COUNT` | Number of strands extending from the corner |
| `WEB_SEGMENTS_PER_RING` | Detail of the curved strands |
| `WEB_THREAD_WIDTH` | Thickness of the web threads |
| `WEAVING_WIGGLE_SPEED` | How quickly he wiggles while weaving |

Larger web dimensions make the web extend farther from its corner.

Longer construction times make him weave more slowly.

## 5. Change his appearance

You can customize:

- Body color
- Leg color
- Knee accents
- Eyes
- Abdomen markings
- Web strands
- Pink and violet details

Try changing one or two colors at a time.

## 6. Experiment safely

A good beginner workflow:

1. Create a backup.
2. Open `spider/settings.py`.
3. Change one or two values.
4. Save the file.
5. Restart Spiderboy.
6. See how your changes look.

To create a backup, run:

    ./spiderboy backup

To open his settings through the launcher, run:

    ./spiderboy customize

To test your changes, run:

    ./spiderboy test

## 7. Where is the rest of his code?

When you are ready to explore further:

| File | What it controls |
|---|---|
| `spider/settings.py` | Customization values |
| `spider/widget.py` | Movement, interaction, menus, and webs |
| `spider/renderer.py` | Spider artwork, animation, and web drawing |
| `main.py` | Application startup |

You can explore these files using a text editor.

The settings file is the recommended starting point.

## Important

Settings are loaded when Spiderboy starts.

Restart the application to apply your changes.

Keep a backup before experimenting with the application code.

Have fun making Spiderboy your own!
