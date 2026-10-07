from playwright.sync_api import sync_playwright
import re, pathlib, json
UA=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
url="https://www.instagram.com/reel/DdXa36gDRhT/"
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome", headless=True)
    ctx=b.new_context(locale="es-AR", viewport={"width":1440,"height":1000}, user_agent=UA)
    pg=ctx.new_page()
    pg.goto(url, wait_until="domcontentloaded", timeout=60000)
    pg.wait_for_timeout(9000)
    html=pg.content()
    pathlib.Path("00-auditoria/probe-post.html").write_text(html,encoding="utf-8")
    for pat in [r'"like_count":\s*\d+', r'"comment_count":\s*\d+', r'"edge_media_preview_like":\{[^}]{0,120}',
                r'og:description"[^>]*content="([^"]{0,200})', r'name="description"[^>]*content="([^"]{0,200})']:
        ms=re.findall(pat,html)
        print(pat[:40],"->",ms[:4] if ms else "NONE")
    txt=pg.inner_text("body")
    print("---- body head ----")
    print(txt[:600])
    b.close()
