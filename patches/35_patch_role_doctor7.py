"""Doctor «المواعيد» round 7 (doctor view only; Sara's calendar tools are untouched): no «Today» tools leaking onto the calendar,
no calls tab in his Messages, «needs booking» + «upcoming fittings» (lab readiness) panel, «my patients / whole clinic» focus,
allergen + minor on calendar cards. Idempotent.  Usage: python patch_role_doctor7.py [path-to-copy]   Backup: <copy>.bak_before_role_doctor7
"""
import io
import shutil
import sys

P = sys.argv[1] if len(sys.argv) > 1 else r'D:/craft/proto_doctor/index.html'
s = io.open(P, encoding='utf-8').read()
if 'ROLE_DOCTOR7_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'ROLE_DOCTOR6_V1' in s, 'needs ROLE_DOCTOR6_V1'
shutil.copyfile(P, P + '.bak_before_role_doctor7')

js = r'''    // ===== ROLE DOCTOR 7 ===== ROLE_DOCTOR7_V1
    const D7 = { focus: 'mine' };
    DOC.plans['Noura Samy'] = { st: 'accepted', at: '2026-11-10', steps: [{ id: 1, en: 'Root canal', ar: 'علاج عصب', tooth: 36, price: 2000, st: 'accepted' }, { id: 2, en: 'Zirconia crown', ar: 'تاج زيركون', tooth: 36, price: 3500, st: 'accepted', lab: true }] };

    // calls tab belongs to Sara: the doctor's messages never show it
    const _d7PrevMsgs = apMessages;
    apMessages = function () {
      if (PM.who === 'doctor' && typeof RN2 !== 'undefined') RN2.tab = 'msgs';
      _d7PrevMsgs();
      if (PM.who !== 'doctor') return;
      const el = document.getElementById('view-messages'); if (!el) return;
      [...el.children].forEach(ch => { if (/RN2\.tab='calls'/.test(ch.innerHTML)) ch.remove(); });
    };
    // the «Today» tools (end of day, nurse requests) must not show on the calendar page
    const _d7PrevTop = docTop;
    docTop = function () { _d7PrevTop(); const el = document.getElementById('doc-top'); if (el && MW.calPage) { el.classList.add('hidden'); } };

    function d7Needs() {
      const out = [];
      Object.keys(DOC.plans).forEach(n => {
        const p = DOC.plans[n]; if (p.st !== 'accepted') return;
        const rem = p.steps.filter(x => x.st !== 'done'); if (!rem.length) return;
        const a = MW.appts.find(x => x.n === n && !['done', 'paid', 'noshow'].includes(x.st));
        const words = x => (x.en + ' ' + x.ar).toLowerCase().split(/\s+/).filter(w => w.length > 4);
        let cover = 0;
        if (a && rem.some(x => words(x).some(w => (a.proc + ' ' + a.procAr).toLowerCase().includes(w)))) cover++;
        if (DOC.next[n]) cover++;
        const need = rem.length - cover; if (need > 0) out.push({ n, need, p });
      });
      return out;
    }
    function d7Fit() {
      return Object.keys(DOC.next).map(n => {
        const nx = DOC.next[n], os = DOC.labs[n] || [], pl = DOC.plans[n], o = os[0];
        let st, tone;
        if (!o) { st = [T('Lab order not placed yet', 'طلب المعمل لسه ما اتبعتش'), ''] ; tone = 'bg-rose-100 text-rose-800'; }
        else if (o.late) { st = [T('Lab late ' + o.late + ' days', 'المعمل متأخر ' + o.late + ' أيام'), '']; tone = 'bg-rose-100 text-rose-800'; }
        else if (o.status === 'waiting_owner') { st = [T('Waiting for the owner to approve', 'مستني موافقة صاحب العيادة'), '']; tone = 'bg-amber-100 text-amber-800'; }
        else { const l = DOC_LABS.find(z => z.k === o.lab), ok = l.days <= nx.days - 1; st = [ok ? T('Lab ordered — arrives in time', 'اتطلب من المعمل — هيوصل في الميعاد') : T('Lab ordered — too late for the visit', 'اتطلب من المعمل — هيتأخر عن الزيارة'), '']; tone = ok ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'; }
        return { n, nx, st: st[0], tone, ordered: !!o };
      });
    }
    function d7Focus(f) { D7.focus = f; d7Apply(); }
    function d7Panel(sec) {
      let box = document.getElementById('d7-panel');
      if (!box) { box = document.createElement('div'); box.id = 'd7-panel'; box.className = 'space-y-3'; const grid = sec.querySelector(':scope > .grid'); if (grid) sec.insertBefore(box, grid); else sec.appendChild(box); }
      const needs = d7Needs(), fit = d7Fit(), mine = MW.appts.filter(a => a.c !== 2).length, all = MW.appts.length;
      const btn = 'text-xs font-semibold px-3 rounded-lg border border-slate-300 bg-white';
      const nRows = needs.map(x => `<div class="flex flex-wrap items-center justify-between gap-2 border border-amber-300 bg-amber-50 rounded-xl px-3 py-2 text-sm"><div><b class="patient-name hipaa-blur">${x.n}</b><div class="text-xs text-slate-600">${T('Plan accepted — ' + x.need + ' visit(s) not booked', 'الخطة متوافق عليها — ناقص حجز ' + x.need + ' جلسة')} · ${x.p.steps.filter(z => z.st !== 'done').map(z => T(z.en, z.ar)).join(' + ')}</div></div><button onclick="mwBook('${x.n}')" class="text-xs font-bold px-3 rounded-lg bg-indigo-600 text-white" style="min-height:36px">${T('Book', 'احجز')}</button></div>`).join('');
      const fRows = fit.map(x => `<div class="flex flex-wrap items-center justify-between gap-2 border border-slate-200 rounded-xl px-3 py-2 text-sm"><div><b class="patient-name hipaa-blur">${x.n}</b> · <span class="text-slate-600">${T(x.nx.whatEn, x.nx.whatAr)} · ${T(x.nx.en, x.nx.ar)}</span><div class="mt-1"><span class="text-xs font-bold ${x.tone} px-2 py-0.5 rounded-full">🧪 ${x.st}</span></div></div>${x.ordered ? '' : `<button onclick="mwOpenByName('${x.n}');pfGo('lab')" class="${btn}" style="min-height:36px">${T('Order from the lab', 'اطلب من المعمل')}</button>`}</div>`).join('');
      const sec2 = (t, n, rows) => n ? `<div class="bg-white border border-slate-200 rounded-2xl p-3 shadow-xs space-y-2"><h2 class="text-sm font-bold text-slate-900">${t} (${n})</h2>${rows}</div>` : '';
      const chips = [['mine', T('My patients', 'مرضاي') + ' (' + mine + ')'], ['all', T('Whole clinic', 'كل العيادة') + ' (' + all + ')']].map(f => `<button onclick="d7Focus('${f[0]}')" class="text-xs font-semibold px-3 rounded-full border ${D7.focus === f[0] ? 'bg-slate-800 text-white border-slate-800' : 'border-slate-300 bg-white text-slate-700'}" style="min-height:36px">${f[1]}</button>`).join('');
      box.innerHTML = `<div class="flex flex-wrap gap-2">${chips}</div>${sec2(T('Needs booking', 'محتاج تتحجز'), needs.length, nRows)}${sec2(T('Upcoming fittings', 'تركيبات جاية'), fit.length, fRows)}`;
    }
    function d7Apply() {
      const sec = document.getElementById('view-mywork'); if (!sec) return;
      const box = document.getElementById('d7-panel');
      if (PM.who !== 'doctor' || !MW.calPage) { if (box) box.remove(); return; }
      d7Panel(sec);
      sec.querySelectorAll('[onclick^="mwOpenFile("]').forEach(card => {
        const id = parseInt(card.getAttribute('onclick').match(/\d+/)[0], 10), a = MW.appts.find(x => x.id === id); if (!a) return;
        card.style.opacity = (D7.focus === 'mine' && a.c === 2) ? '.4' : '';
        const p = PF_PEOPLE[a.n] || {};
        if (card.dataset.d7 === T('en', 'ar') + a.n) return; card.dataset.d7 = T('en', 'ar') + a.n;
        card.querySelectorAll('span').forEach(sp => { if (p.allergy && /bg-rose-100/.test(sp.className) && /حساسية|^Allergy$/.test(sp.innerText.trim())) sp.innerText = '⚠ ' + T(p.allergy, p.allergyAr); });
        if (p.minor && !card.querySelector('.d7-minor')) { const row = card.querySelector('.flex.flex-wrap'); if (row) row.insertAdjacentHTML('beforeend', `<span class="d7-minor text-xs font-bold bg-amber-100 text-amber-800 px-1.5 py-0.5 rounded">${T('Minor', 'قاصر')} ${p.age}</span>`); }
      });
    }
    const _d7PrevCal = calRender;
    calRender = function () { _d7PrevCal(); d7Apply(); };
    const _d7PrevSwitch = switchView;
    switchView = function (id) { _d7PrevSwitch(id); if (id === 'view-scheduler' || id === 'view-mywork') { d7Apply(); docTop(); } };
    const _d7PrevToggle = toggleRTL;
    toggleRTL = function () { _d7PrevToggle(); d7Apply(); };

'''
anchor = '    // initial render\n'
assert s.count(anchor) == 1
s = s.replace(anchor, js + anchor)
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('patched', P)
