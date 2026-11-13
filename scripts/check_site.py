#!/usr/bin/env python3
"""Load every page of the site in Chromium at 320, 400 and 1300 px and report horizontal
overflow (anything wider than the viewport), broken internal links among those visited,
and console errors.  Serves the repository on a local port.

    python3 scripts/check_site.py [--shots DIR]
"""
import http.server
import json
import os
import socketserver
import sys
import threading

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIDTHS = (320, 400, 1300)


def serve():
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    handler = lambda *a, **k: Quiet(*a, directory=ROOT, **k)
    httpd = socketserver.TCPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, httpd.server_address[1]


OVERFLOW_JS = """() => {
  const W = document.documentElement.clientWidth, bad = [];
  if (document.documentElement.scrollWidth > W + 1) bad.push('page scrollWidth ' + document.documentElement.scrollWidth);
  for (const el of document.querySelectorAll('main *, .topbar *')) {
    const r = el.getBoundingClientRect();
    if (r.width && r.right > W + 1 && getComputedStyle(el).position !== 'fixed' && !el.closest('.toc,.gloss,[hidden]')) {
      bad.push((el.className || el.tagName) + ' right=' + Math.round(r.right) + ' ' + (el.textContent || '').trim().slice(0, 40));
      if (bad.length > 6) break;
    }
  }
  return bad;
}"""


def main():
    shots = sys.argv[sys.argv.index('--shots') + 1] if '--shots' in sys.argv else None
    httpd, port = serve()
    base = f'http://127.0.0.1:{port}/'
    lib = json.load(open(os.path.join(ROOT, 'data', 'library.json'), encoding='utf-8'))
    urls = [base, base + 'references/'] + [base + d + '/' for d in ('map', 'charts') if os.path.exists(os.path.join(ROOT, d, 'index.html'))]
    for b in lib['books']:
        urls.append(base + b['slug'] + '/')
        data = json.load(open(os.path.join(ROOT, 'data', b['slug'] + '.json'), encoding='utf-8'))
        cid = b.get('cid', 'ch')
        urls += [base + b['slug'] + '/#' + cid + c['num'] for c in data['chapters']]
    problems = 0
    with sync_playwright() as p:
        br = p.chromium.launch()
        for w in WIDTHS:
            ctx = br.new_context(viewport={'width': w, 'height': 800})
            page = ctx.new_page()
            errs = []
            page.on('console', lambda m: errs.append(m.text + ' @ ' + page.url) if m.type == 'error' and 'TUNNEL' not in m.text else None)
            page.on('pageerror', lambda e: errs.append(str(e)))
            page.on('response', lambda r: errs.append(f'HTTP {r.status} {r.url}') if r.status >= 400 else None)
            for u in urls:
                page.goto(u)
                page.wait_for_timeout(350)
                bad = page.evaluate(OVERFLOW_JS)
                if bad:
                    problems += 1
                    print(f'{w}px {u[len(base)-1:]}: overflow', '; '.join(bad))
                if shots and w in (320, 1300):
                    name = (u[len(base):].replace('/', '_').replace('#', '-') or 'home') + f'-{w}.png'
                    page.screenshot(path=os.path.join(shots, name))
            for e in errs:
                problems += 1
                print(f'{w}px console error: {e}')
            ctx.close()
        br.close()
    httpd.shutdown()
    print(f'{len(urls)} pages x {len(WIDTHS)} widths, {problems} problems')
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main()
