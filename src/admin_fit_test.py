"""Запускается ОТ АДМИНА (через UAC). Проверяет, что с правами
можно ресайзить окно игры. Пишет результат в лог-файл (мост читает его)."""
import sys, time, ctypes, traceback
LOG = r"D:\PROJECT\TilesSurviveMap\admin_result.txt"

def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(str(msg) + "\n")

open(LOG, "w", encoding="utf-8").close()  # очистить
try:
    sys.path.insert(0, r"D:\PROJECT\TilesSurviveMap\src")
    import window_manager as wm

    is_admin = bool(ctypes.windll.shell32.IsUserAnAdmin())
    log(f"IsUserAnAdmin: {is_admin}")

    w = wm.get_window()
    log(f"Сейчас: {(w.width, w.height)} позиция {(w.left, w.top)}")

    log("Ломаю размер -> 1200x700 ...")
    try:
        w.resizeTo(1200, 700); time.sleep(0.8)
        w = wm.get_window()
        log(f"После слома: {(w.width, w.height)}")
    except Exception as e:
        log(f"resize-слом FAIL: {e}")

    log(f"ensure_window -> эталон {wm.ETALON} ...")
    w = wm.ensure_window()
    log(f"После подгона: {(w.width, w.height)} позиция {(w.left, w.top)}")

    img, bbox = wm.capture_window(
        r"D:\PROJECT\TilesSurviveMap\data\720\screens\dalniy_fit.png", settle=1.0)
    log(f"Скрин: {img.size} bbox {bbox}")
    log("DONE")
except Exception:
    log("EXCEPTION:\n" + traceback.format_exc())
    log("DONE")
