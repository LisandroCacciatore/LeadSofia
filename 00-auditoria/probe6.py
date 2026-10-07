from playwright.sync_api import sync_playwright
import pathlib
UA=("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
out=pathlib.Path("00-auditoria")
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome", headless=True)
    ctx=b.new_context(locale="es-AR", user_agent=UA, viewport={"width":430,"height":1400})
    pg=ctx.new_page()
    pg.goto("https://linktr.ee/sofia.strafile", wait_until="domcontentloaded", timeout=60000)
    pg.wait_for_timeout(7000)
    t=pg.inner_text("body")
    out.joinpath("linktree-texto.txt").write_text(t,encoding="utf-8")
    pg.screenshot(path=str(out/"linktree.png"), full_page=True)
    print(t[:2000])
    b.close()
