"""Работа с окном игры TilesSurvive (Unity, класс UnityWndClass).
DPI-awareness включается при импорте — координаты в реальных пикселях."""
import sys, time, ctypes
from ctypes import wintypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

import pygetwindow as gw
from PIL import ImageGrab

TITLE = "TilesSurvive"
GAME_CLASS = "UnityWndClass"
ETALON = (1774, 1028)        # размер окна (ширина, высота)
ETALON_POS = (-1774, 20)     # фикс. позиция (левый монитор), по решению пользователя

_user32 = ctypes.windll.user32
_EnumProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
# 64-бит: без argtypes HWND идёт как обычный int и падает с OverflowError в колбэке EnumWindows
_user32.IsWindowVisible.argtypes = [wintypes.HWND]
_user32.IsWindowVisible.restype = wintypes.BOOL
_user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
_user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
_user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
_user32.EnumWindows.argtypes = [_EnumProc, wintypes.LPARAM]


def _class_of(hwnd):
    buf = ctypes.create_unicode_buffer(256)
    _user32.GetClassNameW(hwnd, buf, 256)
    return buf.value


def _title_of(hwnd):
    n = _user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(n + 1)
    _user32.GetWindowTextW(hwnd, buf, n + 1)
    return buf.value


def get_window():
    found = []

    def cb(hwnd, _):
        if _user32.IsWindowVisible(hwnd) and _class_of(hwnd) == GAME_CLASS:
            if TITLE.lower() in _title_of(hwnd).lower():
                found.append(hwnd)
        return True

    _user32.EnumWindows(_EnumProc(cb), 0)
    return gw.Win32Window(found[0]) if found else None


def ensure_window(size=ETALON, pos=ETALON_POS, settle=0.6):
    """Привести окно к эталонному размеру И фиксированной позиции."""
    w = get_window()
    if w is None:
        raise RuntimeError("Окно игры (UnityWndClass/TilesSurvive) не найдено")
    if w.isMinimized or w.isMaximized:
        w.restore(); time.sleep(settle)
    if (w.width, w.height) != size:
        w.resizeTo(*size); time.sleep(settle)
    w = get_window()
    if (w.left, w.top) != tuple(pos):
        w.moveTo(*pos); time.sleep(settle)
    return get_window()


def capture_window(path, settle=0.0):
    w = get_window()
    if w is None:
        raise RuntimeError("Окно игры не найдено")
    try:
        w.activate()
    except Exception:
        pass
    time.sleep(max(settle, 0.3))
    bbox = (w.left, w.top, w.left + w.width, w.top + w.height)
    img = ImageGrab.grab(bbox=bbox, all_screens=True)
    img.save(path)
    return img, bbox


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    w = get_window()
    print("Игра:", (w.width, w.height), "позиция", (w.left, w.top)) if w else print("нет окна")
