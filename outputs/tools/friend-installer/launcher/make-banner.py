import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB')
W, H = im.size
# Dark band at the bottom so the title reads over any picture.
grad = Image.new('L', (1, H))
for y in range(H):
    t = max(0.0, (y - H * 0.45) / (H * 0.55))
    grad.putpixel((0, y), int(235 * t ** 1.4))
im = Image.composite(Image.new('RGB', (W, H), (8, 6, 10)), im, grad.resize((W, H)))
d = ImageDraw.Draw(im)
big = ImageFont.truetype(r'C:\Windows\Fonts\bahnschrift.ttf', 96); big.set_variation_by_name('Bold')
small = ImageFont.truetype(r'C:\Windows\Fonts\bahnschrift.ttf', 64); small.set_variation_by_name('SemiBold Condensed')
title, tag = 'FRACTURED GALAXY', 'S  W  G'
tw = d.textlength(title, font=big); x = (W - tw) / 2; y = H - 150
glow = Image.new('L', (W, H)); g = ImageDraw.Draw(glow)
g.text((x, y), title, font=big, fill=255)
glow = glow.filter(ImageFilter.GaussianBlur(14))
im = Image.composite(Image.new('RGB', (W, H), (200, 30, 20)), im, glow.point(lambda v: int(v * 0.85)))
d = ImageDraw.Draw(im)
d.text((x, y), title, font=big, fill=(245, 236, 220), stroke_width=2, stroke_fill=(40, 8, 6))
sw = d.textlength(tag, font=small)
d.text(((W - sw) / 2, y - 66), tag, font=small, fill=(240, 170, 70), stroke_width=2, stroke_fill=(40, 8, 6))
im.save(out)
