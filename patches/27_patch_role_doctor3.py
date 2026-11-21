"""Doctor Today round 3: one next-patient block (the «مرضاي» row expands in place), touch sizes (>=44 primary, >=36 secondary,
>=12px text), requests collapse to a small button, wait time on AI drafts (read-only from the escalation engine),
folded AI approval cards. Idempotent.  Usage: python patch_role_doctor3.py [path-to-copy]  (default D:/craft/proto_doctor/index.html)
Backup: <copy>.bak_before_role_doctor3
"""
import io
import shutil
import sys

P = sys.argv[1] if len(sys.argv) > 1 else r'D:/craft/proto_doctor/index.html'
s = io.open(P, encoding='utf-8').read()
if 'ROLE_DOCTOR3_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'DOCTOR_TODAY_V1' in s, 'needs DOCTOR_TODAY_V1'
assert 'ROLE_DOCTOR2_V1' in s, 'needs ROLE_DOCTOR2_V1'
shutil.copyfile(P, P + '.bak_before_role_doctor3')

js = r'''    // ===== ROLE DOCTOR 3 ===== ROLE_DOCTOR3_V1
    const D3 = { open: {} };
    (function () {  // touch sizes: scoped to the doctor's Today, his file bar and the patient column
      const st = document.createElement('style'); st.id = 'd3-style';
      st.textContent = `
        .d3-doc #view-mywork button, .d3-doc #mw-chartbar button, .d3-doc #pf-left button { min-height: 36px; }
        .d3-doc #view-mywork button[class*="bg-indigo-600"], .d3-doc #mw-chartbar button[class*="bg-indigo-600"], .d3-doc #view-mywork button[class*="from-rose-500"], .d3-doc #pf-left button[class*="from-rose-500"] { min-height: 44px; min-width: 44px; }
        .d3-doc #view-mywork [class*="text-[9px]"], .d3-doc #view-mywork [class*="text-[10px]"], .d3-doc #view-mywork [class*="text-[11px]"],
        .d3-doc #mw-chartbar [class*="text-[9px]"], .d3-doc #mw-chartbar [class*="text-[10px]"], .d3-doc #mw-chartbar [class*="text-[11px]"],
        .d3-doc #pf-left [class*="text-[9px]"], .d3-doc #pf-left [class*="text-[10px]"], .d3-doc #pf-left [class*="text-[11px]"] { font-size: 12px !important; }
        .d3-clamp2 { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }`;
      document.head.appendChild(st);
    })();
    function d3Mins(m) { return m < 180 ? T(m + ' min', m + ' دقيقة') : escAge(m); }
    // read-only: the escalation item behind an AI medical draft, if there is one
    function d3Wait(a) {
      const it = (typeof ESC !== 'undefined') && ESC.items.find(x => x.r === 'draft' && ((x.en || '') + (x.ar || '')).includes(a.n)); if (!it) return '';
      const lv = escLevel(it), tone = lv === 'ok' ? 'bg-slate-100 text-slate-700' : lv === 'warn' ? 'bg-amber-100 text-amber-800' : 'bg-rose-100 text-rose-800';
      return `<span class="text-xs font-bold ${tone} px-2 py-0.5 rounded-full">⏱ ${T('Waiting ' + d3Mins(it.min), 'بقالها ' + d3Mins(it.min) + ' مستنياك')}${lv === 'up' ? T(' — escalated', ' — اتصعّدت') : ''}</span>`;
    }
    function d3Toggle(id) { D3.open[id] = !D3.open[id]; renderMyWork(); }
    const _d3PrevAppr = docApprCard;
    docApprCard = function (a, inline) {
      if (inline) return _d3PrevAppr(a, inline);
      const w = d3Wait(a);
      if (a.kind === 'note') return _d3PrevAppr(a, inline).replace(/(<div class="text-\[10px\] font-bold text-fuchsia-800">[^<]*<\/div>)/, '$1' + w);
      if (D3.open[a.id]) return _d3PrevAppr(a, inline).replace(/(<div class="text-\[10px\] font-bold text-fuchsia-800">[^<]*<\/div>)/, '$1<div class="my-0.5">' + w + '</div>') + `<button onclick="d3Toggle('${a.id}')" class="mt-1 text-xs font-semibold text-slate-500 px-2">${T('Fold', 'اطوي')}</button>`;
      const head = a.kind === 'plan' ? T('Plan message for ' + a.n, 'رسالة الخطة لـ ' + a.n) : T('Reply to ' + a.n, 'رد على ' + a.n);
      return `<div class="border border-fuchsia-300 bg-fuchsia-50/60 rounded-xl p-3 space-y-1"><div class="flex flex-wrap items-center justify-between gap-1"><span class="text-xs font-bold text-fuchsia-800">✨ ${T('Medical approval', 'موافقة طبية')}</span>${w}</div><div class="text-sm font-bold text-slate-900 patient-name hipaa-blur">${head}</div><div class="d3-clamp2 text-xs text-slate-600">${isRTL ? a.textAr : a.textEn}</div><button onclick="d3Toggle('${a.id}')" class="w-full text-xs font-semibold px-3 py-2 rounded-lg bg-indigo-600 text-white">${T('Review', 'راجع')}</button></div>`;
    };

    // one next-patient block: the «مرضاي» row expands in place and carries the brief; the toolbar keeps only «request» + «end of day»
    const _d3PrevTop = docTop;
    docTop = function () {
      _d3PrevTop();
      const el = document.getElementById('doc-top'); if (!el || el.classList.contains('hidden')) return;
      d2ReqLoad();
      const rows = D2.req.slice(0, 3).map(r => `<div class="flex items-center justify-between gap-2 text-xs"><span class="text-slate-700">🩺 ${T(r.en, r.ar)}${r.n ? ' · <b class="patient-name hipaa-blur">' + r.n + '</b>' : ''}</span>${d2ReqStatus(r)}</div>`).join('');
      const eod = `<button onclick="docEod()" class="text-xs font-semibold px-3 rounded-lg border border-slate-300 bg-white hover:bg-slate-50 flex items-center gap-1"><i data-lucide="moon" class="w-4 h-4"></i>${T('End of day', 'قفلة اليوم')}</button>`;
      const rq = `<button onclick="d2ReqOpen()" title="${T('Request to the nurse', 'طلب للممرضة')}" class="text-xs font-semibold px-3 rounded-lg border border-slate-300 bg-white hover:bg-slate-50">🩺 ${T('Ask the nurse', 'اطلب من الممرضة')}</button>`;
      el.innerHTML = `<div class="flex flex-wrap items-center justify-end gap-2">${rq}${eod}</div>${rows ? `<div class="mt-2 bg-white border border-slate-200 rounded-2xl px-3 py-2 space-y-1"><div class="text-xs font-bold text-slate-400">${T('YOUR REQUESTS TO THE NURSE', 'طلباتك للممرضة')}</div>${rows}</div>` : ''}`;
      lucide.createIcons();
    };
    function d3Expand() {
      const box = document.getElementById('dr-list'); if (!box || box.style.display === 'none' || DR.range !== 'day') return;
      const row = box.querySelector('button[class*="ring-2"][onclick^="mwOpenFile("]'); if (!row) return;
      const id = parseInt(row.getAttribute('onclick').match(/\d+/)[0], 10), a = MW.appts.find(x => x.id === id); if (!a) return;
      const acts = mwActions(a).map(x => mwBtn(a, x).replace('text-[11px] font-semibold px-2.5 py-1', 'text-sm font-bold px-4 py-2')).join('');
      const chips = docFacts(a.n).filter(x => !x.c.includes('emerald') || x.ic === 'check').slice(0, 6).map(x => `<span class="inline-flex items-center gap-1 text-xs font-bold ${x.c} px-2 py-0.5 rounded-full"><i data-lucide="${x.ic}" class="w-3 h-3"></i>${T(x.en, x.ar)}</span>`).join('');
      const lbl = a.st === 'inchair' ? T('IN THE CHAIR NOW', 'في الكرسي دلوقتي') : T('NEXT — YOUR TURN', 'عليه الدور');
      const d = (typeof DOCP !== 'undefined') && DOCP[a.n];
      row.outerHTML = `<div class="rounded-xl border-2 border-indigo-400 bg-indigo-50 p-3 space-y-2">
        <div class="flex flex-wrap items-center justify-between gap-2"><div class="flex flex-wrap items-center gap-2"><span class="text-xs font-bold text-indigo-700">${lbl}</span><span class="font-mono text-slate-500">${a.t}</span><b class="text-slate-900 text-sm hipaa-blur patient-name">${a.n}</b><span class="text-slate-500">· ${T(a.proc, a.procAr)}</span>${mwChip(a.st)}</div>
        <div class="flex items-center gap-2">${acts}<button onclick="mwOpenFile(${a.id})" class="text-xs font-semibold px-3 rounded-lg border border-slate-300 bg-white hover:bg-slate-50">${T('Open file', 'افتح الملف')}</button></div></div>
        <div class="flex flex-wrap gap-1.5">${chips}</div>${d ? `<div class="text-xs text-slate-700 bg-fuchsia-50 border border-fuchsia-200 rounded-lg px-2 py-1.5"><b class="text-fuchsia-800">✨</b> ${T(d.ai[0], d.ai[1])}</div>` : ''}</div>`;
      // the same patient must not show again as a card in «Needs you»
      const need = document.getElementById('mw-need'), c = document.getElementById('mw-count');
      if (need) [...need.children].forEach(ch => { if (ch.innerHTML.includes('mwOpenFile(' + a.id + ')')) { ch.remove(); if (c) c.innerText = Math.max(0, (+c.innerText || 0) - 1); } });
      if (need && !need.children.length) need.innerHTML = `<p class="text-xs text-slate-400">${T('Nothing needs you right now.', 'مفيش حاجة محتاجاك دلوقتي.')}</p>`;
      lucide.createIcons();
    }
    const _d3PrevDr = drRender;  // the list is rebuilt by switchView / pmMode / date tabs too: expand after each build
    drRender = function () { _d3PrevDr(); if (PM.who === 'doctor' && PM.mode !== 'manage') d3Expand(); };
    const _d3PrevRender = renderMyWork;
    renderMyWork = function () {
      document.body.classList.toggle('d3-doc', PM.who === 'doctor');
      _d3PrevRender();
      if (PM.who === 'doctor' && PM.mode !== 'manage') d3Expand();
    };

'''
anchor = '    // initial render\n'
assert s.count(anchor) == 1
s = s.replace(anchor, js + anchor)
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('patched', P)
