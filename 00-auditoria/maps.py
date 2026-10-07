from playwright.sync_api import sync_playwright
import re, json, pathlib
UA=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
out=pathlib.Path("00-auditoria")
res={}
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome", headless=True)
    ctx=b.new_context(locale="es-AR", viewport={"width":1440,"height":1000}, user_agent=UA)
    pg=ctx.new_page()
    for nombre,q in [("strafile","Sofía Strafile asesora de imagen"),
                     ("sofia_asesora","Sofía asesora de imagen personal shopping Buenos Aires")]:
        url="https://www.google.com/maps/search/"+q.replace(" ","+")+"/"
        try:
            pg.goto(url, wait_until="domcontentloaded", timeout=60000)
            pg.wait_for_timeout(7000)
            txt=pg.inner_text("body")
            res[nombre]={"url":pg.url,"title":pg.title(),"texto":txt[:2500]}
            pg.screenshot(path=str(out/f"maps-{nombre}.png"))
        except Exception as e:
            res[nombre]={"error":str(e)[:200]}
        print("="*70); print(nombre, "->", res[nombre].get("title"), "|", res[nombre].get("url"))
        print((res[nombre].get("texto") or res[nombre].get("error",""))[:1200])
    b.close()
(out/"maps.json").write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding="utf-8")
