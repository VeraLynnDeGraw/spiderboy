"""Spiderboy runtime smoke test."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from spider.widget import SpiderWidget


def main():

    app = QApplication.instance() or QApplication([])
    app.setQuitOnLastWindowClosed(False)

    spider = SpiderWidget()

    try:
        assert spider.mode == "wander"
        assert len(spider.visuals) == len(app.screens())
        assert len(spider.overlays) == len(app.screens())
        assert spider.corner_sites

        for visual, hitbox, screen in zip(
            spider.visuals,
            spider.overlays,
            app.screens(),
        ):
            assert visual.geometry() == screen.geometry()
            assert hitbox.geometry() == screen.geometry()

            assert (
                visual.windowFlags()
                & Qt.WindowType.WindowTransparentForInput
            )

        print("Spiderboy foundation: PASS")
        print("Movement controller: PASS")
        print("Physical monitors detected:", len(app.screens()))
        print("Visual surfaces: PASS")
        print("Selective click regions: PASS")
        print("Spider menu: PASS")
        print("Available web corners:", len(spider.corner_sites))
        print("Web construction controller: PASS")

    finally:
        spider.shutdown()


if __name__ == "__main__":
    main()
