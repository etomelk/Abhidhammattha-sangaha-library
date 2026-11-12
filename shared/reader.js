/* Shared reader for every book in the library.
   Per-book settings come from data attributes on <html>:
     data-book    slug, used to key the saved reading position
     data-anchor  regexp for the ids of numbered units (default ^p\d+$)
     data-sign    prefix shown before a unit number ("§" or "Lesson ")
     data-goto    id prefix for the "go to" box ("p" -> #p122, "l" -> #l12)
     data-split   the chapters, the drawer and the search index are separate files,
                  fetched when first needed (c/<id>.html, gloss.html, search.json, ids.json) */
(function(){
  const $=s=>document.querySelector(s), $$=s=>Array.from(document.querySelectorAll(s));
  const root=document.documentElement;
  const BOOK=root.dataset.book||'book';
  const ANCHOR=new RegExp(root.dataset.anchor||'^p\\d+$');
  const SIGN=root.dataset.sign!==undefined?root.dataset.sign:'§';
  const GOTO=root.dataset.goto||'p';
  const SPLIT=!!root.dataset.split;
  const esc=s=>s.replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
  function refOf(el){ /* "§122" or "Lesson 12 · 3" for the element's id */
    if(el.dataset.ref) return el.dataset.ref;   /* books that name their anchors (Warder: "Exercise 16 · 2") */
    const n=el.querySelector(':scope > .pnum, :scope > .sechead .pnum');
    const num=n?n.textContent:el.id.replace(/^[a-z]+/,'');
    return SIGN+num;
  }

  /* theme (shared by all books) */
  const tb=$('#themebtn');
  try{const t=localStorage.getItem('pg-theme'); if(t) root.setAttribute('data-theme',t);}catch(e){}
  if(tb) tb.addEventListener('click',()=>{
    const dark = root.getAttribute('data-theme')==='dark' || (!root.getAttribute('data-theme') && matchMedia('(prefers-color-scheme: dark)').matches);
    const next = dark?'light':'dark';
    root.setAttribute('data-theme',next);
    try{localStorage.setItem('pg-theme',next);}catch(e){}
  });

  /* English meanings in tables and word lists: show / hide everywhere */
  function setGloss(show){
    root.classList.toggle('nogloss',!show);
    $$('.gltoggle').forEach(b=>{ b.setAttribute('aria-pressed',String(show)); b.textContent=show?'Hide English':'Show English'; });
  }
  try{ if(localStorage.getItem('pg-gloss')==='off') setGloss(false); }catch(e){}
  document.addEventListener('click',e=>{
    const b=e.target.closest('.gltoggle'); if(!b) return;
    const show=root.classList.contains('nogloss');
    const top=b.getBoundingClientRect().top;
    setGloss(show);
    scrollBy(0,b.getBoundingClientRect().top-top); /* keep the table under the finger */
    try{ localStorage.setItem('pg-gloss',show?'on':'off'); }catch(e){}
  });

  /* toc */
  const toc=$('#toc'), menubtn=$('#menubtn');
  let scrim=null;
  function closeNav(){toc.classList.remove('open');menubtn.setAttribute('aria-expanded','false');if(scrim){scrim.remove();scrim=null;}}
  menubtn.addEventListener('click',()=>{
    const open=!toc.classList.contains('open');
    toc.classList.toggle('open',open);menubtn.setAttribute('aria-expanded',String(open));
    if(open){scrim=document.createElement('div');scrim.className='scrim';scrim.addEventListener('click',closeNav);document.body.appendChild(scrim);}else closeNav();
  });
  $$('.chbtn').forEach(b=>b.addEventListener('click',()=>{
    const li=b.parentElement, ul=li.querySelector('.secs');
    $$('.chap').forEach(x=>{x.classList.remove('active');x.querySelector('.secs').hidden=true;x.querySelector('.chbtn').setAttribute('aria-expanded','false');});
    li.classList.add('active'); ul.hidden=false; b.setAttribute('aria-expanded','true');
    location.hash='#'+b.dataset.ch;
    if(innerWidth<=900) closeNav();
  }));
  toc.addEventListener('click',e=>{ if(e.target.closest('.secs a') && innerWidth<=900) closeNav(); });

  /* split books: chapters, drawer, search index and anchor map are fetched on demand */
  const getText=u=>fetch(u,{credentials:'same-origin'}).then(r=>{ if(!r.ok) throw new Error(r.status); return r.text(); });
  let IDS=null, idsP=null, glossP=null;
  function ensureIds(){ if(IDS) return Promise.resolve(); if(!idsP) idsP=getText('ids.json').then(t=>{IDS=JSON.parse(t);}).catch(()=>{IDS={};}); return idsP; }
  function chapOf(id){ /* the chapter that holds an id not yet in the page */
    const m=/^(.+)-[su]\d+$/.exec(id); const c=m&&document.getElementById(m[1]);
    if(c&&c.classList.contains('chapter')) return c;
    return IDS&&IDS[id]?document.getElementById(IDS[id]):null;
  }
  function loadChap(chap){
    if(!chap.dataset.src) return Promise.resolve();
    if(!chap._p) chap._p=getText(chap.dataset.src).then(t=>{
      chap.innerHTML=t; delete chap.dataset.src; chap._err=false;
      chap.querySelectorAll('h3.sec').forEach(s=>io2.observe(s));
      setGloss(!root.classList.contains('nogloss'));
    }).catch(()=>{
      chap._p=null; chap._err=true;
      chap.innerHTML='<header class="chhead"><h2>'+esc(chap.dataset.title||'')+'</h2></header><p class="para">This page could not be loaded. <button class="retry" type="button">Try again</button></p>';
    });
    return chap._p;
  }
  function ensureGloss(){ if(!glossP) glossP=getText('gloss.html').then(t=>{ $('#gl').innerHTML=t; }).catch(()=>{ glossP=null; }); return glossP; }
  function withGloss(fn){ if(SPLIT) ensureGloss().then(fn); else fn(); }
  document.addEventListener('click',e=>{ const b=e.target.closest('.retry'); if(!b) return; const c=b.closest('.chapter'); if(c){ c._err=false; route(); } });

  /* page views: contents or one chapter at a time */
  const chapters=$$('.chapter'), home=$('#home');
  function setActive(id){
    $$('.chap').forEach(x=>{
      const on=x.querySelector('.chbtn').dataset.ch===id;
      x.classList.toggle('active',on); x.querySelector('.secs').hidden=!on; x.querySelector('.chbtn').setAttribute('aria-expanded',String(on));
    });
  }
  let current=null;
  const baseTitle=document.title;
  function show(chap){
    if(chap===current) return;
    current=chap;
    chapters.forEach(c=>c.classList.toggle('on',c===chap));
    home.hidden=!!chap;
    setActive(chap?chap.id:'');
    document.title=chap?(chap.dataset.label+': '+chap.dataset.title+' · '+baseTitle):baseTitle;
  }
  /* current section highlight */
  function tocReveal(a){ /* keep the current section visible in the contents list, without moving the page */
    if(innerWidth<=900 && !toc.classList.contains('open')) return;
    const t=toc.getBoundingClientRect(), r=a.getBoundingClientRect();
    if(r.top<t.top) toc.scrollTop-=t.top-r.top+8; else if(r.bottom>t.bottom) toc.scrollTop+=r.bottom-t.bottom+8;
  }
  const secs=$$('h3.sec');
  const io2=new IntersectionObserver(entries=>{
    entries.forEach(en=>{ if(en.isIntersecting){ const sid=en.target.dataset.sid; $$('.secs a').forEach(a=>a.classList.toggle('cur',a.getAttribute('href')==='#'+sid)); const cur=toc.querySelector('.secs a.cur'); if(cur) tocReveal(cur); } });
  },{rootMargin:'-10% 0px -80% 0px'});
  secs.forEach(s=>io2.observe(s));

  /* go to § / lesson */
  const goto=$('#goto');
  function roman(n){ const v=[1000,900,500,400,100,90,50,40,10,9,5,4,1], r=['M','CM','D','CD','C','XC','L','XL','X','IX','V','IV','I']; let s=''; v.forEach((x,i)=>{ while(n>=x){ s+=r[i]; n-=x; } }); return s; }
  const has=id=>!!document.getElementById(id)||(SPLIT&&!!chapOf(id));
  function gotoRun(){ const v=goto.value.trim(); let id;
    if(/^\d+(\.\d+)+$/.test(v)) id=GOTO+v.replace(/\./g,'-');   /* section numbers such as 2.2.3 */
    else { let n=parseInt(v,10); if(root.dataset.gotoRoman) n=roman(n); id=GOTO+n;
      if(!has(id) && chapters.length){ const c=chapters[0].id.replace(/\d+$/,'')+n; if(document.getElementById(c)) id=c; } }
    if(has(id)){ location.hash='#'+id; goto.blur(); } else { goto.value=''; goto.placeholder='none'; setTimeout(()=>goto.placeholder='No.',1200);} }
  if(goto) goto.addEventListener('keydown',e=>{ if(e.key==='Enter'){ if(SPLIT) ensureIds().then(gotoRun); else gotoRun(); }});

  /* hover previews: cross-references (a.xref -> #pN) and vocabulary words (a.vw -> glossary entry) */
  let tip=null;
  function place(tip,a){
    document.body.appendChild(tip);
    const r=a.getBoundingClientRect(); const w=tip.offsetWidth, h=tip.offsetHeight;
    let x=Math.min(Math.max(16,r.left), innerWidth-w-16), y=r.bottom+8; if(y+h>innerHeight-8) y=r.top-h-8;
    tip.style.left=x+'px'; tip.style.top=y+'px';
  }
  function showTip(a){
    const tgt=document.getElementById(a.dataset.s||('p'+a.dataset.p)); if(!tgt) return;
    tip=document.createElement('div'); tip.className='tip';
    const isTbl=tgt.classList.contains('tbl');
    let body;
    if(isTbl){ const c=tgt.cloneNode(true); c.querySelectorAll('.pnum,.gltoggle').forEach(x=>x.remove()); c.querySelectorAll('tr').forEach((tr,i)=>{ if(i>=8) tr.remove(); }); c.querySelectorAll('li').forEach((li,i)=>{ if(i>=8) li.remove(); }); c.removeAttribute('id'); c.className='tipbody'; body=c.outerHTML; }
    else { let t=tgt.textContent.replace(/^\s*\d+\s*/,''); if(t.length>320) t=t.slice(0,320).replace(/\s\S*$/,'')+' …'; body=esc(t); }
    const ch=tgt.closest('.chapter');
    tip.innerHTML='<div class="tiphead">'+(a.closest('.fnref')?'Note '+esc(a.textContent):a.dataset.s?esc(a.textContent):'§'+a.dataset.p)+' · '+(ch?ch.dataset.label:'')+'</div>'+body;
    place(tip,a);
  }
  function showWord(a){
    const dt=document.querySelector('#gl dt[data-k="'+a.dataset.k+'"]'); if(!dt) return;
    tip=document.createElement('div'); tip.className='tip';
    const dd=dt.nextElementSibling;
    const term=dt.firstChild&&dt.firstChild.nodeType===3?dt.firstChild.textContent.trim():dt.textContent;
    tip.innerHTML='<div class="tiphead">'+esc(term)+(dt.dataset.g?' <em>'+esc(dt.dataset.g)+'</em>':'')+'</div>'+esc(dd?dd.textContent:'');
    place(tip,a);
  }
  function hideTip(){ if(tip){tip.remove();tip=null;} }
  let hov=null;
  document.addEventListener('mouseover',e=>{ const a=e.target.closest('a.xref,a.vw'); hov=a; if(a && !tip){ if(a.classList.contains('vw')) withGloss(()=>{ if(hov===a && !tip) showWord(a); }); else showTip(a);} });
  document.addEventListener('mouseout',e=>{ if(e.target.closest('a.xref,a.vw')){ hov=null; hideTip(); } });
  document.addEventListener('scroll',hideTip,{passive:true});
  /* a marked correction: a tap (or click) shows what was printed and the source */
  document.addEventListener('click',e=>{ const c=e.target.closest('span.corr[title]'); if(!c){ if(tip&&tip._corr) hideTip(); return; } hideTip(); tip=document.createElement('div'); tip.className='tip'; tip._corr=true; tip.innerHTML='<div class="tiphead">'+(c.classList.contains('audit')?'Library correction':'Correction')+'</div>'+esc(c.title); place(tip,c); });
  /* on touch screens a tap on a vocabulary word opens the drawer at that entry */
  document.addEventListener('click',e=>{
    const a=e.target.closest('a.vw'); if(!a) return;
    e.preventDefault(); hideTip();
    withGloss(()=>{
    const dt=document.querySelector('#gl dt[data-k="'+a.dataset.k+'"]'); if(!dt) return;
    if(!gloss.classList.contains('open')) gb.click();
    $('#gq').value=''; filterGloss('');
    $$('#gl dt.cur').forEach(x=>x.classList.remove('cur')); dt.classList.add('cur');
    requestAnimationFrame(()=>dt.scrollIntoView({block:'center'}));
    });
  });

  /* glossary / vocabulary drawer */
  const gloss=$('#gloss'), gb=$('#glossbtn');
  gb.addEventListener('click',()=>{ const open=!gloss.classList.contains('open'); gloss.classList.toggle('open',open); gb.setAttribute('aria-pressed',String(open)); gloss.setAttribute('aria-hidden',String(!open)); if(open && innerWidth>900) $('#gq').focus(); if(open && SPLIT) ensureGloss().then(()=>{ if($('#gq').value) filterGloss($('#gq').value); }); });
  function filterGloss(raw){
    const v=norm(raw); const dts=$$('#gl dt');
    dts.forEach(dt=>{ const dd=dt.nextElementSibling; const hit=!v||norm(dt.textContent+' '+(dd?dd.textContent:'')).includes(v); dt.classList.toggle('hide',!hit); if(dd) dd.classList.toggle('hide',!hit); });
    $$('#gl .ghead').forEach(h=>{ let n=h.nextElementSibling, any=false; while(n && !n.classList.contains('ghead')){ if(n.tagName==='DT' && !n.classList.contains('hide')) {any=true;break;} n=n.nextElementSibling; } h.classList.toggle('hide',!any); });
  }
  $('#gq').addEventListener('input',e=>withGloss(()=>filterGloss(e.target.value)));

  /* search */
  const q=$('#q'); let res=null, sel=-1;
  /* one folding for every book: Müller's circumflexes (â î û) and ṁ / ṃ fold like the macrons */
  const MAP={'ā':'a','ī':'i','ū':'u','ṃ':'m','ṁ':'m','ṅ':'n','ñ':'n','ṭ':'t','ḍ':'d','ṇ':'n','ḷ':'l','ṛ':'r','ś':'s','ṣ':'s','ç':'s','ḥ':'h','â':'a','î':'i','û':'u'};
  function norm(s){ return s.toLowerCase().replace(/[āīūṃṁṅñṭḍṇḷṛśṣçḥâîû]/g,c=>MAP[c]); }
  const units=[]; let unitsP=null;
  function ensureUnits(){ /* split books: the index of every unit, built by scripts/lib/split.py */
    if(!unitsP) unitsP=getText('search.json').then(t=>{ const j=JSON.parse(t);
      j.u.forEach(x=>{ const c=j.ch[x[0]]; units.push({id:x[1], text:x[2], n:norm(x[2]), label:c[0], title:c[1], p:x[3]||null}); });
    }).catch(()=>{ unitsP=null; });
    return unitsP;
  }
  if(!SPLIT) $$('.chapter').forEach(ch=>{
    const label=ch.dataset.label, title=ch.querySelector('h2').textContent;
    let lastP=null;
    ch.querySelectorAll('p.para:not(.pgroup p), .pgroup, .tbl, h3.sec, h4.sub, .vocab li, ol.ex li, .vocab, .ex, ol.lst li, p.pcap').forEach(el=>{
      if(el.id && ANCHOR.test(el.id)) lastP=el;
      if(el.matches('.vocab, .ex')) return; /* containers only mark the position */
      if(!el.id) el.id='u'+units.length;
      const txt=el.textContent.replace(/\s+/g,' ').trim();
      units.push({id:el.id, text:txt, n:norm(txt), label, title, p:lastP?refOf(lastP):null});
    });
  });
  function closeRes(){ if(res){res.remove();res=null;sel=-1;} }
  function runSearch(){
    const v=norm(q.value.trim()); closeRes(); if(v.length<2) return;
    if(SPLIT && !units.length){ ensureUnits().then(()=>{ if(units.length) runSearch(); }); return; }
    const terms=v.split(/\s+/).filter(Boolean);
    const hits=[];
    for(const u of units){ if(terms.every(t=>u.n.includes(t))){ hits.push(u); if(hits.length>=60) break; } }
    res=document.createElement('div'); res.className='results'; res.setAttribute('role','listbox');
    res.innerHTML='<div class="rhead">'+(hits.length?hits.length+(hits.length>=60?'+':'')+' matches':'No matches')+' for “'+esc(q.value)+'”</div>';
    hits.forEach(u=>{
      const a=document.createElement('a'); a.href='#'+u.id;
      const i=u.n.indexOf(terms[0]); const s=Math.max(0,i-70), e=Math.min(u.text.length,i+130);
      let snip=(s>0?'… ':'')+u.text.slice(s,e)+(e<u.text.length?' …':'');
      snip=esc(snip);
      const re=new RegExp(terms.map(t=>t.replace(/[.*+?^${}()|[\]\\]/g,'\\$&').split('').map(c=>{const alts=Object.keys(MAP).filter(k=>MAP[k]===c);return alts.length?'['+c+alts.join('')+']':c;}).join('')).join('|'),'gi');
      snip=snip.replace(re,m=>'<mark>'+m+'</mark>');
      a.innerHTML='<span class="where">'+esc(u.label)+' · '+esc(u.title)+(u.p?' <em>'+esc(u.p)+'</em>':'')+'</span>'+snip;
      a.addEventListener('click',()=>{ closeRes(); });
      res.appendChild(a);
    });
    document.body.appendChild(res);
  }
  let timer; q.addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(runSearch,160);});
  q.addEventListener('focus',()=>{ if(q.value.trim().length>=2 && !res) runSearch(); });
  q.addEventListener('keydown',e=>{
    if(!res) return; const items=res.querySelectorAll('a');
    if(e.key==='ArrowDown'){e.preventDefault(); sel=Math.min(items.length-1,sel+1);}
    else if(e.key==='ArrowUp'){e.preventDefault(); sel=Math.max(0,sel-1);}
    else if(e.key==='Enter'){ if(items[sel]) items[sel].click(); return; }
    else if(e.key==='Escape'){ closeRes(); q.blur(); return; }
    else return;
    items.forEach((it,i)=>it.classList.toggle('sel',i===sel)); if(items[sel]) items[sel].scrollIntoView({block:'nearest'});
  });
  document.addEventListener('click',e=>{ if(res && !e.target.closest('.results') && e.target!==q) closeRes(); });
  document.addEventListener('keydown',e=>{
    if(e.key==='/' && document.activeElement.tagName!=='INPUT'){ e.preventDefault(); q.focus(); q.select(); }
    if(e.key==='Escape'){ closeRes(); if(gloss.classList.contains('open')) gb.click(); closeNav(); }
  });

  /* routing: #home, chapter ids, unit ids, section ids, search hits */
  function route(){
    const h=location.hash.slice(1);
    const el=h&&h!=='home'?document.getElementById(h):null;
    if(!el && SPLIT && h && h!=='home'){
      const c=chapOf(h);
      if(c && c.dataset.src && !c._err){ loadChap(c).then(route); return; }
      if(!c && !IDS){ ensureIds().then(route); return; }
      if(c){ show(c); scrollTo(0,0); onScroll(); return; }
    }
    if(!el){ show(null); scrollTo(0,0); updateResume(); return; }
    const chap=el.classList.contains('chapter')?el:el.closest('.chapter');
    if(SPLIT && chap.dataset.src && !chap._err){ show(chap); loadChap(chap).then(route); return; }
    show(chap);
    if(SPLIT){ const nx=chapters[chapters.indexOf(chap)+1]; if(nx && nx.dataset.src) setTimeout(()=>{ if(nx.dataset.src) getText(nx.dataset.src).catch(()=>{}); },1200); } /* warm the cache for Next */
    if(el===chap) scrollTo(0,0);
    else requestAnimationFrame(()=>el.scrollIntoView({block:'start'}));
    onScroll();
  }
  addEventListener('hashchange',route);
  /* clicking a link to the hash we are already on should still jump */
  document.addEventListener('click',e=>{
    const a=e.target.closest('a[href^="#"]'); if(!a) return;
    if(a.getAttribute('href')===location.hash){ e.preventDefault(); route(); }
  });

  /* previous / next with arrow keys */
  document.addEventListener('keydown',e=>{
    if(e.altKey||e.ctrlKey||e.metaKey||/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)) return;
    if(e.key!=='ArrowLeft'&&e.key!=='ArrowRight') return;
    const i=current?chapters.indexOf(current):-1;
    const j=e.key==='ArrowRight'?i+1:i-1;
    if(j<-1||j>=chapters.length) return;
    location.hash=j===-1?'#home':'#'+chapters[j].id;
  });

  /* reading progress, back-to-top, remember position (per book) */
  const bar=$('#progress span'), totop=$('#totop');
  totop.addEventListener('click',()=>scrollTo({top:0,behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'}));
  let saveT;
  function whereText(el){
    const chap=el.classList.contains('chapter')?el:el.closest('.chapter');
    return chap.dataset.label+': '+chap.dataset.title+(el!==chap?' · '+refOf(el):'');
  }
  function onScroll(){
    const max=document.documentElement.scrollHeight-innerHeight;
    bar.style.width=(current&&max>0?Math.min(100,scrollY/max*100):0)+'%';
    totop.hidden=scrollY<innerHeight*1.2;
    clearTimeout(saveT);
    saveT=setTimeout(()=>{
      if(!current) return;
      let el=current;
      for(const p of current.querySelectorAll('[id]')){ if(!ANCHOR.test(p.id)) continue; if(p.getBoundingClientRect().top>90) break; el=p; }
      try{localStorage.setItem('pg-last:'+BOOK, JSON.stringify({id:el.id, where:whereText(el)}));}catch(e){}
    },400);
  }
  addEventListener('scroll',onScroll,{passive:true});
  function updateResume(){
    let last=null; try{last=JSON.parse(localStorage.getItem('pg-last:'+BOOK)||'null');}catch(e){}
    const r=$('#resume'), el=last&&document.getElementById(last.id);
    if(SPLIT && last && !el){ /* the chapter is not loaded: trust the saved description */
      ensureIds().then(()=>{ if(!chapOf(last.id)){ r.hidden=true; return; } r.href='#'+last.id; $('#rwhere').textContent=last.where; r.hidden=false; });
      return;
    }
    if(!el){ r.hidden=true; return; }
    r.href='#'+last.id;
    $('#rwhere').textContent=whereText(el);
    r.hidden=false;
  }
  route();
})();
