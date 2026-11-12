#!/usr/bin/env python3
"""Write data/references.json: the reference list of the Dhammasaṅgaṇī Library, grouped
by area. The list is the library's own (there is no source list, so no entry is marked
added): every work was checked against a library catalogue, the publisher or the scan
itself. The work that is a book in this library links to its reader (lib=)."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AREAS = [
    ('editions', 'Editions of the text', 'Pāli editions of the Dhammasaṅgaṇī, of its commentary the Atthasālinī and of the Mūlaṭīkā, in Roman, Burmese and Devanāgarī script.'),
    ('translations', 'Translations', 'The Dhammasaṅgaṇī and the Atthasālinī in English and German, and the mātikā on its own.'),
    ('commentaries', 'The commentarial tradition', 'The Abhidhamma manuals and sub-commentaries that read the Dhammasaṅgaṇī through the Atthasālinī: the Abhidhammāvatāra, the Abhidhammatthasaṅgaha and its ṭīkā, the Mohavicchedanī, and studies of the commentaries themselves.'),
    ('matika', 'The mātikā and Abhidhamma method', 'Where the mātikā and its triplets and couplets came from, and how the canonical Abhidhamma grew out of the lists of the discourses.'),
    ('studies', 'Studies and introductions', 'Guides, introductions and studies of the Dhammasaṅgaṇī and of Theravāda Abhidhamma thought: mind, matter, dhammas and the process of cognition.'),
    ('reference', 'Reference works', 'Dictionaries, handbooks and the online Tipiṭaka sites and readers used alongside the text.'),
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
add('editions', 'Müller, E. (Ed.)', '1885', 'The Dhammasaṅgaṇi', 'London: Pali Text Society (Henry Frowde) (reprinted 1978, 2001)', lib='muller/', found='https://archive.org/details/dhammasanganiedi00mluoft', label='Scan')
add('editions', 'Müller, E. (Ed.)', '1897', 'The Atthasālinī: Buddhaghosa’s commentary on the Dhammasaṅgaṇi', 'London: Pali Text Society (Henry Frowde) (revised reprint with indexes by L. S. Cousins, 1979)', found='https://catalog.hathitrust.org/Record/008694030', label='Scan')
add('editions', 'Chaṭṭha Saṅgāyana', '1956b', 'Dhammasaṅgaṇī-aṭṭhakathā (Aṭṭhasālinī), -mūlaṭīkā and -anuṭīkā (Sixth Council edition)', 'Yangon: Buddhasāsana Samiti; digital edition, Vipassana Research Institute', lib='atthasalini/', found='https://github.com/VipassanaTech/tipitaka-xml', label='VRI text')
add('editions', 'Bapat, P. V., & Vadekar, R. D. (Eds.)', '1942', 'Aṭṭhasālinī: Commentary on Dhammasangaṇi, the first book of the Abhidhammapiṭaka of the Buddhists of the Theravāda school, for the first time critically edited in Devanāgarī characters', 'Poona: Bhandarkar Oriental Research Institute (Bhandarkar Oriental Series, 3)')
add('editions', 'Chaṭṭha Saṅgāyana', '1956', 'Abhidhammapiṭaka, Dhammasaṅgaṇīpāḷi (Sixth Council edition)', 'Yangon: Buddhasāsana Samiti; digital edition, Vipassana Research Institute (Chaṭṭha Saṅgāyana Tipiṭaka)', lib='pali/', found='https://github.com/VipassanaTech/tipitaka-xml', label='VRI text')
add('editions', 'Kashyap, J. (Gen. Ed.)', '1960', 'The Dhammasaṅgaṇi (Abhidhamma piṭaka, Vol. 1)', 'Nālandā: Pali Publication Board, Bihar Government (Nālandā-Devanāgarī-Pāli-Series)')
add('editions', 'Haṃsāvatī Press', '1900', 'Abhidhammā piṭakat, Dhammasaṅgaṇī Pāḷi to [Abhidhammapiṭaka, Dhammasaṅgaṇīpāḷi]', 'Rangoon: Haṃsāvatī Press (Burmese script; University of Tokyo Library, Burmese Script Editions of the Pāli Tipiṭaka)', found='https://da.dl.itc.u-tokyo.ac.jp/portal/en/assets/055dfea0-0e80-809d-77e7-bf116c24a1d9', label='Scan')
add('editions', 'Ānanda', '1904', 'Abhidhamma piṭaka, Mūla ṭīkā [Dhammasaṅgaṇīmūlaṭīkā]', 'Rangoon: Praññ Krīʺ Maṇḍuiṅ Piṭakat Press (Burmese script; University of Tokyo Library, Burmese Script Editions of the Pāli Tipiṭaka)', found='https://da.dl.itc.u-tokyo.ac.jp/portal/en/assets/3ed1f3f3-95c7-070f-4b2e-147cd73b20da', label='Scan')
add('editions', 'Ānanda', '1960 [i.e. 1977]', 'Dhammasaṅgaṇīmūlaṭīkā: Abhidhammapiṭake Dhammasaṅgaṇīaṭṭhakathāya atthavaṇṇanābhūtā', 'Rangoon: Marammaraṭṭhe Buddhasāsanasamiti (Burmese script; with Dhammapāla’s Dhammasaṅgaṇīanuṭīkā)')

# --- Translations
add('translations', 'Rhys Davids, C. A. F. (Trans.)', '1900', 'A Buddhist manual of psychological ethics of the fourth century B.C., being a translation, now made for the first time, from the original Pāli, of the first book in the Abhidhamma Piṭaka, entitled Dhamma-Sangaṇi (Compendium of states or phenomena)', 'London: Royal Asiatic Society (Oriental Translation Fund, New Series, 12) (2nd ed. 1923; 3rd ed., Pali Text Society, 1974)', lib='rhysdavids/', found='https://archive.org/details/buddhistmanualof00davirich', label='Scan')
add('translations', 'Kyaw Khine, U (Trans.)', '1996', 'The Dhammasaṅgaṇī: Enumeration of the ultimate realities (Vols. I–II)', 'Rangoon: Department for the Promotion and Propagation of the Sāsanā (reprinted Delhi: Sri Satguru Publications, Bibliotheca Indo-Buddhica 198, 1999)', lib='khine/')
add('translations', 'Maung Tin, P. (Trans.); Rhys Davids, C. A. F. (Ed.)', '1920–1921', 'The expositor (Atthasālinī): Buddhaghosa’s commentary on the Dhammasaṅgaṇī, the first book of the Abhidhamma Piṭaka (Vols. I–II)', 'London: Oxford University Press for the Pali Text Society (Translation Series, 8–9) (reprinted in one volume, 1976)', found='https://palitextsociety.org/product/the-expositor', label='Publisher', lib='expositor/')
add('translations', 'Nyanaponika (Trans.); Bretfeld, S., & Knopf, R. (Eds.)', '2005', 'Darlegung der Bedeutung (Atthasālinī): Der Kommentar zur Dhammasaṅgaṇi', 'Oxford: Pali Text Society (Translation Series, 50) (translation made in 1942)', found='https://palitextsociety.org/product/darlegung-der-bedeutung', label='Publisher')
add('translations', 'Ānandajoti (Ed. & Trans.)', '2011', 'The matrix from the abstract teaching (Abhidhamma-mātikā from Dhammasaṅgaṇī) (new ed.)', 'Ancient Buddhist Texts', found='https://www.ancient-buddhist-texts.net/English-Texts/Abstract-Matrix/index.htm', label='Online')

# --- The commentarial tradition
add('commentaries', 'Pe Maung Tin (Trans.); Rhys Davids, C. A. F. (Ed.)', '1920', 'The expositor (Atthasālinī): Buddhaghosa’s commentary on the Dhammasaṅgaṇi, the first book of the Abhidhamma Piṭaka (Vols. I–II)', 'London: Pali Text Society (Translation Series, 8) (1920–1921; reprinted 1976)', lib='expositor/')
add('commentaries', 'Buddhadatta, A. P. (Ed.)', '1915', 'Buddhadatta’s manuals, or Summaries of Abhidhamma: Abhidhammāvatāra and Rūpārūpavibhāga', 'London: Humphrey Milford, Oxford University Press for the Pali Text Society (Part II, Vinayavinicchaya and Uttaravinicchaya, 1928; reprinted in one volume, 1980)', found='https://palitextsociety.org/product/buddhadattas-manuals/', label='Publisher')
add('commentaries', 'Shwe Zan Aung (Trans.); Rhys Davids, C. A. F. (Ed.)', '1910', 'Compendium of philosophy: Being a translation now made for the first time from the original Pali of the Abhidhammattha-saṅgaha, with introductory essay and notes', 'London: Henry Frowde for the Pali Text Society', found='https://catalog.hathitrust.org/Record/100158912', label='Scan')
add('commentaries', 'Saddhātissa, H. (Ed.)', '1989', 'The Abhidhammatthasaṅgaha of Bhadantācariya Anuruddha and the Abhidhammatthavibhāvinī-ṭīkā of Bhadantācariya Sumaṅgalasāmi', 'Oxford: Pali Text Society', found='https://palitextsociety.org/?p=5028', label='Publisher')
add('commentaries', 'Wijeratne, R. P., & Gethin, R. (Trans.)', '2002', 'Summary of the topics of Abhidhamma (Abhidhammatthasaṅgaha) by Anuruddha; Exposition of the topics of Abhidhamma (Abhidhammatthavibhāvinī) by Sumaṅgala', 'Oxford: Pali Text Society', found='https://palitextsociety.org/product/the-summary-of-the-topics-of-abhidhamma-and-exposition-of-the-topics-of-abhidhamma/', label='Publisher')
add('commentaries', 'Buddhadatta, A. P., & Warder, A. K. (Eds.)', '1961', 'Mohavicchedanī Abhidhammamātikatthavaṇṇanā by Kassapatthera of Coḷa', 'London: Luzac & Co. for the Pali Text Society', found='https://palitextsociety.org/product/mohavicchedani/', label='Publisher')
add('commentaries', 'Cousins, L. S.', '2003', 'Buddhadatta, “Abhidhammāvatāra”: Summary', 'In K. H. Potter (Ed.), Encyclopedia of Indian philosophies (Vol. IX, pp. 217–254). Delhi: Motilal Banarsidass')
add('commentaries', 'Cousins, L. S.', '2011', 'Abhidhamma studies I: Jotipāla and the Abhidhamma Anuṭīkā', 'Thai International Journal for Buddhist Studies, II, 1–36')
add('commentaries', 'Cousins, L. S.', '2015', 'The case of the Abhidhamma commentary', 'Journal of the International Association of Buddhist Studies, 36–37 (2013–2014), 389–422')

# --- The mātikā and Abhidhamma method
add('matika', 'Anālayo', '2014', 'The dawn of Abhidharma', 'Hamburg: Hamburg University Press (Hamburg Buddhist Studies, 2)', found='https://hup.sub.uni-hamburg.de/oa-pub/catalog/book/222', label='Publisher')
add('matika', 'Bronkhorst, J.', '1985', 'Dharma and Abhidharma', 'Bulletin of the School of Oriental and African Studies, 48(2), 305–320', found='https://serval.unil.ch/resource/serval:BIB_5CD6C4D2C2C6.P001/REF', label='Article')
add('matika', 'Cousins, L. S.', '1981', 'The Paṭṭhāna and the development of the Theravādin Abhidhamma', 'Journal of the Pali Text Society, IX, 22–46', found='https://palitextsociety.org/wp-content/uploads/2022/01/JPTS_1981_IX.pdf', label='Article')
add('matika', 'Cousins, L. S.', '2015', 'Abhidhamma studies III: Origins of the canonical Abhidha(r)mma literature', 'Journal of the Oxford Centre for Buddhist Studies, 8, 96–145', found='https://jocbs.org/index.php/jocbs/article/view/108', label='Article')
add('matika', 'Frauwallner, E.', '1995', 'Studies in Abhidharma literature and the origins of Buddhist philosophical systems (S. F. Kidd, Trans.; E. Steinkellner, Supervision)', 'Albany: State University of New York Press (SUNY Series in Indian Thought: Texts and Studies)', found='https://www.sunypress.edu/p-2231-studies-in-abhidharma-literatur.aspx', label='Publisher')
add('matika', 'Gethin, R.', '1992', 'The mātikās: Memorization, mindfulness, and the list', 'In J. Gyatso (Ed.), In the mirror of memory: Reflections on mindfulness and remembrance in Indian and Tibetan Buddhism (pp. 149–172). Albany: State University of New York Press')
add('matika', 'Gethin, R.', '2020', 'Reading repetitions in the Saṃyutta-nikāya and early Abhidhamma: From the Mahā-vagga to the Dhammasaṅgaṇi', 'In Dhammadinnā (Ed.), Research on the Saṃyukta-āgama (pp. 109–169). Taipei: Dharma Drum Publishing Corporation')
add('matika', 'Watanabe, F.', '1983', 'Philosophy and its development in the Nikāyas and Abhidhamma', 'Delhi: Motilal Banarsidass')

# --- Studies and introductions
add('studies', 'Nhu Lien (Susantā)', '2007a', 'Abhidhammapiṭaka, Dhammasaṅgaṇīpāḷi, Mātika: Tikamātika', 'Class notes, B.A. ‘B’ course. Yangon: International Theravāda Buddhist Missionary University (June 2005, revised May 2007)', lib='nhulien/')
add('studies', 'Nhu Lien (Susantā)', '2007b', 'Dhammasaṅgaṇī: Dukamātikā, Aṭṭhakathākaṇḍa', 'Notes. Yangon: International Theravāda Buddhist Missionary University (with review questions of 2009)', lib='nhulien/')
add('studies', 'Dhammajeewa, Mawarale', '2022', 'Tika Mātika Clarification; Duka Mātika', 'Study tables. Yangon: International Theravada Buddhist Missionary University', lib='dhammajeewa/')
add('studies', 'Bodhi (Gen. Ed.)', '1993', 'A comprehensive manual of Abhidhamma: The Abhidhammattha saṅgaha of Ācariya Anuruddha', 'Kandy: Buddhist Publication Society (Pāli text originally edited and translated by Nārada; introduction and explanatory guide by U Rewata Dhamma & Bhikkhu Bodhi; tables by U Sīlānanda)', found='https://bps.lk/book/the-comprehensive-manual-of-abhidhamma', label='Publisher')
add('studies', 'Cousins, L. S.', '1984', 'Nibbāna and Abhidhamma', 'Buddhist Studies Review, 1, 95–109')
add('studies', 'Gethin, R.', '1986', 'The five khandhas: Their treatment in the Nikāyas and early Abhidhamma', 'Journal of Indian Philosophy, 14(1), 35–53', found='https://link.springer.com/article/10.1007/BF00165825', label='Publisher')
add('studies', 'Gethin, R.', '1994', 'Bhavaṅga and rebirth according to the Abhidhamma', 'In T. Skorupski & U. Pagel (Eds.), The Buddhist forum (Vol. III, pp. 11–35). London: School of Oriental and African Studies', found='https://www.shin-ibs.edu/research/archived-publications-and-research-projects/the-buddhist-forum/the-buddhist-forum-volume-iii/', label='Online')
add('studies', 'Gethin, R.', '2004', 'He who sees Dhamma sees dhammas: Dhamma in early Buddhism', 'Journal of Indian Philosophy, 32(5–6), 513–542')
add('studies', 'Gethin, R.', '2005', 'On the nature of dhammas: A review article', 'Buddhist Studies Review, 22(2), 175–194', found='https://journal.equinoxpub.com/BSR/article/view/14034', label='Publisher')
add('studies', 'Heim, M.', '2014', 'The forerunner of all things: Buddhaghosa on mind, intention, and agency', 'New York: Oxford University Press')
add('studies', 'Heim, M.', '2018', 'Voice of the Buddha: Buddhaghosa on the immeasurable words', 'New York: Oxford University Press')
add('studies', 'Hinüber, O. v.', '1996', 'A handbook of Pāli literature', 'Berlin: Walter de Gruyter')
add('studies', 'Karunadasa, Y.', '1967', 'Buddhist analysis of matter', 'Colombo: Department of Cultural Affairs')
add('studies', 'Karunadasa, Y.', '1996', 'The Dhamma theory: Philosophical cornerstone of the Abhidhamma', 'Kandy: Buddhist Publication Society (The Wheel, 412/413)', found='https://www.bps.lk/index.php/book/the-dhamma-theory', label='Publisher')
add('studies', 'Karunadasa, Y.', '2010', 'The Theravāda Abhidhamma: Its inquiry into the nature of conditioned reality', 'Hong Kong: Centre for Buddhist Studies, The University of Hong Kong (Wisdom Publications edition, 2019)', found='https://wisdomexperience.org/product/the-theravada-abhidhamma/', label='Publisher')
add('studies', 'Norman, K. R.', '1983', 'Pāli literature: Including the canonical literature in Prakrit and Sanskrit of all the Hīnayāna schools of Buddhism', 'Wiesbaden: Otto Harrassowitz')
add('studies', 'Nyanaponika', '1998', 'Abhidhamma studies: Buddhist explorations of consciousness and time (Bodhi, Ed.; 4th ed.)', 'Kandy: Buddhist Publication Society; Boston: Wisdom Publications (first published Colombo: Frewin & Co., 1949; 2nd rev. and enl. ed. 1965)', found='https://bps.lk/book/abhidhamma-studies', label='Publisher')
add('studies', 'Nyanatiloka', '2008', 'Guide through the Abhidhamma-Piṭaka: A synopsis of the philosophical collection of the Theravāda Buddhist canon (5th rev. ed.)', 'Kandy: Buddhist Publication Society (first published 1938; 2nd ed., revised and enlarged by Nyanaponika, Colombo: Bauddha Sāhitya Sabhā, 1957)', found='https://www.bps.lk/olib/bp/bp302s_Nyanatiloka_Guide-to-Abhidamma.pdf', label='Publisher')
add('studies', 'Rhys Davids, C. A. F.', '1914', 'Buddhist psychology: An inquiry into the analysis and theory of mind in Pali literature', 'London: G. Bell and Sons (The Quest Series)', found='https://catalog.hathitrust.org/Record/103048207', label='Scan')
add('studies', 'Ronkin, N.', '2005', 'Early Buddhist metaphysics: The making of a philosophical tradition', 'London: RoutledgeCurzon (Routledge Critical Studies in Buddhism)', found='https://www.routledge.com/products/9780415600019', label='Publisher')
add('studies', 'Ronkin, N.', '2010', 'Abhidharma', 'In The Stanford encyclopedia of philosophy (first published 16 August 2010; substantive revision 31 March 2026)', found='https://plato.stanford.edu/entries/abhidharma/', label='Online')

# --- Reference works
add('reference', 'Bodhirasa', 'n.d.', 'Digital Pāḷi dictionary [online dictionary]', '', found='https://dpdict.net', label='Online')
add('reference', 'Cone, M.', '2001–2020', 'A dictionary of Pāli (Vols. I–III)', 'The Pali Text Society (searchable online through the Society)', found='https://palitextsociety.org/a-dictionary-of-pali-online/', label='Publisher')
add('reference', 'Malalasekera, G. P.', '1937–1938', 'Dictionary of Pāli proper names (Vols. I–II)', 'London: John Murray (Indian Texts Series)')
add('reference', 'Nyanatiloka', '1980', 'Buddhist dictionary: Manual of Buddhist terms and doctrines (Nyanaponika, Ed.; 4th rev. ed.)', 'Kandy: Buddhist Publication Society (first published 1952)', found='https://bps.lk/book/buddhist-dictionary', label='Publisher')
add('reference', 'Ñāṇamoli', '1994', 'A Pali-English glossary of Buddhist technical terms (Bodhi, Ed.)', 'Kandy: Buddhist Publication Society (2nd ed. 2007)', found='https://www.bps.lk/olib/bp/bp608s_Nyanamoli_Pali-Glossary.pdf', label='Publisher')
add('reference', 'Rhys Davids, T. W., & Stede, W. (Eds.)', '1921–1925', 'The Pali Text Society’s Pali-English dictionary', 'Chipstead: The Pali Text Society (searchable edition, Digital Dictionaries of South Asia, University of Chicago)', found='https://dsal.uchicago.edu/dictionaries/pali/index.html', label='Online')
add('reference', 'Trenckner, V., Andersen, D., Smith, H., et al. (Eds.)', '1925–2011', 'A critical Pāli dictionary (Vols. I–III)', 'Copenhagen: Royal Danish Academy of Sciences and Letters (online edition, University of Cologne, with the Pali Text Society)', found='https://cpd.uni-koeln.de/', label='Online')
add('reference', 'Sirimangalo International', 'n.d.', 'Digital Pāḷi reader [the canon with its aṭṭhakathā and ṭīkā, dictionaries and search]', 'Sirimangalo.org', found='https://pali.sirimangalo.org/', label='Online')
add('reference', 'SuttaCentral', 'n.d.', 'SuttaCentral: Early Buddhist texts, translations, and parallels', 'SuttaCentral', found='https://suttacentral.net/', label='Online')
add('reference', 'Vipassana Research Institute', 'n.d.', 'The Pāḷi Tipiṭaka [Chaṭṭha Saṅgāyana edition, with the aṭṭhakathā and ṭīkā]', 'Igatpuri: Vipassana Research Institute', found='https://tipitaka.org/', label='Online')

json.dump(dict(areas=[dict(id=a, name=n, blurb=b) for a, n, b in AREAS], refs=R),
          open(os.path.join(ROOT, 'data', 'references.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(R), 'references')
