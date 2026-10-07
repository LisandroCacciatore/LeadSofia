from playwright.sync_api import sync_playwright
import pathlib, json
UA=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
out=pathlib.Path("00-auditoria")
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome", headless=True)
    ctx=b.new_context(locale="es-AR", viewport={"width":1440,"height":1000}, user_agent=UA)
    pg=ctx.new_page()
    print("### EMBED de un post sin conteo (DdXa36gDRhT)")
    for u in ["https://www.instagram.com/p/DdXa36gDRhT/embed/captioned/",
              "https://www.instagram.com/reel/DdXa36gDRhT/embed/captioned/"]:
        try:
            pg.goto(u, wait_until="domcontentloaded", timeout=45000); pg.wait_for_timeout(5000)
            t=pg.inner_text("body")
            print(f"-- {u}\n{t[:400]}\n   [len={len(t)}]")
            out.joinpath("embed-probe.txt").write_text(u+"\n"+t[:3000],encoding="utf-8")
        except Exception as e:
            print("ERR",u,str(e)[:120])
    print("\n### TIKTOK: buscar el handle y comprobar existencia")
    for u in ["https://www.tiktok.com/@sofistrafile","https://www.tiktok.com/@sofiastrafile",
              "https://www.tiktok.com/search?q=sofia%20strafile"]:
        try:
            pg.goto(u, wait_until="domcontentloaded", timeout=45000); pg.wait_for_timeout(7000)
            print(f"-- {u}\n   title: {pg.title()}\n   body: {pg.inner_text('body')[:300]}")
        except Exception as e:
            print("ERR",u,str(e)[:120])
    b.close()
