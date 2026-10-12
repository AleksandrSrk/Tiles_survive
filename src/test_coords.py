"""Тест координат: растёт ли X/Y в верхней плашке при сдвиге карты и сколько px на клетку.
Макс. отдаление -> 40 щелчков приближения -> кадр -> драги с известной длиной -> кадры.
Кадры: data/720/screens/coords/c0..c3.png ; журнал команд: coords_log.json
OCR плашки делается отдельно (в нормальном процессе), здесь только управление и снимки."""
import sys, os, time, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import window_manager as wm
import driver as dv

OUT = r"D:\PROJECT\TilesSurviveMap\data\720\screens\coords"
os.makedirs(OUT, exist_ok=True)
log = []


def shot(name):
    img, _ = wm.capture_window(OUT + rf"\{name}.png", settle=0.6)
    print(f"снимок {name}", flush=True)


def drag_cursor(dx, dy, label):
    """Курсор тянем на (dx,dy) от центра; контент идёт за курсором."""
    w = dv.ensure_focus()
    cx, cy = w.left + w.width // 2, w.top + w.height // 2
    dv.safe_drag(cx - dx / 2, cy - dy / 2, cx + dx / 2, cy + dy / 2)
    time.sleep(1.6)
    log.append({"step": label, "cursor_drag": [dx, dy]})
    print(f"драг {label}: курсор {dx},{dy}", flush=True)


try:
    if dv.abort_requested():
        print("ScrollLock включён — выключи и запусти снова"); sys.exit(2)
    w = wm.ensure_window()
    dv.clear_popups()
    print("[1] отдаляем до упора", flush=True)
    print("   упор достигнут:", dv.zoom_max(), flush=True)
    cx, cy = w.left + w.width // 2, w.top + w.height // 2
    print("[2] приближаем на 40 щелчков", flush=True)
    dv.safe_wheel(cx, cy, 40, delta=+120)
    time.sleep(1.8)
    shot("c0")
    drag_cursor(-400, 0, "c1: контент влево на 400 (вид вправо)")
    shot("c1")
    drag_cursor(0, -300, "c2: контент вверх на 300 (вид вниз)")
    shot("c2")
    drag_cursor(300, 200, "c3: контент вправо-вниз (300,200)")
    shot("c3")
    json.dump(log, open(OUT + r"\coords_log.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("[3] возвращаем максимальное отдаление", flush=True)
    dv.zoom_max()
    print("готово", flush=True)
except dv.Aborted as e:
    print("ОСТАНОВЛЕНО:", e)
except dv.FocusLost as e:
    print("ФОКУС ПОТЕРЯН:", e)
