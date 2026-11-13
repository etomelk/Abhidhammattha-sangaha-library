"""Put the Pāli diacritics back into the OCR of Nārada's Chapter VIII (from the 1956–57 edition,
Buddha Sāsana Council reprint, Rangoon 1970), as a draft for the proofread against the page images:

python3 scripts/narada/restore.py work/n8/pg-374.txt …  > work/n8/draft.txt

Tesseract reads the print's ā as d / a / 4, ṁ as m, ñ as fi / ii, and drops the dots of ṭ ṇ ḷ.
Each word of the OCR is compared, without its diacritics, with the words of the Pāli books of this
library (the Saṅgaha, the Vibhāvinī, the Paramatthadīpanī, the Anudīpanī, Nārada's other chapters):
where exactly one Pāli word fits (the most frequent one if several spellings fit), it replaces the OCR
word. English words (by their frequency in English) are left alone. The print writes ṁ; the library
writes ṃ."""
import collections
import itertools
import json
import os
import re
import sys
import unicodedata

from wordfreq import zipf_frequency

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
PALI = 'āīūṃṅñṭḍṇḷ'


def bare(w):
    w = unicodedata.normalize('NFD', w.lower())
    return ''.join(c for c in w if unicodedata.category(c) != 'Mn')


def lexicon():
    freq = collections.Counter()
    for slug in ('sangaha', 'vibhavini', 'paramattha', 'anudipani', 'narada', 'tinmon', 'guide', 'handbook'):
        d = json.load(open(os.path.join(ROOT, 'data', f'{slug}.json'), encoding='utf-8'))
        for c in d['chapters']:
            for b in c['blocks']:
                for w in re.findall(r'[a-zA-Zāīūṃṅñṭḍṇḷ]+', b.get('text', '') or ''):
                    # every word of the Pāli books; from the English books only the words with diacritics
                    if slug in ('sangaha', 'vibhavini', 'paramattha', 'anudipani') or any(ch in PALI for ch in w.lower()):
                        freq[w.lower()] += 1
    idx = collections.defaultdict(list)
    for w, n in freq.items():
        idx[bare(w)].append((n, w))
    return idx


def variants(tok):
    """the bare forms the OCR word may stand for: d/4/é → a (ā), fi/ii → nn (ññ), rn → m"""
    t = tok.lower()
    t = t.replace('é', 'a').replace('á', 'a').replace('4', 'a').replace('ā', 'a')
    t = re.sub(r'fi|ii|ﬁ', 'nn', t)
    out = {t}
    ds = [m.start() for m in re.finditer('d', t)]
    if len(ds) <= 4:
        for k in range(1, len(ds) + 1):
            for comb in itertools.combinations(ds, k):
                s = list(t)
                for p in comb:
                    s[p] = 'a'
                out.add(''.join(s))
    return out


def restore(text, idx):
    def fix(m):
        tok = m.group(0)
        z = zipf_frequency(tok.lower(), 'en')
        if len(tok) < 3 or z > 3.5 or (z > 2.5 and not re.search(r'[dé4]$', tok)):
            return tok
        best = None
        for v in variants(tok):
            for n, w in idx.get(v, []):
                if best is None or n > best[0]:
                    best = (n, w)
        if not best:
            return tok
        w = best[1]
        if tok[0].isupper():
            w = w[0].upper() + w[1:]
        return w
    return re.sub(r"[A-Za-zāīūṃṅñṭḍṇḷéá4]+", fix, text)


def main(files):
    idx = lexicon()
    for f in files:
        t = open(f, encoding='utf-8').read()
        print(f'=== {os.path.basename(f)}')
        print(restore(t, idx))


if __name__ == '__main__':
    main(sys.argv[1:])
