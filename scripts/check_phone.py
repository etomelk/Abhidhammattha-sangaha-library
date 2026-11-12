#!/usr/bin/env python3
"""Phone check (Pixel 5 emulation, touch): in a book, tap the menu, a part, then a section
link in the sidebar, and an entry of the "In this part" list; each tap must bring its
target to the top of the screen.  python3 scripts/check_phone.py [slug]"""
import http.server, os, socketserver, sys, threading
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
slug = sys.argv[1] if len(sys.argv) > 1 else 'muller'
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
h = socketserver.TCPServer(('127.0.0.1', 0), lambda *a, **k: Q(*a, directory=ROOT, **k))
threading.Thread(target=h.serve_forever, daemon=True).start()
base = f'http://127.0.0.1:{h.server_address[1]}/{slug}/'
fails = 0
with sync_playwright() as p:
    br = p.chromium.launch()
    ctx = br.new_context(**p.devices['Pixel 5'])
    pg = ctx.new_page()
    pg.goto(base); pg.wait_for_timeout(500)
    chaps = pg.locator('.chbtn').count()
    for k in range(chaps):
        pg.goto(base); pg.wait_for_timeout(300)
        pg.tap('#menubtn'); pg.wait_for_timeout(300)
        pg.locator('.chbtn').nth(k).tap(); pg.wait_for_timeout(700)
        cid = pg.evaluate('location.hash')
        pg.tap('#menubtn'); pg.wait_for_timeout(300)
        links = pg.locator('.chap.active .secs a')
        n = links.count()
        if not n:
            continue
        link = links.nth(n // 2)
        href = link.get_attribute('href')
        link.tap(); pg.wait_for_timeout(900)
        top = pg.evaluate(f"(()=>{{const e=document.getElementById('{href[1:]}'); return e? Math.round(e.getBoundingClientRect().top) : null}})()")
        AT_END = 'scrollY + innerHeight >= document.documentElement.scrollHeight - 2'   # a target near the end cannot reach the top
        ok1 = pg.evaluate('location.hash') == href and top is not None and (0 <= top < 160 or top >= 0 and pg.evaluate(AT_END))
        # "In this part"
        pg.evaluate('scrollTo(0,0)'); pg.wait_for_timeout(200)
        det = pg.locator('section.chapter.on details.intoc')
        ok2 = True
        if det.count():
            det.locator('summary').tap(); pg.wait_for_timeout(300)
            items = det.locator('a'); m = items.count()
            it = items.nth(m - 1); href2 = it.get_attribute('href')
            it.tap(); pg.wait_for_timeout(900)
            top2 = pg.evaluate(f"(()=>{{const e=document.getElementById('{href2[1:]}'); return e? Math.round(e.getBoundingClientRect().top) : null}})()")
            ok2 = pg.evaluate('location.hash') == href2 and top2 is not None and (0 <= top2 < 160 or top2 >= 0 and pg.evaluate(AT_END))
        print(f'{cid}: sidebar {href} {"ok" if ok1 else "FAIL top=" + str(top)}; in-this-part {"ok" if ok2 else "FAIL"}')
        fails += (not ok1) + (not ok2)
    br.close()
h.shutdown()
print('failures:', fails)
sys.exit(1 if fails else 0)
