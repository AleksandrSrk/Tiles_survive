"""Один раз от админа (UAC): регистрирует служебную задачу TSM_AdminRunner
(для будущих админ-прогонов БЕЗ UAC) и проверяет ресайз самой игры."""
import sys, ctypes, traceback, subprocess
BASE = r"D:\PROJECT\TilesSurviveMap"
PY = BASE + r"\.venv\Scripts\python.exe"
RUNNER = BASE + r"\src\admin_runner.py"
LOG = BASE + r"\admin_result.txt"

def log(m):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(str(m) + "\n")

open(LOG, "w", encoding="utf-8").close()
try:
    log(f"IsAdmin: {bool(ctypes.windll.shell32.IsUserAnAdmin())}")

    # 1) зарегистрировать задачу для будущих тихих запусков
    tr = f'\\"{PY}\\" \\"{RUNNER}\\"'
    cmd = f'schtasks /Create /TN "TSM_AdminRunner" /TR "{tr}" /SC ONCE /ST 23:59 /RL HIGHEST /F'
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                       encoding="cp866", errors="replace")
    log(f"schtasks create rc={r.returncode} out={r.stdout.strip()} err={r.stderr.strip()}")

    # 2) проверить ресайз ИГРЫ (исправленный поиск по классу UnityWndClass)
    sys.path.insert(0, BASE + r"\src")
    import window_manager as wm
    w = wm.get_window()
    log(f"Игра найдена: size={(w.width, w.height)} pos={(w.left, w.top)}")
    w = wm.ensure_window()
    log(f"После эталона: size={(w.width, w.height)} pos={(w.left, w.top)}")
    img, bbox = wm.capture_window(BASE + r"\data\720\screens\dalniy_fit2.png", settle=1.2)
    log(f"Скрин игры: {img.size} bbox={bbox}")
    log("DONE")
except Exception:
    log("EXC:\n" + traceback.format_exc())
    log("DONE")
