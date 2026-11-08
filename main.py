"""
Spiderboy.

Application entry point. No startup preflight or artificial delay.
"""

import sys

from PySide6.QtWidgets import QApplication

from spider.widget import SpiderWidget


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Spiderboy")
    app.setQuitOnLastWindowClosed(False)

    spider = SpiderWidget()
    app.aboutToQuit.connect(spider.shutdown)

    spider.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
