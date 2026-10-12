"""Проверка фикса размера+позиции: ломаем, потом бот возвращает к эталону."""
import sys, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import window_manager as wm

w = wm.get_window()
print("старт:", (w.width, w.height), "позиция", (w.left, w.top))
# ломаем: другой размер и позиция
try:
    w.resizeTo(1300, 760); time.sleep(0.5)
    w = wm.get_window(); w.moveTo(-1500, 300); time.sleep(0.5)
    w = wm.get_window()
    print("сломали:", (w.width, w.height), "позиция", (w.left, w.top))
except Exception as e:
    print("ломание:", e)

w = wm.ensure_window()
print("после ensure:", (w.width, w.height), "позиция", (w.left, w.top))
print("эталон ок:", (w.width, w.height) == wm.ETALON and (w.left, w.top) == wm.ETALON_POS)
