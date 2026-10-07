from playwright.sync_api import sync_playwright
import pathlib, json
UA=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
out=pathlib.Path("00-auditoria"); res={}
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome", headless=True)
    ctx=b.new_context(locale="es-AR", viewport={"width":1440,"height":1000}, user_agent=UA)
    pg=ctx.new_page()
    # 1) TikTok via busqueda general (ahi aparece el bloque Usuarios)
    for i in range(2):
        try:
            pg.goto("https://www.tiktok.com/search?q=sofia%20strafile", wait_until="domcontentloaded", timeout=60000)
            pg.wait_for_timeout(9000)
            t=pg.inner_text("body")
            if "Seguidores" in t and "Usuarios" in t:
                break
        except Exception as e:
            t=f"ERR {e}"
    (out/"tiktok-busqueda.txt").write_text(t, encoding="utf-8")
    pg.screenshot(path=str(out/"tiktok-busqueda.png"))
    print("=== TIKTOK (bloque Usuarios) ===")
    i=t.find("Usuarios"); print(t[i:i+300] if i>=0 else t[:300])
    # 2) Google SERP por su nombre
    pg.goto("https://www.google.com/search?q=%22Sof%C3%ADa+Strafile%22&hl=es&gl=ar&num=20",
            wait_until="domcontentloaded", timeout=60000)
    pg.wait_for_timeout(5000)
    gt=pg.inner_text("body")
    (out/"google-serp.txt").write_text(gt, encoding="utf-8")
    pg.screenshot(path=str(out/"google-serp.png"))
    print("\n=== GOOGLE: \"Sofía Strafile\" ===")
    print(gt[:1500])
    b.close()
