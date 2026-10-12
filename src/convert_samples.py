"""Одноразовая утилита: webp -> png с осмысленными именами.
Категории: playermap (режим игроков, есть X:Y), territory (земли, слой А),
card (UI-карточки для сводки), misc (экран сбора союза)."""
from pathlib import Path
from PIL import Image

SAMPLES = Path(r"D:\PROJECT\TilesSurviveMap\samples")

RENAME = {
    "1791535104492": "playermap_720_x123_y1201",
    "1791535647768": "playermap_720_x122_y1203",
    "1791536366392": "playermap_720_x131_y1201",
    "1791536376154": "playermap_720_x131_y1201_zoom",
    "1791535025985": "territory_720_a",
    "1791535919593": "territory_720_b",
    "1791535934670": "territory_719_preview",
    "1791536310558": "territory_719_far",
    "1791535122976": "card_player_endeavour",
    "1791535146275": "card_showcase_endeavour",
    "1791535156454": "card_alliance_one",
    "1791535045570": "misc_rally_far",
    "1791535059141": "misc_rally_mid",
    "1791535073002": "misc_rally_near",
}

done, skipped = [], []
for f in sorted(SAMPLES.glob("*.webp")):
    key = f.stem.split("_")[0]
    new = RENAME.get(key)
    if not new:
        skipped.append(f.name)
        continue
    Image.open(f).convert("RGB").save(SAMPLES / f"{new}.png", "PNG")
    f.unlink()
    done.append(f"{new}.png")

print("CONVERTED:")
for d in sorted(done):
    print(" ", d)
if skipped:
    print("SKIPPED (неизвестные):", skipped)
print("TOTAL:", len(done))
