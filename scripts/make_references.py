"""Write data/references.json: the reference list of the Abhidhammattha-saṅgaha Library, grouped
by area. The list is the library's own (no source list, so nothing is marked added). The works
that are books in this library link to their readers (lib=)."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AREAS = [
    ('editions', 'Editions of the text', 'The Pāli of the Abhidhammatthasaṅgaha and of its commentaries.'),
    ('translations', 'Translations', 'The Saṅgaha, and the Vibhāvinī, in English.'),
    ('studies', 'Studies and introductions', 'Guides to the Saṅgaha and to Theravāda Abhidhamma thought.'),
    ('reference', 'Reference works', 'Dictionaries and the online Tipiṭaka used alongside the text.'),
]

R = []
def add(area, authors, year, title, where='', url='', lib='', found='', label='', added=False):
    """url: a link given in a source list (this library has none, so it stays empty).
    found: a link located and opened for this library — a public-domain scan (Scan), an
    open-access article (Article), a lending-library copy (Borrow), the publisher's or
    author's own page (Publisher), or a free online resource published by its makers
    (Online); label says which. lib: the slug of a book in this library (Read here)."""
    d = dict(area=area, authors=authors, year=year, title=title, where=where, url=url, lib=lib, found=found, label=label)
    if added:
        d['added'] = True       # not used here: the list has no source list to be added to
    R.append(d)

# --- Editions of the text
add('editions', 'Anuruddha', 'Chaṭṭha Saṅgāyana ed.', 'Abhidhammatthasaṅgaho', 'Sixth Council text; digital edition of the Vipassana Research Institute', lib='sangaha/')
add('editions', 'Sumaṅgala', 'Chaṭṭha Saṅgāyana ed.', 'Abhidhammatthavibhāvinīṭīkā', 'Sixth Council text; digital edition of the Vipassana Research Institute', lib='vibhavini/')
add('editions', 'Ledi Sayadaw', 'Chaṭṭha Saṅgāyana ed.', 'Paramatthadīpanī (Saṅgaha-mahāṭīkā)', 'Digital edition of the Vipassana Research Institute', lib='paramattha/')
add('editions', 'Ledi Sayadaw', 'Chaṭṭha Saṅgāyana ed.', 'Anudīpanī', 'Digital edition of the Vipassana Research Institute', lib='anudipani/')
add('editions', 'Saddhātissa, H. (Ed.)', '1989', 'The Abhidhammatthasaṅgaha and the Abhidhammatthavibhāvinī-ṭīkā', 'Oxford: Pali Text Society')
add('editions', 'Kosambi, D. (Ed.)', '1941', 'Abhidhammattha Saṅgaho, with the Navanīta-ṭīkā', 'Bombay: Mahabodhi Society')

# --- Translations
add('translations', 'Shwe Zan Aung & Rhys Davids, C. A. F.', '1910', 'Compendium of philosophy, being a translation now made for the first time from the original Pali of the Abhidhammattha-sangaha', 'London: Pali Text Society')
add('translations', 'Nārada Thera', '1956', 'A manual of Abhidhamma, being Abhidhammattha Saṅgaha of Bhadanta Anuruddhācariya', 'Colombo; later editions Kandy: Buddhist Publication Society', lib='narada/')
add('translations', 'Bodhi, Bhikkhu (Gen. Ed.)', '1993', 'A comprehensive manual of Abhidhamma: The Abhidhammattha Saṅgaha of Ācariya Anuruddha', 'Kandy: Buddhist Publication Society (translation by Mahāthera Nārada, revised; guide by U Rewata Dhamma and U Sīlānanda)')
add('translations', 'Wijeratne, R. P. & Gethin, R.', '2002', 'Summary of the topics of Abhidhamma (Abhidhammatthasaṅgaha) by Anuruddha; Exposition of the topics of Abhidhamma (Abhidhammatthavibhāvinī) by Sumaṅgala', 'Oxford: Pali Text Society')

# --- Studies
add('studies', 'Sīlānanda, U', '2012', 'Handbook of Abhidhamma studies (Vols. I–II)', 'Selangor: Selangor Buddhist Vipassana Meditation Society', lib='handbook/')
add('studies', 'Rob', '2016', 'Practical Abhidhamma course (version 1.1)', 'practicalabhidhamma.com', lib='practical/')
add('studies', 'Dhammadhaja, Bhikkhu Vietnam', '2025–2026', 'Systematization of Abhidhammaṭṭha Saṅgaha', 'Na Uyana Forest Monastery, Sri Lanka (tables in the Charts of this library)', lib='charts/')
add('studies', 'Nyanaponika Thera', '1949', 'Abhidhamma studies: Researches in Buddhist psychology', 'Colombo: Frewin; 4th ed. Kandy: Buddhist Publication Society, 1998')
add('studies', 'Karunadasa, Y.', '2010', 'The Theravāda Abhidhamma: Its inquiry into the nature of conditioned reality', 'Hong Kong: Centre of Buddhist Studies, University of Hong Kong')
add('studies', 'Mehm Tin Mon', '1995', 'The essence of Buddha Abhidhamma', 'Yangon: Mya Mon Yadanar Publication')
add('studies', 'Mehm Tin Mon', 'n.d.', 'Buddha Abhidhamma: Ultimate science', 'Buddha Dharma Education Association (BuddhaNet)', lib='tinmon/')
add('studies', 'Nandamālābhivaṃsa', '2005', 'Fundamental Abhidhamma, Part I (2nd ed., rev.)', 'Sagaing: Centre for Buddhist Studies, Mahāsubodhayon Monastery', lib='fundamental/')

# --- Reference
add('studies', 'Nyanatiloka Mahāthera', '1957', 'Guide through the Abhidhamma Piṭaka (2nd rev. ed., ed. Nyanaponika; 4th ed. 2008)', 'Colombo: Bauddha Sahitya Sabha; later editions Kandy: Buddhist Publication Society', lib='guide/')
add('reference', 'Rhys Davids, T. W. & Stede, W. (Eds.)', '1921–1925', 'The Pali Text Society’s Pali–English dictionary', 'London: Pali Text Society')
add('reference', 'Nyanatiloka', '1952', 'Buddhist dictionary: Manual of Buddhist terms and doctrines', 'Colombo: Frewin; later editions Kandy: Buddhist Publication Society')
add('reference', 'Vipassana Research Institute', 'n.d.', 'The Pāḷi Tipiṭaka [Chaṭṭha Saṅgāyana edition, with the aṭṭhakathā and ṭīkā]', 'Igatpuri: Vipassana Research Institute', found='https://tipitaka.org/', label='Online')

json.dump(dict(areas=[dict(id=a, name=n, blurb=b) for a, n, b in AREAS], refs=R),
          open(os.path.join(ROOT, 'data', 'references.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(R), 'references')
