"""Досъёмка слабых плиток вблизи (4 щелчка). Запуск через админ-раннер (без аргументов)."""
import sys, glob, os
BASE = r"D:\PROJECT\TilesSurviveMap"
scan = sorted(glob.glob(BASE + r"\data\720\scans\scan_*"))[-1]
sys.argv = ["crawl_mm.py", "--points", BASE + r"\data\720\recheck_none.json", "--into", scan, "--zoom", "4"]
sys.path.insert(0, BASE + r"\src")
import crawl_mm, driver as dv
if dv.abort_requested():
    print("ScrollLock"); sys.exit(2)
crawl_mm.main()
