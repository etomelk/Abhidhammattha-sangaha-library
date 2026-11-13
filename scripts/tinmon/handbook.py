"""Join the two volumes of U Sīlānanda's Handbook of Abhidhamma Studies into data/handbook.json:

python3 scripts/tinmon/convert.py work/handbook-1.txt handbook1
python3 scripts/tinmon/convert.py work/handbook-2.txt handbook2
python3 scripts/tinmon/handbook.py

Volume I: front matter and Introduction, Chapters One–Three (Three only Vedanā, Hetu and Kicca);
Volume II: front matter, Chapters Four–Six. Each part's label names its volume."""
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
chapters = []
for vol, slug in (('I', 'handbook1'), ('II', 'handbook2')):
    f = os.path.join(ROOT, 'data', f'{slug}.json')
    for c in json.load(open(f, encoding='utf-8'))['chapters']:
        c['label'] = f'Vol. {vol} · ' + (c['label'] if c['label'] != 'Front matter' else 'Front matter')
        c['num'] = str(len(chapters))
        chapters.append(c)
    os.remove(f)
json.dump(dict(chapters=chapters, glossary=[]), open(os.path.join(ROOT, 'data', 'handbook.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('wrote data/handbook.json:', len(chapters), 'parts')
