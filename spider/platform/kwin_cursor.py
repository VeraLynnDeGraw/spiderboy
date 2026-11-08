"""KWin global cursor diagnostics for Spider Boy.

This module is an optional KDE-specific adapter. It does not control
movement, animation, or interaction behavior.
"""

from pathlib import Path

from PySide6.QtCore import QElapsedTimer, QObject, QPoint, Signal, Slot
from PySide6.QtDBus import QDBusConnection, QDBusInterface, QDBusMessage


SERVICE_NAME = "org.spiderboy.CursorBridge"
OBJECT_PATH = "/Cursor"
INTERFACE_NAME = "org.spiderboy.CursorBridge"
PLUGIN_NAME = "org.spiderboy.CursorBridge"


class KWinCursorBridge(QObject):
    """Receive global cursor coordinates forwarded by KWin."""

    positionChanged = Signal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.bus = QDBusConnection.sessionBus()
        self.interface = None

        self.available = False
        self.latest_position = None
        self.received_count = 0
        self._position_clock = QElapsedTimer()
        self._position_clock.start()
        self._has_position = False
        self._registered_service = False
        self._registered_object = False
        self._script_loaded = False

    @Slot(int, int)
    def updatePosition(self, x, y):
        """D-Bus entry point called by the KWin script."""

        self.latest_position = (x, y)
        self.received_count += 1
        self._position_clock.restart()
        self._has_position = True
        self.positionChanged.emit(x, y)

    def cursor_position(self, max_age_ms=250):
        """Return a fresh global position, or None if it is stale."""
        if not self._has_position:
            return None
        if self._position_clock.elapsed() > max_age_ms:
            return None
        x, y = self.latest_position
        return QPoint(x, y)

    @staticmethod
    def _message_error(message):
        if message.type() == QDBusMessage.MessageType.ErrorMessage:
            return message.errorMessage()

        return None

    def _call_kwin(self, method, *arguments):
        message = self.interface.call(method, *arguments)
        error = self._message_error(message)

        if error:
            raise RuntimeError(f"KWin {method} failed: {error}")

        return message.arguments()

    def start(self):
        """Register the D-Bus receiver and start the KWin observer."""

        if self.available:
            return True

        if not self.bus.isConnected():
            print("[Spider Boy] KDE cursor bridge: session bus unavailable.")
            return False

        if not self.bus.registerService(SERVICE_NAME):
            print(
                "[Spider Boy] KDE cursor bridge: could not register "
                f"D-Bus service: {self.bus.lastError().message()}"
            )
            return False

        self._registered_service = True

        if not self.bus.registerObject(
            OBJECT_PATH,
            self,
            QDBusConnection.RegisterOption.ExportAllSlots,
        ):
            print(
                "[Spider Boy] KDE cursor bridge: could not register "
                f"D-Bus object: {self.bus.lastError().message()}"
            )
            self.stop()
            return False

        self._registered_object = True

        self.interface = QDBusInterface(
            "org.kde.KWin",
            "/Scripting",
            "org.kde.kwin.Scripting",
            self.bus,
        )

        if not self.interface.isValid():
            print(
                "[Spider Boy] KDE cursor bridge: KWin scripting "
                "interface unavailable."
            )
            self.stop()
            return False

        script_path = (
            Path(__file__).with_name("kwin_cursor.js").resolve()
        )

        try:
            loaded = self._call_kwin(
                "isScriptLoaded",
                PLUGIN_NAME,
            )

            if loaded and loaded[0]:
                self._call_kwin("unloadScript", PLUGIN_NAME)

            result = self._call_kwin(
                "loadScript",
                str(script_path),
                PLUGIN_NAME,
            )

            if not result or int(result[0]) < 0:
                raise RuntimeError("KWin did not load the cursor script.")

            self._script_loaded = True

            self._call_kwin("start")

            self.available = True
            print("[Spider Boy] KDE global cursor diagnostics active.")
            return True

        except Exception as exc:
            print(f"[Spider Boy] KDE cursor bridge unavailable: {exc}")
            self.stop()
            return False

    def stop(self):
        """Unload the observer and release the D-Bus registrations."""

        if self.interface is not None and self._script_loaded:
            try:
                self._call_kwin("unloadScript", PLUGIN_NAME)
            except Exception as exc:
                print(
                    "[Spider Boy] Cursor observer cleanup warning: "
                    f"{exc}"
                )

        self._script_loaded = False
        self.available = False
        self.interface = None

        if self._registered_object:
            self.bus.unregisterObject(OBJECT_PATH)
            self._registered_object = False

        if self._registered_service:
            self.bus.unregisterService(SERVICE_NAME)
            self._registered_service = False

    def shutdown(self):
        self.stop()
