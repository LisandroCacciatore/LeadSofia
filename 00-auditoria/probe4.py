from playwright.sync_api import sync_playwright
import pathlib, json
UA=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
out=pathlib.Path("00-auditoria")
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome", headless=True)
    ctx=b.new_context(locale="es-AR", viewport={"width":1440,"height":1000}, user_agent=UA)
    pg=ctx.new_page()
    pg.goto("https://www.tiktok.com/search/user?q=sofia%20strafile", wait_until="domcontentloaded", timeout=60000)
    pg.wait_for_timeout(9000)
    t=pg.inner_text("body")
    (out/"tiktok-busqueda.txt").write_text(t, encoding="utf-8")
    pg.screenshot(path=str(out/"tiktok-busqueda.png"))
    print("--- search/user ---"); print(t[:900])
    b.close()
