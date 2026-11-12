"""Split output for large books ("split": true in data/library.json).

The book's index.html keeps only the contents, the home view and an empty
<section> per chapter; each chapter's body is written to <slug>/c/<cid>.html
and fetched by reader.js when the chapter is opened.  The drawer goes to
<slug>/gloss.html (fetched on first use) and the search index to
<slug>/search.json (fetched on first search).  <slug>/ids.json maps the
anchors that do not name their chapter (#p70, #l5-agreement …) to it; ids of
the form <cid>-s3 / <cid>-u12 name their chapter themselves.

The search index holds the same units, in the same order, that reader.js
collects from the page for an unsplit book (see the selector in reader.js);
the units without an id get <cid>-uN here so that a hit can be routed.
"""
import json
import os
import re

import lxml.html

UNIT_CLASSES = ('pgroup', 'tbl', 'vocab', 'ex')


def _cls(e):
    return set((e.get('class') or '').split())


def _has_anc(e, pred):
    p = e.getparent()
    while p is not None:
        if pred(p):
            return True
        p = p.getparent()
    return False


def _is_unit(e):
    """reader.js: 'p.para:not(.pgroup p), .pgroup, .tbl, h3.sec, h4.sub, .vocab li, ol.ex li,
    .vocab, .ex, ol.lst li, p.pcap'"""
    if not isinstance(e.tag, str):
        return False
    c, t = _cls(e), e.tag
    if t == 'p' and 'para' in c and not _has_anc(e, lambda a: 'pgroup' in _cls(a)):
        return True
    if c & {'pgroup', 'tbl', 'vocab', 'ex', 'brace'}:
        return True
    if (t == 'h3' and 'sec' in c) or (t == 'h4' and 'sub' in c) or (t == 'p' and 'pcap' in c):
        return True
    if t == 'li' and _has_anc(e, lambda a: 'vocab' in _cls(a) or (a.tag == 'ol' and ('ex' in _cls(a) or 'lst' in _cls(a)))):
        return True
    return False


def _text(el):
    """text_content() without the chips to the other books (a.xb)."""
    out = [el.text or '']
    for ch in el:
        if isinstance(ch.tag, str) and 'xb' not in _cls(ch):
            out.append(_text(ch))
        out.append(ch.tail or '')
    return ''.join(out)


def _ref(el, sign):
    if el.get('data-ref'):          # anchors that name themselves ("p. 12", "Mātikā d7", "note 204"), as in reader.js
        return el.get('data-ref')
    for ch in el:
        if isinstance(ch.tag, str) and 'pnum' in _cls(ch):
            return sign + ch.text_content()
        if isinstance(ch.tag, str) and 'sechead' in _cls(ch):
            for g in ch:
                if isinstance(g.tag, str) and 'pnum' in _cls(g):
                    return sign + g.text_content()
    return sign + re.sub(r'^[a-z]+', '', el.get('id'))


def write_split(outdir, parts, gloss_html, anchor, sign):
    anchor_re = re.compile(anchor)
    cdir = os.path.join(outdir, 'c')
    os.makedirs(cdir, exist_ok=True)
    for f in os.listdir(cdir):
        if f.endswith('.html'):
            os.remove(os.path.join(cdir, f))
    ids, chs, units = {}, [], []
    for ci, (cid, label, title, body) in enumerate(parts):
        chs.append([label, title])
        root = lxml.html.fromstring('<div>' + body + '</div>')
        last = None
        k = 0
        for el in root.iter():
            if el is root or not isinstance(el.tag, str):
                continue
            if el.get('id') and anchor_re.search(el.get('id')):
                last = el
            if not _is_unit(el):
                continue
            c = _cls(el)
            if c & {'vocab', 'ex'} and not c & {'tbl', 'pgroup'} and el.tag != 'li':
                continue            # containers only mark the position
            if not el.get('id'):
                el.set('id', f'{cid}-u{k}')
                k += 1
            txt = re.sub(r'\s+', ' ', _text(el)).strip()
            units.append([ci, el.get('id'), txt] + ([_ref(last, sign)] if last is not None else []))
        for el in root.iter():
            i = isinstance(el.tag, str) and el.get('id')
            if i and not re.fullmatch(re.escape(cid) + r'-[su]\d+', i):
                ids[i] = cid
        html = (root.text or '') + ''.join(lxml.html.tostring(ch, encoding='unicode') for ch in root)
        with open(os.path.join(cdir, cid + '.html'), 'w', encoding='utf-8') as f:
            f.write(html)
    with open(os.path.join(outdir, 'ids.json'), 'w', encoding='utf-8') as f:
        json.dump(ids, f, ensure_ascii=False, separators=(',', ':'))
    with open(os.path.join(outdir, 'search.json'), 'w', encoding='utf-8') as f:
        json.dump({'ch': chs, 'u': units}, f, ensure_ascii=False, separators=(',', ':'))
    with open(os.path.join(outdir, 'gloss.html'), 'w', encoding='utf-8') as f:
        f.write(gloss_html)
