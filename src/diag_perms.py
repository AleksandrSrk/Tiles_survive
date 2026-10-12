"""Диагностика прав на управление окном игры."""
import sys, ctypes
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import window_manager as wm

w = wm.get_window()
print("Окно:", (w.width, w.height), "позиция", (w.left, w.top))

# PID процесса, которому принадлежит окно
user32 = ctypes.windll.user32
pid = ctypes.c_ulong()
user32.GetWindowThreadProcessId(w._hWnd, ctypes.byref(pid))
print("PID окна игры:", pid.value)

# наш уровень прав (админ ли мы)
is_admin = ctypes.windll.shell32.IsUserAnAdmin()
print("Наш процесс запущен от администратора:", bool(is_admin))

for op, fn in [("move", lambda: w.moveTo(w.left, w.top)),
               ("resize", lambda: w.resizeTo(1600, 900))]:
    try:
        fn()
        print(f"{op}: OK")
    except Exception as e:
        print(f"{op}: FAIL -> {e}")
