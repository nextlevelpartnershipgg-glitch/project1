from PIL import Image, ImageDraw, ImageFont
import textwrap, os, random

FONT_PATHS = [
    "assets/fonts/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

def _find_font():
    for p in FONT_PATHS:
        if os.path.exists(p):
            return p
    return None

def make_news_cover(headline: str, trend: str|None=None, outfile: str="cover.jpg") -> str:
    W,H = 1200, 675
    img = Image.new("RGB", (W,H), (20,20,28))
    draw = ImageDraw.Draw(img)

    # сетка
    for x in range(80, W-40, 40):
        draw.line([(x,100),(x,H-120)], fill=(40,40,50), width=1)
    for y in range(120, H-120, 40):
        draw.line([(80,y),(W-40,y)], fill=(40,40,50), width=1)

    # трендовая линия
    if trend in ("up","down"):
        pts = [(80, H-180)]
        for k in range(12):
            dy = random.randint(10,45) * (-1 if trend=="down" else 1)
            last = pts[-1]
            x = 80 + (k+1)*((W-120)//12)
            y = max(120, min(H-180, last[1]-dy))
            pts.append((x,y))
        draw.line(pts, fill=(220,220,220), width=5)

    # заголовок
    font_path = _find_font()
    font = ImageFont.truetype(font_path, 56) if font_path else None
    wrapped = "\n".join(textwrap.wrap(headline, width=28))
    draw.text((90, H-240), wrapped, font=font, fill=(245,245,245))
    img.save(outfile)
    return outfile
