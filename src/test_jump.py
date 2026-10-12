"""Тест прыжка по миникарте: клик по левому углу ромба (фикс-координаты) ->
камера должна перенестись в левый угол нашего штата."""
import sys, traceback
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import driver as dv
import window_manager as wm

MM_LEFT = dv.MM_LEFT_CORNER   # левый угол ромба миникарты (из driver)

try:
    if dv.abort_requested():
        print("СТОП: включён ScrollLock."); sys.exit(0)
    dv.ensure_focus()
    dv.clear_popups()
    dv.goto_own_state()                 # в свой штат + макс-зум
    w = dv.ensure_focus()
    print("клик по миникарте:", (w.left + MM_LEFT[0], w.top + MM_LEFT[1]))
    dv.safe_click(w.left + MM_LEFT[0], w.top + MM_LEFT[1])
    import time; time.sleep(2.2)
    img, _ = wm.capture_window(r"D:\PROJECT\TilesSurviveMap\data\720\screens\jump_result.png", settle=1.2)
    print("снимок:", img.size)
except dv.Aborted as e:
    print("ОСТАНОВЛЕНО (ScrollLock):", e)
except dv.FocusLost as e:
    print("FOCUS LOST:", e)
except Exception:
    print("ОШИБКА:\n" + traceback.format_exc())
