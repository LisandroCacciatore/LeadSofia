from playwright.sync_api import sync_playwright
import pathlib, re, json
UA=("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
out=pathlib.Path("00-auditoria"); res={}
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome", headless=True)
    ctx=b.new_context(locale="es-AR", user_agent=UA, viewport={"width":430,"height":900})
    pg=ctx.new_page()
    for name,u in [("wa_asesoria","https://wa.me/p/23924291647213034/5493416153151"),
                   ("wa_colorimetria","https://wa.me/p/25673960648860647/5493416153151"),
                   ("wa_link","https://wa.link/xii63u")]:
        try:
            pg.goto(u, wait_until="domcontentloaded", timeout=45000); pg.wait_for_timeout(6000)
            t=pg.inner_text("body")
            res[name]={"url":pg.url,"title":pg.title(),"texto":t[:900]}
            pg.screenshot(path=str(out/f"{name}.png"))
            print("="*60); print(name, "->", pg.url); print(t[:700])
        except Exception as e:
            res[name]={"error":str(e)[:150]}; print("ERR",name,str(e)[:150])
    # TikTok real: perfil por handle correcto
    for name,u in [("tt_ok","https://www.tiktok.com/@sofiastrafile"),
                   ("tt_busqueda","https://www.tiktok.com/search?q=sofia%20strafile")]:
        try:
            pg.goto(u, wait_until="domcontentloaded", timeout=45000); pg.wait_for_timeout(8000)
            t=pg.inner_text("body")
            res[name]={"url":pg.url,"title":pg.title(),"texto":t[:900]}
            pg.screenshot(path=str(out/f"{name}.png"))
            print("="*60); print(name, "->", pg.title()); print(t[:500])
        except Exception as e:
            res[name]={"error":str(e)[:150]}; print("ERR",name,str(e)[:150])
    (out/"wa-tiktok.json").write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding="utf-8")
    b.close()
