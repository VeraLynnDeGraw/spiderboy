/*
 * Spider Boy — KWin global cursor observer.
 *
 * KDE-specific adapter only. This script does not control Spider Boy.
 */

var lastSent = 0;

function sendPosition() {
    var now = Date.now();

    // Limit D-Bus traffic to approximately 60 updates per second.
    if (now - lastSent < 16) {
        return;
    }

    lastSent = now;

    var position = workspace.cursorPos;

    callDBus(
        "org.spiderboy.CursorBridge",
        "/Cursor",
        "local.KWinCursorBridge",
        "updatePosition",
        position.x,
        position.y
    );
}

sendPosition();
workspace.cursorPosChanged.connect(sendPosition);

print("SPIDERBOY_CURSOR_BRIDGE_READY");
