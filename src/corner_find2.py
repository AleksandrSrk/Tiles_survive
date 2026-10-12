"""Баг2 — стоп на границе штата через сравнение плашки штата с эталоном.
Дома (720) снимаем эталон плашки. Пан вниз-влево мелкими шагами; как только
плашка изменилась (сменился штат) — откат на шаг и стоп. Без OCR в цикле."""
import sys, time, traceback
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np, cv2
import driver as dv
import window_manager as wm

SCR = r"D:\PROJECT\TilesSurviveMap\data\720\screens"
THRESH = 10.0   # порог изменения плашки (средний abs по серому)


def plate(img):
    a = np.array(img)
    g = cv2.cvtColor(a[50:150, 10:230], cv2.COLOR_RGB2GRAY).astype(np.float32)
    return g


def diff(g1, g2):
    return float(np.abs(g1 - g2).mean())


try:
    dv.ensure_focus()
    print("домой + макс-зум...")
    dv.go_home(); dv.zoom_max()
    ref_img, _ = wm.capture_window(SCR + r"\cf_ref.png", settle=1.0)
    ref = plate(ref_img)
    print("старт: дома, 720, макс-зум; эталон плашки снят")

    hit = False
    for i in range(15):
        w = dv.ensure_focus(); L, T = w.left, w.top
        dv.safe_drag(L + 600, T + 650, L + 850, T + 500)   # вид -> вниз-влево
        time.sleep(1.4)
        img, _ = wm.capture_window(SCR + rf"\cf2_{i}.png", settle=0.5)
        d = diff(ref, plate(img))
        print(f"шаг {i}: diff плашки={d:.1f}")
        if d > THRESH:
            print("ГРАНИЦА: плашка изменилась -> сменился штат. Откат на шаг назад.")
            w = dv.ensure_focus(); L, T = w.left, w.top
            dv.safe_drag(L + 850, T + 500, L + 600, T + 650)   # обратный драг
            time.sleep(1.4)
            bimg, _ = wm.capture_window(SCR + r"\cf2_boundary.png", settle=0.8)
            print("после отката: diff плашки =", round(diff(ref, plate(bimg)), 1))
            hit = True
            break
    if not hit:
        print("за 15 шагов граница не достигнута (мелкий шаг/далеко до края)")
    print("done")
except dv.FocusLost as e:
    print("FOCUS LOST — ввод прерван:", e)
except Exception:
    print("ОШИБКА:\n" + traceback.format_exc())
