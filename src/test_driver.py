"""Тест safe-input слоя: домой -> макс-зум -> снимок -> безопасный драг.
Всё через driver с проверкой фокуса. Возврат в своё состояние (штат 720)."""
import sys, traceback
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import driver as dv
import window_manager as wm

SCR = r"D:\PROJECT\TilesSurviveMap\data\720\screens"
try:
    w = dv.ensure_focus()
    print("focus ok | окно", (w.width, w.height), (w.left, w.top))
    print("домой (Мое поселение)..."); dv.go_home()
    print("макс-зум..."); dv.zoom_max()
    img, _ = wm.capture_window(SCR + r"\driver_test.png", settle=1.2)
    print("снимок:", img.size)
    w = wm.get_window(); L, T = w.left, w.top
    print("безопасный драг (мелкий)...")
    dv.safe_drag(L + 600, T + 600, L + 900, T + 450)
    print("ИТОГ: safe-input + home + zoom + drag отработали без потери фокуса")
except dv.FocusLost as e:
    print("FOCUS LOST — ввод корректно прерван:", e)
except Exception:
    print("ОШИБКА:\n" + traceback.format_exc())
