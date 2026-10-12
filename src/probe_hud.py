"""Шаг 1: проверка, читает ли OCR верхний HUD (#штат X:.. Y:..).
Берём playermap-скрины, режем верхнюю полосу, прогоняем easyocr,
regex-ом достаём штат/X/Y и сравниваем с тем, что зашито в имени файла."""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import re
from pathlib import Path
import easyocr
from PIL import Image
import numpy as np

SAMPLES = Path(r"D:\PROJECT\TilesSurviveMap\samples")
LOG = Path(r"D:\PROJECT\TilesSurviveMap\hud_test_result.txt")

EXPECT = {
    "playermap_720_x123_y1201": (720, 123, 1201),
    "playermap_720_x122_y1203": (720, 122, 1203),
    "playermap_720_x131_y1201": (720, 131, 1201),
    "playermap_720_x131_y1201_zoom": (720, 131, 1201),
}

print("Инициализация easyocr (первый раз качает модели, тихо)...", flush=True)
reader = easyocr.Reader(["en"], gpu=False, verbose=False)
print("Reader готов.\n", flush=True)

PAT = re.compile(r"#?\s*(\d{3,4}).{0,12}?X[:\s]*(\d+).{0,6}?Y[:\s]*(\d+)", re.I)
lines_out = []

for name, exp in EXPECT.items():
    f = SAMPLES / f"{name}.png"
    img = Image.open(f).convert("RGB")
    W, H = img.size
    band = img.crop((0, 0, W, int(H * 0.075)))
    band = band.resize((band.width * 2, band.height * 2))
    res = reader.readtext(np.array(band), detail=0)
    joined = " ".join(res)
    m = PAT.search(joined)
    got = (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None
    ok = "OK " if got == exp else "FAIL"
    block = (f"[{ok}] {name}  size={W}x{H}\n"
             f"      ожидали: штат{exp[0]} X{exp[1]} Y{exp[2]}\n"
             f"      распозн: {got}\n"
             f"      сырьё  : {res}\n")
    print(block, flush=True)
    lines_out.append(block)

LOG.write_text("\n".join(lines_out), encoding="utf-8")
print("Результат также сохранён:", LOG)
