"""Тестовый запуск обхода: только первые N кадров (граница -b, граница -a, начало ряда).
Раннер не принимает аргументы, поэтому они заданы здесь."""
import sys, runpy, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv = ["crawl.py", "--max-tiles", "6"]
runpy.run_path(os.path.join(HERE, "crawl.py"), run_name="__main__")
