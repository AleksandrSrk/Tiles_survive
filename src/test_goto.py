"""Тест возврата в свой штат по иконке кнопки 'Предпросмотр'.
Старт: чужой штат -> должны отдалиться, поймать иконку, кликнуть, вернуться в 720."""
import sys, traceback
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import driver as dv
import window_manager as wm

try:
    if dv.abort_requested():
        print("СТОП: включён ScrollLock — выключи его и запусти снова."); sys.exit(0)
    dv.ensure_focus()
    print("гашу попапы..."); dv.clear_popups()
    ok = dv.goto_own_state()
    print(f"goto_own_state: в своём штате (кнопки нет) = {ok}")
    img, _ = wm.capture_window(r"D:\PROJECT\TilesSurviveMap\data\720\screens\goto_result.png", settle=1.0)
    print("снимок:", img.size)
except dv.Aborted as e:
    print("ОСТАНОВЛЕНО пользователем (ScrollLock):", e)
except dv.FocusLost as e:
    print("FOCUS LOST — ввод прерван:", e)
except Exception:
    print("ОШИБКА:\n" + traceback.format_exc())
