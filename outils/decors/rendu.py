"""Rend un SVG en image HD (Chromium), ajoute un grain de peinture léger, écrit .webp et un aperçu .png"""
import sys, asyncio, io, os
import numpy as np
from PIL import Image
from playwright.async_api import async_playwright
svg, sortie = sys.argv[1], sys.argv[2]
grain = float(sys.argv[3]) if len(sys.argv) > 3 else 3.0
async def main():
    s = open(svg, encoding='utf-8').read()
    import re
    W, H = map(int, re.search(r'width="(\d+)" height="(\d+)"', s).groups())
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': W, 'height': H})
        await pg.set_content('<html><body style="margin:0;background:#000">' + s + '</body></html>')
        await pg.wait_for_timeout(300)
        png = await pg.screenshot(clip={'x': 0, 'y': 0, 'width': W, 'height': H})
        await b.close()
    im = np.asarray(Image.open(io.BytesIO(png)).convert('RGB')).astype(np.float32)
    rng = np.random.default_rng(5)
    im += rng.normal(0, grain, im.shape[:2])[..., None]
    out = Image.fromarray(np.clip(im, 0, 255).astype(np.uint8))
    out.save(sortie, quality=84, method=6)
    out.resize((W // 3, H // 3), Image.LANCZOS).save(os.path.splitext(sortie)[0] + '_apercu.png')
    print(sortie, out.size, os.path.getsize(sortie) // 1024, 'Ko')
asyncio.run(main())
