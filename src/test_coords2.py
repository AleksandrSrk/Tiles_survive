"""Тест 2: координаты при сдвиге + порог появления имён над домами.
Свой штат -> «Мое поселение» (камера на нашем доме) -> приближение 17/21/25 щелчков
(пауза 0.3 с) со снимком на каждом пороге -> 3 небольших драга со снимками.
Кадры: data/720/screens/coords2/*.png ; журнал: log.json. OCR — отдельно, в облаке."""
import sys, os, time, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
import window_manager as wm
import driver as dv

OUT = r"D:\PROJECT\TilesSurviveMap\data\720\screens\coords2"
os.makedirs(OUT, exist_ok=True)
log = []


def shot(name):
    wm.capture_window(OUT + rf"\{name}.png", settle=0.6)
    print("снимок", name, flush=True)


def drag_cursor(dx, dy, label):
    w = dv.ensure_focus()
    cx, cy = w.left + w.width // 2, w.top + w.height // 2
    dv.safe_drag(cx - dx / 2, cy - dy / 2, cx + dx / 2, cy + dy / 2)
    time.sleep(1.6)
    log.append({"step": label, "cursor_drag": [dx, dy]})
    print("драг", label, (dx, dy), flush=True)


try:
    if dv.abort_requested():
        print("ScrollLock включён — выключи и запусти снова"); sys.exit(2)
    w = wm.ensure_window()
    dv.clear_popups()
    print("[1] отдаляем до упора:", dv.zoom_max(), flush=True)
    img, _ = wm.capture_window(OUT + r"\_state.png", settle=0.5)
    foreign = dv.find_return_button(np.array(img)) is not None
    print("[2] чужой штат:", foreign, flush=True)
    if foreign:
        print("   возврат в свой штат:", dv.goto_own_state(), flush=True)
    dv.go_home()
    print("[3] «Мое поселение» нажато", flush=True)
    shot("far_home")
    cx, cy = w.left + w.width // 2, w.top + w.height // 2
    total = 0
    for target in (17, 21, 25):
        dv.safe_wheel(cx, cy, target - total, delta=+120, pause=0.3)
        total = target
        time.sleep(1.2)
        shot(f"zoom_{total:02d}")
    drag_cursor(-300, 0, "d1: контент влево 300")
    shot("d1")
    drag_cursor(0, -250, "d2: контент вверх 250")
    shot("d2")
    drag_cursor(250, 150, "d3: контент вправо-вниз (250,150)")
    shot("d3")
    json.dump(log, open(OUT + r"\log.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("[4] возвращаем максимальное отдаление", flush=True)
    dv.zoom_max()
    print("готово", flush=True)
except dv.Aborted as e:
    print("ОСТАНОВЛЕНО:", e)
except dv.FocusLost as e:
    print("ФОКУС ПОТЕРЯН:", e)
