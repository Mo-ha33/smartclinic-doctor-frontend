"""Doctor patient file round 4: sticky patient bar (allergen + minor), work-first layout on tablets, status badges on tabs,
touch/text floor inside the tabs, close-visit guard. Idempotent.
Usage: python patch_role_doctor4.py [path-to-copy]  (default D:/craft/proto_doctor/index.html)   Backup: <copy>.bak_before_role_doctor4
"""
import io
import shutil
import sys

P = sys.argv[1] if len(sys.argv) > 1 else r'D:/craft/proto_doctor/index.html'
s = io.open(P, encoding='utf-8').read()
if 'ROLE_DOCTOR4_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'ROLE_DOCTOR3_V1' in s, 'needs ROLE_DOCTOR3_V1'
shutil.copyfile(P, P + '.bak_before_role_doctor4')

js = r'''    // ===== ROLE DOCTOR 4 ===== ROLE_DOCTOR4_V1
    (function () {
      const st = document.createElement('style'); st.id = 'd4-style';
      st.textContent = `
        .d3-doc #mw-chartbar { position: sticky; top: 0; z-index: 40; box-shadow: 0 2px 8px rgba(15,23,42,.12); }
        .d3-doc #pf-tabs button { min-height: 44px; }
        .d3-doc #pf-pane button, .d3-doc #pf-pane select, .d3-doc #pf-pane input:not([type=checkbox]) { min-height: 36px; }
        .d3-doc #pf-pane button[class*="bg-indigo-600"], .d3-doc #pf-pane button[class*="from-rose-500"] { min-height: 44px; }
        .d3-doc #pf-pane [class*="text-[9px]"], .d3-doc #pf-pane [class*="text-[10px]"], .d3-doc #pf-pane [class*="text-[11px]"], .d3-doc #pf-tabs [class*="text-[10px]"] { font-size: 12px !important; }
        @media (max-width: 1279px) { .d3-doc #pf-tabs { flex-wrap: nowrap; overflow-x: auto; } .d3-doc #pf-tabs button { white-space: nowrap; flex-shrink: 0; } }`;
      document.head.appendChild(st);
    })();
    const d4Doc = () => PM.who === 'doctor';

    // 1) sticky patient bar: name, allergen, minor, nurse request; also for patients opened from search (no appointment)
    function d4BarExtra(bar, n) {
      const p = PF_PEOPLE[n] || {};
      if (p.allergy) bar.querySelectorAll('span').forEach(sp => { if (/bg-rose-100/.test(sp.className) && /حساسية|^Allergy$/.test(sp.innerText.trim())) sp.remove(); });
      const extra = (p.allergy ? `<span class="text-xs font-bold bg-rose-600 text-white px-2 py-0.5 rounded-full">⚠ ${T(p.allergy, p.allergyAr)}</span>` : '') + (p.minor ? `<span class="text-xs font-bold bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full">${T('Minor', 'قاصر')} ${p.age}</span>` : '') + (p.cond ? `<span class="text-xs font-bold bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full">${T(p.cond, p.condAr)}</span>` : '');
      if (bar.firstElementChild) bar.firstElementChild.insertAdjacentHTML('beforeend', extra);
      if (bar.lastElementChild) bar.lastElementChild.insertAdjacentHTML('afterbegin', `<button onclick="d2ReqOpen('${n}')" title="${T('Ask the nurse', 'اطلب من الممرضة')}" class="text-xs font-semibold px-3 rounded-lg border border-slate-300 bg-white hover:bg-slate-50">🩺</button>`);
    }
    const _d4PrevBar = mwShowBar;
    mwShowBar = function (a) { _d4PrevBar(a); if (a && d4Doc()) { const bar = document.getElementById('mw-chartbar'); if (bar) d4BarExtra(bar, a.n); } };
    const _d4PrevOpen = openPatientChart;
    openPatientChart = function (name, i, d) {
      _d4PrevOpen(name, i, d);
      if (!d4Doc() || !name || MW.appts.find(x => x.n === name)) return;
      const bar = document.getElementById('mw-chartbar'); if (!bar) return;
      bar.innerHTML = `<div class="flex flex-wrap items-center gap-2 text-xs"><span class="font-bold text-slate-900 hipaa-blur patient-name">${name}</span><span class="text-slate-500">${T('No visit today', 'مفيش موعد النهارده')}</span></div><div class="flex items-center gap-2"><button onclick="mwShowBar(null);switchView('view-mywork')" class="text-xs font-semibold px-3 rounded-lg border border-slate-300 bg-white hover:bg-slate-50">${T('Back to My Work', 'رجوع لشغلي')}</button></div>`;
      bar.classList.remove('hidden'); d4BarExtra(bar, name);
    };

    // 2) tablets: the work comes first, the brief is folded (the allergen already sits in the sticky bar), nurse request moved to the bar
    const _d4PrevLeft = pfLeft;
    pfLeft = function () {
      let h = _d4PrevLeft();
      if (!d4Doc() || window.innerWidth >= 1280) return h;
      h = h.replace('<details open', '<details').replace(/<summary[^>]*>[^<]*<\/summary>/, `<summary class="text-xs font-bold text-indigo-700 cursor-pointer select-none py-2">${T('Before you walk in — tap to open', 'قبل ما تدخل — دوس تفتح')}</summary>`);
      return h.replace(/<button onclick="d2ReqOpen\('[^']*'\)"[^>]*>🩺[^<]*<\/button>\s*$/, '');
    };

    // 3) status badges on the tabs
    function d4Badge(k, n) {
      const pl = DOC.plans[n], f = (typeof D2 !== 'undefined' && D2.forms[n]) || null, nt = PF.notes[n] || {};
      const b = (tone, txt) => `<span class="ms-1 rounded-full px-1.5 py-0.5 font-bold ${tone}" style="font-size:12px;line-height:1.2">${txt}</span>`;
      if (k === 'exam') return nt.draft ? b('bg-fuchsia-100 text-fuchsia-800', '✨ ' + T('draft', 'مسودة')) : nt.signed ? b('bg-emerald-100 text-emerald-800', '✓') : '';
      if (k === 'plan') {
        if (!pl) return '';
        if (pl.st === 'draft') return b('bg-amber-100 text-amber-800', T('draft', 'مسودة'));
        if (pl.st === 'approved') return b('bg-fuchsia-100 text-fuchsia-800', '✨ ' + T('message', 'رسالة'));
        if (pl.st === 'presented') return b('bg-amber-100 text-amber-800', T('waiting', 'مستني رد'));
        const cur = pl.steps.find(x => x.st === 'accepted'); return cur && !DOC.consents[n + ':' + cur.id] ? b('bg-amber-100 text-amber-800', T('consent', 'موافقة')) : '';
      }
      if (k === 'rx') { const l = (PF.rx[n] || []).length; return l && !PF.rx[n + '_sent'] ? b('bg-amber-100 text-amber-800', T('not sent', 'مش متبعتة')) : ''; }
      if (k === 'lab') {
        const os = DOC.labs[n] || [];
        if (os.some(o => o.late)) return b('bg-rose-100 text-rose-800', T('late', 'متأخر'));
        return pl && pl.steps.some(x => x.lab && x.st !== 'done') && !os.length ? b('bg-sky-100 text-sky-800', T('needed', 'مطلوب')) : '';
      }
      if (k === 'forms') { if (!f) return ''; const miss = (f.hx !== 'filled' ? 1 : 0) + (f.cons !== 'signed' && f.cons !== 'na' ? 1 : 0); return miss ? b('bg-amber-100 text-amber-800', miss) : ''; }
      return '';
    }
    const _d4PrevRpf = renderPatientFile;
    renderPatientFile = function () {
      _d4PrevRpf();
      if (!d4Doc()) return;
      const keys = pfTabsFor().map(t => t.k);
      document.querySelectorAll('#pf-tabs button').forEach((btn, i) => { const h = keys[i] ? d4Badge(keys[i], PF.name) : ''; if (h) btn.insertAdjacentHTML('beforeend', h); });
    };

    // 5) close-visit guard: a signed exam note is required; the rest is listed, not blocking
    function d4Close() { const m = document.getElementById('d4-close'); if (m) m.remove(); }
    function d4Go(id, tab) { d4Close(); mwOpenFile(id); PF.tab = tab; renderPatientFile(); }
    function d4Finish(id) { d4Close(); window._d4ok = id; mwAct(id, 'done'); window._d4ok = null; }
    const _d4PrevAct = mwAct;
    mwAct = function (id, to) {
      if (to !== 'done' || !d4Doc() || window._d4ok === id) return _d4PrevAct(id, to);
      const a = MW.appts.find(x => x.id === id); if (!a) return _d4PrevAct(id, to);
      const n = a.n, nt = PF.notes[n] || {}, pl = DOC.plans[n], os = DOC.labs[n] || [];
      const row = (ok, block, en, ar, tab) => `<button onclick="d4Go(${id},'${tab}')" class="w-full text-start flex items-start gap-2 text-sm px-3 py-2 rounded-xl border ${ok ? 'border-emerald-200 bg-emerald-50' : block ? 'border-rose-300 bg-rose-50' : 'border-amber-200 bg-amber-50'}"><span class="font-bold ${ok ? 'text-emerald-600' : block ? 'text-rose-600' : 'text-amber-600'}">${ok ? '✓' : block ? '✕' : '●'}</span><span class="text-slate-800">${T(en, ar)}</span></button>`;
      const rx = (PF.rx[n] || []).length;
      const items = [row(!!nt.signed, true, nt.signed ? 'Exam note signed' : 'The exam note is not signed — required to finish', nt.signed ? 'ملاحظة الكشف متوقّعة' : 'ملاحظة الكشف ما اتوقّعتش — لازم قبل الإقفال', 'exam'),
        row(!!pl, false, pl ? 'Treatment plan: ' + (pl.st === 'accepted' ? 'accepted' : pl.st) : 'No treatment plan yet', pl ? 'خطة العلاج: ' + (pl.st === 'accepted' ? 'متوافق عليها' : pl.st === 'presented' ? 'مستنيين رد المريض' : pl.st === 'approved' ? 'الرسالة مستنياك' : 'مسودة') : 'مفيش خطة علاج لسه', 'plan'),
        row(rx > 0, false, rx ? 'Prescription ready — it is sent when you finish' : 'No prescription written', rx ? 'الروشتة جاهزة — هتتبعت مع الإقفال' : 'مفيش روشتة مكتوبة', 'rx')];
      if (pl && pl.steps.some(x => x.lab && x.st !== 'done') && !os.length) items.push(row(false, false, 'This plan needs a lab order', 'الخطة دي محتاجة طلب معمل', 'lab'));
      d4Close();
      const m = document.createElement('div'); m.id = 'd4-close'; m.className = 'fixed inset-0 z-[90] bg-slate-900/40 flex items-center justify-center p-4';
      m.innerHTML = `<div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-5 space-y-3"><div class="flex items-center justify-between"><h3 class="font-bold text-slate-900">${T('Finish the visit — ', 'إقفال الزيارة — ')}<span class="patient-name hipaa-blur">${n}</span></h3><button onclick="d4Close()" class="text-slate-400 p-2"><i data-lucide="x" class="w-4 h-4"></i></button></div>${items.join('')}
        <div class="flex justify-end gap-2"><button onclick="d4Close()" class="text-sm font-semibold px-4 rounded-lg border border-slate-300" style="min-height:44px">${T('Back', 'رجوع')}</button>${nt.signed ? `<button onclick="d4Finish(${id})" class="text-sm font-bold px-4 rounded-lg bg-indigo-600 text-white" style="min-height:44px">${T('Finish & sign', 'خلّص ووقّع')}</button>` : `<button onclick="d4Go(${id},'exam')" class="text-sm font-bold px-4 rounded-lg bg-indigo-600 text-white" style="min-height:44px">${T('Open the exam note', 'افتح ملاحظة الكشف')}</button>`}</div></div>`;
      document.body.appendChild(m); lucide.createIcons();
    };

'''
anchor = '    // initial render\n'
assert s.count(anchor) == 1
s = s.replace(anchor, js + anchor)
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('patched', P)
