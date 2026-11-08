# Spider Boy 🕷️

**A little spider who lives on your desktop.**

Spider Boy is a lightweight animated desktop companion.
He wanders around your screens, follows your cursor,
scurries away when startled, and builds little corner webs.

He also has a very important talent: shaking his bum.

## Getting started

You do not need to know Python to use Spider Boy.

1. Download or clone this project.
2. Open a terminal inside the Spider Boy folder.
3. Run `./spiderboy`.
4. Choose **2. Set up or repair Spider Boy**.
5. When setup finishes, choose **1. Start Spider Boy**.

That's it!

Setup creates a private Python environment inside this
project and installs the required packages. It does not
install Python packages globally.

## Controls

Right-click or left-click Spider Boy to open his menu.

The menu includes:

- Follow me
- Wander
- Scurry away
- Build a web
- Clear webs
- Pause and resume
- Quit Spider Boy

## Customize your own spider

You do not need to understand the entire codebase to
personalize Spider Boy.

Open:

`spider/settings.py`

This is the main customization file.

Change his colors, movement speeds, following distance,
abdomen wiggle, web size, and weaving time.

Save your changes and restart Spider Boy.

See [CUSTOMIZATION.md](docs/CUSTOMIZATION.md).

## Friendly terminal commands

| Command | What it does |
|---|---|
| `./spiderboy` | Opens the numbered menu |
| `./spiderboy setup` | Installs or repairs dependencies |
| `./spiderboy run` | Starts Spider Boy |
| `./spiderboy test` | Runs automated tests |
| `./spiderboy verify` | Checks the application and displays |
| `./spiderboy backup` | Creates a project backup |
| `./spiderboy clean-cache` | Cleans generated project files |
| `./spiderboy customize` | Opens the settings file |
| `./spiderboy docs` | Opens the beginner guide |
| `./spiderboy help` | Shows available commands |

The older `./run.sh` launcher is also supported.

## Project map

| Location | Purpose |
|---|---|
| `spiderboy` | Friendly terminal launcher |
| `main.py` | Application startup |
| `spider/settings.py` | Beginner-friendly customization |
| `spider/widget.py` | Movement, interaction, and web behavior |
| `spider/renderer.py` | Spider and web artwork |
| `tests/` | Automated tests |
| `docs/` | Customization guide |
| `verify.py` | Runtime and display checks |

## Technology

- Python 3
- PySide6 / Qt
- Bash
- Python's built-in unittest framework

## Development status

Spider Boy is an evolving open-source project.

The current implementation includes autonomous movement,
cursor following, escape behavior, a desktop menu,
multi-monitor overlays, and progressive corner-web building.

The project has been tested on Arch Linux with KDE Plasma
Wayland and two displays. Other desktop environments and
compositors still need testing.

Desktop input and transparency behavior can vary depending
on the window system and compositor.

## Contributing

You are welcome to explore, learn from, customize, and
improve Spider Boy.

Have fun, and be kind to the little spider.
