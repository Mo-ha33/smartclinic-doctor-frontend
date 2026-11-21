"""Doctor «المرضى» round 5 (doctor view only; Sara's table is untouched): rich clickable rows, filters + search by name/phone
kept across both tabs, header-first layout, touch/text floor, smarter «مستني ردهم» (oldest first, tiers, button state,
«missing before the visit»). Idempotent.  Usage: python patch_role_doctor5.py [path-to-copy]   Backup: <copy>.bak_before_role_doctor5
"""
import io
import shutil
import sys

P = sys.argv[1] if len(sys.argv) > 1 else r'D:/craft/proto_doctor/index.html'
s = io.open(P, encoding='utf-8').read()
if 'ROLE_DOCTOR5_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'ROLE_DOCTOR4_V1' in s, 'needs ROLE_DOCTOR4_V1'
shutil.copyfile(P, P + '.bak_before_role_doctor5')

js = r'''    // ===== ROLE DOCTOR 5 ===== ROLE_DOCTOR5_V1
    const D5 = { q: '', f: 'all', s: {} };
    (function () { const st = document.createElement('style'); st.id = 'd5-style'; st.textContent = '.d3-doc #view-patients [class*="text-[9px]"], .d3-doc #view-patients [class*="text-[10px]"], .d3-doc #view-patients [class*="text-[11px]"] { font-size: 12px !important; }'; document.head.appendChild(st); })();
    const d5Chip = (tone, txt) => `<span class="text-xs font-bold ${tone} px-2 py-0.5 rounded-full">${txt}</span>`;
    function d5Names() { return [...new Set(MW.appts.map(a => a.n).concat(MW.extra, Object.keys(DOC.plans), Object.keys(DOC.labs)))]; }
    function d5Rank(n) { const a = MW.appts.find(x => x.n === n); if (!a) return 3000; if (['done', 'paid', 'noshow'].includes(a.st)) return 2000 + parseInt(a.t); return parseInt(a.t) - (['inchair', 'ready', 'arrived'].includes(a.st) ? 100 : 0); }
    function d5Match(n) {
      const q = D5.q.trim().toLowerCase(); if (!q) return true;
      const p = PF_PEOPLE[n] || {}, dq = q.replace(/\D/g, '');
      return n.toLowerCase().includes(q) || (dq.length >= 3 && (p.phone || '').replace(/\D/g, '').includes(dq));
    }
    function d5Plan(n) { const p = DOC.plans[n]; return p && ['draft', 'approved', 'presented'].includes(p.st); }
    function d5Lab(n) { return (DOC.labs[n] || []).some(o => o.late || o.status === 'waiting_owner'); }
    function d5Pass(n) {
      const p = PF_PEOPLE[n] || {}, a = MW.appts.find(x => x.n === n);
      return D5.f === 'all' || (D5.f === 'today' && a) || (D5.f === 'alert' && (p.allergy || p.minor || p.cond)) || (D5.f === 'plan' && d5Plan(n)) || (D5.f === 'lab' && d5Lab(n));
    }
    function d5Chips(n) {
      const p = PF_PEOPLE[n] || {}, pl = DOC.plans[n], os = DOC.labs[n] || [], c = [];
      if (p.allergy) c.push(d5Chip('bg-rose-600 text-white', '⚠ ' + T(p.allergy, p.allergyAr)));
      if (p.minor) c.push(d5Chip('bg-amber-100 text-amber-800', T('Minor ', 'قاصر ') + p.age));
      if (p.cond) c.push(d5Chip('bg-amber-100 text-amber-800', T(p.cond, p.condAr)));
      if (pl) c.push(pl.st === 'accepted' ? d5Chip('bg-emerald-100 text-emerald-800', T('Plan accepted', 'الخطة متوافق عليها')) : pl.st === 'presented' ? d5Chip('bg-amber-100 text-amber-800', T('Plan: waiting for the patient', 'الخطة: مستنية رد المريض')) : pl.st === 'approved' ? d5Chip('bg-fuchsia-100 text-fuchsia-800', T('Plan message waits for you', 'رسالة الخطة مستنياك')) : d5Chip('bg-slate-100 text-slate-700', T('Plan: draft', 'الخطة: مسودة')));
      if (os.some(o => o.late)) c.push(d5Chip('bg-rose-100 text-rose-800', T('Lab late', 'المعمل متأخر'))); else if (os.length) c.push(d5Chip('bg-sky-100 text-sky-800', T('Lab: ordered', 'المعمل: اتطلب')));
      if (p.bal > 0) c.push(d5Chip('bg-amber-100 text-amber-800', T('Unpaid balance', 'فيه متبقي') + (PM.mode === 'manage' ? ' ' + docE(p.bal) : '')));
      return c.join('');
    }
    function d5Row(n) {
      const p = PF_PEOPLE[n] || {}, a = MW.appts.find(x => x.n === n), d = DOCP[n], isNext = a && ['inchair', 'ready', 'arrived'].includes(a.st);
      const today = a ? mwChip(a.st) + ` <span class="text-xs text-slate-500">${a.t}</span>` : `<span class="text-xs text-slate-400">${T('No visit today', 'مفيش موعد النهارده')}</span>`;
      return `<div onclick="mwOpenByName('${n}')" class="cursor-pointer bg-white border ${isNext ? 'border-indigo-400 ring-2 ring-indigo-200' : 'border-slate-200'} rounded-2xl p-3 shadow-xs hover:bg-slate-50 flex flex-wrap items-center justify-between gap-3">
        <div class="min-w-0 space-y-1"><div class="flex flex-wrap items-center gap-2"><b class="text-sm text-slate-900 hipaa-blur patient-name">${n}</b><span class="text-xs font-mono text-slate-500">${p.phone || '—'}</span>${today}</div>
          <div class="flex flex-wrap gap-1.5">${d5Chips(n)}</div>${d ? `<div class="text-xs text-slate-500">${T('Last: ' + d.last[0], 'آخر زيارة: ' + d.last[1])}</div>` : ''}</div>
        <div class="flex items-center gap-2 shrink-0"><button onclick="event.stopPropagation();mwOpenByName('${n}')" class="text-sm font-bold px-4 rounded-lg bg-indigo-600 text-white" style="min-height:44px">${T('Open file', 'افتح الملف')}</button><button onclick="event.stopPropagation();mwBook('${n}')" class="text-xs font-semibold px-3 rounded-lg border border-slate-300 bg-white" style="min-height:36px">${T('Book', 'احجز')}</button></div></div>`;
    }
    function d5Missing() {  // today's patients whose pre-visit forms are not done
      return MW.appts.filter(a => !['done', 'paid', 'noshow'].includes(a.st)).map(a => { const f = D2.forms[a.n] || { hx: 'none', cons: 'none' }; const miss = []; if (f.hx !== 'filled') miss.push('hx'); if (f.cons !== 'signed' && f.cons !== 'na') miss.push('cons'); return miss.length ? { a, f, miss } : null; }).filter(Boolean);
    }
    function d5Waiting() {
      const plans = Object.keys(DOC.plans).filter(n => DOC.plans[n].st === 'presented').map(n => [n, d2Days(DOC.plans[n].sentAt)]).sort((x, y) => y[1] - x[1]);
      const labs = []; Object.keys(DOC.labs).forEach(n => DOC.labs[n].forEach(o => { if (o.late || o.status === 'waiting_owner') labs.push([n, o]); })); labs.sort((x, y) => (y[1].late || 0) - (x[1].late || 0));
      return { plans, labs, miss: d5Missing() };
    }
    function d5Remind(n) { D5.s['rem:' + n] = docTm(); d2Remind(n); apPatients(); }
    function d5Call(key, who, what) { D5.s['call:' + key] = true; d2Call(who, what); }
    function d5SendForm(n, k) {
      const f = (D2.forms[n] = D2.forms[n] || { hx: 'none', cons: 'none', rev: false }); f[k] = 'sent';
      mwLog((k === 'hx' ? 'Medical history form' : 'Procedure consent') + ' sent to ' + n + ' on WhatsApp', (k === 'hx' ? 'استمارة التاريخ المرضي' : 'موافقة الإجراء') + ' اتبعتت لـ ' + n + ' على واتساب');
      showToast(T('Sent on WhatsApp (fixed approved text with a form link)', 'اتبعتت على واتساب (نص ثابت متوافق عليه + لينك الاستمارة)')); apPatients();
      setTimeout(() => { if (f[k] !== 'sent') return; f[k] = k === 'hx' ? 'filled' : 'signed'; if (k === 'hx') f.rev = false; mwLog(n + (k === 'hx' ? ' filled the medical history form' : ' signed the procedure consent'), n + (k === 'hx' ? ' ملا استمارة التاريخ المرضي' : ' وقّع موافقة الإجراء')); apPatients(); renderMyWork(); }, 8000);
    }
    function d5WaitBody() {
      const w = d5Waiting(), card = (t, n, body) => `<div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs space-y-2"><h2 class="text-sm font-bold text-slate-900">${t} (${n})</h2>${body || `<p class="text-xs text-slate-400">${T('None.', 'مفيش.')}</p>`}</div>`;
      const btn = 'text-xs font-semibold px-3 rounded-lg border border-slate-300 bg-white';
      const done = txt => `<span class="text-xs font-bold text-emerald-700">${txt}</span>`;
      const miss = w.miss.map(m => `<div class="flex flex-wrap items-center justify-between gap-2 border border-slate-200 rounded-xl px-3 py-2 text-sm"><div><b class="patient-name hipaa-blur">${m.a.n}</b> <span class="text-xs text-slate-500">${m.a.t}</span><div class="text-xs text-amber-800">${m.miss.map(k => k === 'hx' ? T('History form ' + (m.f.hx === 'sent' ? 'sent, not filled' : 'not sent'), 'استمارة التاريخ ' + (m.f.hx === 'sent' ? 'اتبعتت ولسه' : 'ما اتبعتتش')) : T('Consent ' + (m.f.cons === 'sent' ? 'sent, not signed' : 'not sent'), 'الموافقة ' + (m.f.cons === 'sent' ? 'اتبعتت ولسه' : 'ما اتبعتتش'))).join(' · ')}</div></div><div class="flex gap-2">${m.miss.filter(k => m.f[k] !== 'sent').map(k => `<button onclick="d5SendForm('${m.a.n}','${k}')" class="${btn}" style="min-height:36px">${k === 'hx' ? T('Send the history form', 'ابعت استمارة التاريخ') : T('Send the consent', 'ابعت الموافقة')}</button>`).join('')}</div></div>`).join('');
      const plans = w.plans.map(x => { const n = x[0], d = x[1], p = DOC.plans[n], tone = d >= 4 ? 'border-rose-300 bg-rose-50' : d >= 1 ? 'border-amber-300 bg-amber-50' : 'border-slate-200';
        return `<div class="flex flex-wrap items-center justify-between gap-2 border ${tone} rounded-xl px-3 py-2 text-sm"><div><button onclick="mwOpenByName('${n}')" class="font-bold text-slate-900 patient-name hipaa-blur" style="min-height:36px">${n}</button><div class="text-xs text-slate-600">${p.steps.map(z => T(z.en, z.ar)).join(' + ')} · ${docE(docPlanTotal(p))} · <b class="${d >= 4 ? 'text-rose-700' : 'text-amber-800'}">${T('no answer for ' + d + ' days', 'ما ردش من ' + d + ' يوم')}</b></div></div><div class="flex flex-wrap items-center gap-2"><button onclick="mwOpenByName('${n}');pfGo('plan')" class="${btn}" style="min-height:36px">${T('Open plan', 'افتح الخطة')}</button>${D5.s['rem:' + n] ? done(T('Reminded ✓ ', 'اتذكّر ✓ ') + D5.s['rem:' + n]) : `<button onclick="d5Remind('${n}')" class="${btn}" style="min-height:36px">${T('Remind', 'ذكّره')}</button>`}${D5.s['call:p' + n] ? done(T('Call task sent ✓', 'مهمة اتصال راحت ✓')) : `<button onclick="d5Call('p${n}','${n}','${T('treatment plan not answered', 'خطة العلاج ما اتردش عليها')}')" class="text-xs font-bold px-3 rounded-lg bg-indigo-600 text-white" style="min-height:36px">${T('Call him', 'اتصل بيه')}</button>`}</div></div>`; }).join('');
      const labs = w.labs.map(x => { const n = x[0], o = x[1], l = DOC_LABS.find(z => z.k === o.lab), st = docLabStatus(o);
        return `<div class="flex flex-wrap items-center justify-between gap-2 border ${o.late ? 'border-rose-300 bg-rose-50' : 'border-amber-300 bg-amber-50'} rounded-xl px-3 py-2 text-sm"><div><b class="patient-name hipaa-blur">${n}</b> · ${T(o.svc.en, o.svc.ar)} #${o.tooth}<div class="text-xs text-slate-600">${T(l.en, l.ar)} · <b class="${o.late ? 'text-rose-700' : 'text-amber-800'}">${T(st[0], st[1])}</b>${o.appt ? ' · ' + T('fitting ' + o.appt, 'التركيب ' + o.apptAr) : ''}</div></div><div class="flex items-center gap-2"><button onclick="mwOpenByName('${n}');pfGo('lab')" class="${btn}" style="min-height:36px">${T('Open order', 'افتح الطلب')}</button>${D5.s['call:l' + n] ? done(T('Call task sent ✓', 'مهمة اتصال راحت ✓')) : `<button onclick="d5Call('l${n}','${l.en}','${T('order for ' + n + ' is late', 'طلب ' + n + ' متأخر')}')" class="text-xs font-bold px-3 rounded-lg bg-indigo-600 text-white" style="min-height:36px">${T('Call the lab', 'اتصل بالمعمل')}</button>`}</div></div>`; }).join('');
      return card(T('Missing before the visit (today)', 'ناقص قبل الزيارة (النهارده)'), w.miss.length, miss) + card(T('Treatment plans waiting for the patient', 'خطط علاج مستنية رد المريض'), w.plans.length, plans) + card(T('Lab orders that are stuck', 'طلبات معمل واقفة'), w.labs.length, labs);
    }
    function d5Body() {
      if (D2.ptTab === 'wait') return d5WaitBody();
      const names = d5Names().filter(d5Match).filter(d5Pass).sort((a, b) => d5Rank(a) - d5Rank(b));
      return names.length ? `<div class="space-y-2">${names.map(d5Row).join('')}</div>` : `<div class="bg-white border border-slate-200 rounded-2xl p-6 text-sm text-slate-500 text-center">${T('No patient matches. Clear the filter or the search.', 'مفيش مريض مطابق. شيل الفلتر أو البحث.')}</div>`;
    }
    function d5Q(v) { D5.q = v; const l = document.getElementById('d5-list'); if (l) { l.innerHTML = d5Body(); lucide.createIcons(); } }
    function d5F(f) { D5.f = f; apPatients(); }
    function d5Tab(t) { D2.ptTab = t; apPatients(); }
    function d5Page() {
      const w = d5Waiting(), cnt = w.plans.length + w.labs.length + w.miss.length, all = D2.ptTab !== 'wait';
      const tab = (k, label) => `<button onclick="d5Tab('${k}')" class="text-sm font-semibold px-4 rounded-xl ${D2.ptTab === k || (k === 'all' && all) ? 'bg-indigo-600 text-white' : 'text-slate-600 hover:bg-slate-100'}" style="min-height:44px">${label}</button>`;
      const fl = [['all', T('All', 'الكل')], ['today', T('Today', 'النهارده')], ['alert', T('Medical alert', 'تنبيه طبي')], ['plan', T('Plan waiting', 'خطة مستنية')], ['lab', T('Lab', 'معمل')]].map(f => `<button onclick="d5F('${f[0]}')" class="text-xs font-semibold px-3 rounded-full border ${D5.f === f[0] ? 'bg-slate-800 text-white border-slate-800' : 'border-slate-300 bg-white text-slate-700'}" style="min-height:36px">${f[1]}</button>`).join('');
      return `<div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs flex flex-wrap items-center justify-between gap-3"><div><h1 class="text-lg font-bold text-slate-900">${T('Patients', 'المرضى')}</h1><p class="text-sm text-slate-500">${all ? T('Who is who, and what is stuck with each one', 'مين هو مين، وإيه اللي واقف مع كل واحد') : T('What is stuck outside the room', 'اللي واقف برّه الأوضة')}</p></div><input id="pt-q" value="${D5.q.replace(/"/g, '&quot;')}" oninput="d5Q(this.value)" placeholder="${T('Name or phone', 'الاسم أو الموبايل')}" class="border border-slate-300 rounded-xl px-3 text-sm w-72" style="min-height:44px"></div>
        <div class="bg-white border border-slate-200 rounded-2xl p-1.5 shadow-xs flex flex-wrap gap-1">${tab('all', T('All patients', 'كل المرضى'))}${tab('wait', T('Waiting for them', 'مستني ردهم') + (cnt ? ' (' + cnt + ')' : ''))}</div>
        ${all ? `<div class="flex flex-wrap gap-2">${fl}</div>` : ''}<div id="d5-list" class="space-y-3">${d5Body()}</div>`;
    }
    const _d5PrevPatients = apPatients;
    apPatients = function () {
      _d5PrevPatients();
      if (PM.who !== 'doctor') return;
      const el = document.getElementById('view-patients'); if (!el) return;
      el.innerHTML = d5Page(); lucide.createIcons();
    };

'''
anchor = '    // initial render\n'
assert s.count(anchor) == 1
s = s.replace(anchor, js + anchor)
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('patched', P)
