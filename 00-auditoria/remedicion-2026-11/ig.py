import json, re
from playwright.sync_api import sync_playwright
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
out={}
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome",headless=True)
    ctx=b.new_context(viewport={"width":1440,"height":900},locale="es-AR",user_agent=UA)
    pg=ctx.new_page()
    pg.goto("https://www.instagram.com/sofiastrafile/?hl=es",wait_until="domcontentloaded",timeout=60000)
    pg.wait_for_timeout(6000)
    for _ in range(4):
        pg.mouse.wheel(0,1500); pg.wait_for_timeout(1200)
    txt=pg.evaluate("document.body.innerText")
    out["innerText"]=txt
    out["url"]=pg.url
    out["bioLinks"]=pg.evaluate("Array.from(document.querySelectorAll('header a')).map(a=>({h:a.getAttribute('href'),t:a.innerText.trim()}))")
    out["highlights"]=pg.evaluate("Array.from(document.querySelectorAll('a[href*=\"/stories/highlights/\"]')).map(a=>a.innerText.trim())")
    out["posts"]=pg.evaluate("Array.from(document.querySelectorAll('a[href*=\"/p/\"],a[href*=\"/reel/\"]')).map(a=>({href:a.getAttribute('href'),alt:a.querySelector('img')?.getAttribute('alt')||''}))")
    pg.screenshot(path=r"C:\Users\Torso\LeadSofia\00-auditoria\remedicion-2026-11\ig-perfil.png",full_page=False)
    b.close()
open(r"C:\Users\Torso\LeadSofia\00-auditoria\remedicion-2026-11\ig.json","w",encoding="utf-8").write(json.dumps(out,ensure_ascii=False,indent=1))
print(txt[:1500])
print("POSTS",len(out["posts"]))
for x in out["posts"][:15]: print(x)
print("HL",out["highlights"])
print("LINKS",out["bioLinks"][:8])
