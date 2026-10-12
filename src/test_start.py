"""Тест полного старта: окно к эталону -> возврат в 720 -> нижне-левый угол.
Юзер меняет угол/зум/размер/позицию окна перед запуском."""
import sys, traceback
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import driver as dv
import window_manager as wm

try:
    if dv.abort_requested():
        print("СТОП: включён ScrollLock — выключи его."); sys.exit(0)
    res = dv.start_position()
    print("start_position:", res)
    img, _ = wm.capture_window(r"D:\PROJECT\TilesSurviveMap\data\720\screens\start_corner.png", settle=1.0)
    print("снимок:", img.size)
except dv.Aborted as e:
    print("ОСТАНОВЛЕНО (ScrollLock):", e)
except dv.FocusLost as e:
    print("FOCUS LOST:", e)
except Exception:
    print("ОШИБКА:\n" + traceback.format_exc())
