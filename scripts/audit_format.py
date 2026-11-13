#!/usr/bin/env python3
"""Look through every book of the library for the faults that text taken from PDFs is prone to, and
print a count per book and kind, with examples:

python3 scripts/audit_format.py            # summary
python3 scripts/audit_format.py guide      # one book, all examples

lone     a paragraph that is only punctuation or a stray brace ("}", "|", ")")
spaced   a list number written apart from its point ("1 . eye")
broken   a paragraph that ends without punctuation and is followed by one that starts in lower case
         (one paragraph cut in two)
hyphen   a paragraph that ends in a hyphen
smallpre a "table" of one or two short lines that is really a line of text
sentence a heading that is a sentence (long, or ending in a full stop)
empty    an empty paragraph or heading
dup      a paragraph repeated right after itself
letters  a word broken into letters (P A Ṭ Ṭ H Ā N A)
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def audit(slug):
    d = json.load(open(os.path.join(ROOT, 'data', f'{slug}.json'), encoding='utf-8'))
    out = {}

    def hit(kind, ch, text):
        out.setdefault(kind, []).append(f'{ch["label"]}: {text[:110]}')
    for ch in d['chapters']:
        bl = ch['blocks']
        for i, b in enumerate(bl):
            t = b.get('text', '') if isinstance(b.get('text'), str) else ''
            if b['type'] in ('p', 'h', 'h4') and not t.strip() and not b.get('pnum'):
                hit('empty', ch, repr(t))
            if b['type'] == 'p' and t and t != '* * *' and re.fullmatch(r'[\s{}()\[\]|.,;:•*–—-]+', t):
                hit('lone', ch, t)
            if b['type'] == 'p' and re.match(r'^\(?\d{1,2} \.\s', t):
                hit('spaced', ch, t)
            if b['type'] == 'p' and not b.get('note') and t.endswith('-') and not re.search(r'[:—-]-$', t):
                hit('hyphen', ch, t[-80:])
            if b['type'] == 'pre':
                ls = [l for l in t.split('\n') if l.strip()]
                if len(ls) <= 2 and all(len(re.findall(r'\S {3,}\S', l.strip())) <= 1 for l in ls) and sum(len(l.split()) for l in ls) >= 8:
                    hit('smallpre', ch, ' / '.join(l.strip() for l in ls))
            if b['type'] in ('h', 'h4') and (len(t) > 110 or (re.search(r'[a-z]\.$', t) and len(t.split()) > 6)):
                hit('sentence', ch, t)
            if b['type'] == 'p' and i + 1 < len(bl) and bl[i + 1]['type'] == 'p' and not b.get('note') and not bl[i + 1].get('note') \
                    and not b.get('ind') and not bl[i + 1].get('ind') and not b.get('pnum') and not bl[i + 1].get('pnum'):
                n = bl[i + 1].get('text', '')
                if t and n and re.search(r'[a-z,]$', t) and re.match(r'^[a-z]', n):
                    hit('broken', ch, t[-50:] + ' ‖ ' + n[:50])
                if t and t == n and len(t) > 20:
                    hit('dup', ch, t)
            if re.search(r'\b[A-ZĀĪŪṬḌṆṄ] [A-ZĀĪŪṬḌṆṄ] [A-ZĀĪŪṬḌṆṄ] [A-ZĀĪŪṬḌṆṄ]\b', t) and b['type'] != 'pre':
                hit('letters', ch, t)
    return out


def main():
    lib = json.load(open(os.path.join(ROOT, 'data', 'library.json'), encoding='utf-8'))
    slugs = [sys.argv[1]] if len(sys.argv) > 1 else [b['slug'] for b in lib['books']]
    kinds = ['lone', 'spaced', 'broken', 'hyphen', 'smallpre', 'sentence', 'empty', 'dup', 'letters']
    print(f'{"book":12}' + ''.join(f'{k:>9}' for k in kinds))
    res = {s: audit(s) for s in slugs}
    for s in slugs:
        print(f'{s:12}' + ''.join(f'{len(res[s].get(k, [])):>9}' for k in kinds))
    for s in slugs:
        for k in kinds:
            ex = res[s].get(k, [])
            if ex:
                print(f'\n[{s} · {k}] {len(ex)}')
                for e in ex[:(len(ex) if len(slugs) == 1 else 4)]:
                    print('   ', e)


if __name__ == '__main__':
    main()
