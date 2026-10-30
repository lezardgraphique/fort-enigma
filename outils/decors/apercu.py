import asyncio, base64, sys
from playwright.async_api import async_playwright
b64 = base64.b64encode(open('out/accueil_nuit_L.webp','rb').read()).decode()
html = f'''<html><body style="margin:0"><div style="width:1200px;height:630px;position:relative;overflow:hidden;font-family:'TeX Gyre Pagella',serif;
background:url(data:image/webp;base64,{b64}) 18% 40%/1400px auto no-repeat">
<div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(5,8,24,0) 30%,rgba(5,8,24,.78) 62%)"></div>
<div style="position:absolute;right:60px;top:0;bottom:0;width:560px;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;color:#f4d03f">
<div style="font-size:74px;font-weight:700;letter-spacing:.03em;white-space:nowrap;text-shadow:0 0 30px rgba(244,208,63,.55),0 3px 8px #000">FORT ÉNIGMA</div>
<div style="font-size:30px;letter-spacing:.35em;margin-top:8px;color:#ffe08a">L'APPEL DU GARDIEN</div>
<div style="font-size:24px;margin-top:26px;color:#dfe6ff;font-style:italic">Franchis la porte du Fort · 10 mondes · un coffre à ouvrir</div></div></div></body></html>'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width':1200,'height':630})
        await pg.set_content(html); await pg.wait_for_timeout(300)
        await pg.screenshot(path=sys.argv[1], type='jpeg', quality=88); await b.close()
asyncio.run(main())
