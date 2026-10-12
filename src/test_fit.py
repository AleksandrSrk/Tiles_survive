"""Тест автоподгона окна: ломаем размер, потом даём боту вернуть к эталону."""
import sys, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import window_manager as wm

w = wm.get_window()
print("Сейчас:", (w.width, w.height), "позиция", (w.left, w.top))

print("Ломаю размер -> 1200x700 ...")
w.resizeTo(1200, 700); time.sleep(0.8)
w = wm.get_window()
print("После слома:", (w.width, w.height))

print(f"Бот подгоняет к эталону {wm.ETALON} ...")
w = wm.ensure_window()
print("После подгона:", (w.width, w.height), "позиция", (w.left, w.top))

img, bbox = wm.capture_window(
    r"D:\PROJECT\TilesSurviveMap\data\720\screens\dalniy_fit.png", settle=1.0)
print("Контрольный скрин:", img.size, "bbox", bbox)
