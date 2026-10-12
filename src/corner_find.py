"""Поиск нижне-левого угла штата: тащим карту вверх-вправо (вид едет вниз-влево),
с фокус-гвардом, по шагам, со снимками. cv2-метрика "воля/облака" для стопа.
БЕЗ easyocr (по сплиту: это управление+захват)."""
import sys, time, ctypes
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np, cv2
import window_manager as wm

SCR = r"D:\PROJECT\TilesSurviveMap\data\720\screens"
u = ctypes.windll.user32


def drag(x0, y0, x1, y1, steps=25, hold=0.15):
    u.SetCursorPos(int(x0), int(y0)); time.sleep(0.2)
    u.mouse_event(0x0002, 0, 0, 0, 0); time.sleep(hold)
    for i in range(1, steps + 1):
        u.SetCursorPos(int(x0 + (x1 - x0) * i / steps), int(y0 + (y1 - y0) * i / steps))
        time.sleep(0.012)
    time.sleep(hold)
    u.mouse_event(0x0004, 0, 0, 0, 0)


def focus():
    w = wm.ensure_window()
    try:
        w.activate()
    except Exception:
        pass
    time.sleep(0.4)
    return w, (u.GetForegroundWindow() == w._hWnd)


def void_frac(img):
    """Доля 'внешней воли' (олив.-зелёный фон за диамантом) в нижне-левой четверти."""
    a = np.array(img)
    h, wd = a.shape[:2]
    reg = a[int(h * 0.5):int(h * 0.92), int(wd * 0.02):int(wd * 0.45)]  # низ-лево, без чата
    hsv = cv2.cvtColor(reg, cv2.COLOR_RGB2HSV)
    # олив/зелёный фон: H~35..95, умеренная S, не слишком яркий
    mask = cv2.inRange(hsv, (30, 30, 40), (95, 200, 200))
    return float(mask.mean() / 255)


w, ok = focus()
print("focus ok:", ok, "| окно", (w.width, w.height), (w.left, w.top))

prev_v = None
for i in range(7):
    w, ok = focus()
    if not ok:
        print(f"шаг {i}: ВНИМАНИЕ окно не в фокусе"); 
    L, T = w.left, w.top
    # тащим карту вверх-вправо -> вид к нижне-левому углу
    drag(L + 500, T + 720, L + 1150, T + 300)
    time.sleep(1.6)
    img, _ = wm.capture_window(SCR + rf"\corner_step_{i}.png", settle=0.6)
    v = void_frac(img)
    d = "" if prev_v is None else f" (Δ={v-prev_v:+.3f})"
    print(f"шаг {i}: воля(низ-лево)={v:.3f}{d}")
    prev_v = v
print("done")
