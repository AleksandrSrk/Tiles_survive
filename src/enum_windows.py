"""Перечислить все видимые верхнеуровневые окна: hwnd, pid, класс, размер, заголовок.
Ищем структуру обёртки игры (внешняя рамка vs внутренний движок tspc)."""
import sys, ctypes
from ctypes import wintypes
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

user32 = ctypes.windll.user32
EnumProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

rows = []

def cb(hwnd, _):
    if not user32.IsWindowVisible(hwnd):
        return True
    n = user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(n + 1)
    user32.GetWindowTextW(hwnd, buf, n + 1)
    title = buf.value
    cls = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, cls, 256)
    pid = ctypes.c_ulong()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    r = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(r))
    w, h = r.right - r.left, r.bottom - r.top
    # интересны окна с заметной площадью или с заголовком
    if title or (w > 200 and h > 200):
        rows.append((hwnd, pid.value, cls.value, title, w, h, r.left, r.top))
    return True

user32.EnumWindows(EnumProc(cb), 0)

print(f"{'hwnd':>10} {'pid':>7} {'класс':<22} {'WxH':>11} {'поз':>14}  заголовок")
for hwnd, pid, cls, title, w, h, l, t in rows:
    print(f"{hwnd:>10} {pid:>7} {cls[:22]:<22} {f'{w}x{h}':>11} {f'({l},{t})':>14}  {title[:40]}")
