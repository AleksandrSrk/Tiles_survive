"""Запускается служебной задачей ОТ АДМИНА (без UAC).
Читает путь целевого скрипта из admin_cmd.txt, выполняет его,
весь вывод кладёт в admin_result.txt — мост читает файл."""
import sys, subprocess, datetime
BASE = r"D:\PROJECT\TilesSurviveMap"
try:
    target = open(BASE + r"\admin_cmd.txt", encoding="utf-8").read().strip()
    r = subprocess.run([sys.executable, target], capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    out = (f"[{datetime.datetime.now():%H:%M:%S}] target={target}\n"
           f"RC={r.returncode}\n--- STDOUT ---\n{r.stdout}\n--- STDERR ---\n{r.stderr}\n")
except Exception as e:
    out = f"RUNNER ERROR: {e}\n"
with open(BASE + r"\admin_result.txt", "w", encoding="utf-8") as f:
    f.write(out)
