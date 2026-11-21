"""Doctor round 2: «+ جديد» lab/plan, «مستني ردهم» tab in Patients, «مسودة AI جاهزة» filter in Messages,
doctor <-> nurse requests (synced between tabs through localStorage, feeds the escalation engine), pre-visit forms.
Idempotent.  Usage: python patch_role_doctor2.py [path-to-copy]   (default D:/craft/proto_doctor/index.html)
Backup: <copy>.bak_before_role_doctor2
"""
import io
import shutil
import sys

P = sys.argv[1] if len(sys.argv) > 1 else r'D:/craft/proto_doctor/index.html'
s = io.open(P, encoding='utf-8').read()
if 'ROLE_DOCTOR2_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'ESCALATION_V1' in s, 'needs ESCALATION_V1'
assert 'ROLE_DOCTOR_V1' in s, 'needs ROLE_DOCTOR_V1'
shutil.copyfile(P, P + '.bak_before_role_doctor2')

js = r'''    // ===== ROLE DOCTOR 2 ===== ROLE_DOCTOR2_V1
    const D2 = { ptTab: 'all', msgF: 'all', req: [], reqSig: '', forms: {
      'Peter Parker': { hx: 'filled', cons: 'signed', rev: false }, 'Mary Jane': { hx: 'filled', cons: 'sent', rev: true },
      'Ben Wayne': { hx: 'filled', cons: 'na', rev: true }, 'Gwen Stacy': { hx: 'sent', cons: 'sent', rev: false } } };
    const D2_MIN = 6000;  // demo: one "minute" of the escalation clock = 6 seconds
    const D2_LS = 'ROLE_DOCTOR2_REQ';
    // seeds: plans waiting for the patient, a lab order that is late
    DOC.plans['Harry Osborn'] = { st: 'presented', sentAt: '2026-11-19', steps: [{ id: 1, en: 'Zirconia crown', ar: 'تاج زيركون', tooth: 36, price: 3500, st: 'proposed', lab: true }, { id: 2, en: 'Composite filling', ar: 'حشو تجميلي', tooth: 25, price: 600, st: 'proposed' }] };
    DOC.plans['Eddie Brock'] = { st: 'presented', sentAt: '2026-11-16', steps: [{ id: 1, en: 'Root canal', ar: 'علاج عصب', tooth: 46, price: 2200, st: 'proposed' }] };
    DOC.labs['Mona Hassan'] = [{ id: 99, lab: 'a', tooth: 24, shade: 'A2', cost: 1400, svc: { en: 'PFM crown', ar: 'تاج بورسلين على معدن' }, status: 'sent_to_lab', appt: 'Nov 24', apptAr: '24 نوفمبر', at: '2026-11-17', late: 3 }];
    const _d2PrevLabSt = docLabStatus;
    docLabStatus = function (o) { return o.late ? ['late ' + o.late + ' days', 'متأخر ' + o.late + ' أيام'] : _d2PrevLabSt(o); };
    const d2Ago = (d) => T(d + ' days ago', 'من ' + d + ' يوم');
    const d2Days = (iso) => Math.max(0, Math.round((new Date('2026-11-21') - new Date(iso)) / 864e5));
    const d2ChartOpen = () => { const v = document.getElementById('view-chart'); return !!(v && !v.classList.contains('hidden')); };
    const d2Ids = (a) => a.map(x => x.n).join('|');

    // ---------- 1) «+ جديد»
    const _d2PrevHb = hbItems;
    hbItems = function () {
      const r = _d2PrevHb();
      if (PM.who === 'doctor' && PM.mode !== 'manage') r.splice(1, 0, ['Lab order', 'طلب معمل', "d2NewFor('lab')"], ['Treatment plan', 'خطة علاج', "d2NewFor('plan')"], ['Request to the nurse', 'طلب للممرضة', 'd2ReqOpen()']);
      return r;
    };
    function d2Patients() { return [...new Set(MW.appts.map(a => a.n).concat(MW.extra))]; }
    function d2NewFor(kind) {
      if (d2ChartOpen() && PF.name) { pfGo(kind); return; }
      d2Pick(T('Which patient?', 'لأنهي مريض؟'), n => { mwOpenByName(n); pfGo(kind); });
    }
    function d2Pick(title, cb) {
      d2Close();
      window._d2cb = cb;
      const m = document.createElement('div'); m.id = 'd2-modal'; m.className = 'fixed inset-0 z-[90] bg-slate-900/40 flex items-center justify-center p-4';
      m.innerHTML = `<div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-4 space-y-2"><div class="flex items-center justify-between"><b class="text-sm text-slate-900">${title}</b><button onclick="d2Close()" class="text-slate-400"><i data-lucide="x" class="w-4 h-4"></i></button></div>${d2Patients().map(n => `<button onclick="d2Close();window._d2cb('${n}')" class="w-full text-start px-3 py-2 rounded-xl border border-slate-200 hover:bg-slate-50 text-xs font-semibold patient-name hipaa-blur">${n}</button>`).join('')}</div>`;
      document.body.appendChild(m); lucide.createIcons();
    }
    function d2Close() { const m = document.getElementById('d2-modal'); if (m) m.remove(); }

    // ---------- 4) doctor <-> nurse requests (same origin tabs share localStorage)
    ESC_RULES.push({ k: 'req', en: 'Doctor request nobody answered', ar: 'طلب من الدكتور محدش رد عليه', warn: 3, red: 5, then: 10, first: 'nurse', next: 'desk', go: "switchView('view-mywork')" });
    function d2ReqLoad() { try { D2.req = JSON.parse(localStorage.getItem(D2_LS) || '[]'); } catch (e) { D2.req = []; } }
    function d2ReqSave() { try { localStorage.setItem(D2_LS, JSON.stringify(D2.req)); } catch (e) { /* private mode */ } }
    function d2ReqMin(r) { return Math.floor((Date.now() - r.t) / D2_MIN); }
    function d2ReqSync() {  // rebuild the escalation items from the open requests; re-render only when something changed
      d2ReqLoad();
      const sig = D2.req.map(r => r.id + r.st).join(',');
      ESC.items = ESC.items.filter(it => it.r !== 'req');
      D2.req.filter(r => r.st === 'open').forEach(r => ESC.items.push({ id: r.id, r: 'req', en: 'Doctor asks: ' + r.en + (r.n ? ' (' + r.n + ')' : ''), ar: 'الدكتور بيطلب: ' + r.ar + (r.n ? ' (' + r.n + ')' : ''), min: d2ReqMin(r) }));
      escRender();
      if (sig !== D2.reqSig) { D2.reqSig = sig; renderMyWork(); }
    }
    window.addEventListener('storage', e => { if (e.key === D2_LS) d2ReqSync(); });
    setInterval(d2ReqSync, 3000);
    const D2_PRESETS = [['Get the chair ready', 'جهّزي الكرسي'], ['Bring the X-ray', 'هاتي الأشعة'], ['Seat the next patient', 'دخّلي المريض اللي بعده']];
    function d2ReqOpen(n0) {
      d2Close();
      const a = docNextAppt(), cur = n0 || (d2ChartOpen() ? PF.name : (a ? a.n : ''));
      window._d2sel = cur;
      const m = document.createElement('div'); m.id = 'd2-modal'; m.className = 'fixed inset-0 z-[90] bg-slate-900/40 flex items-center justify-center p-4';
      m.innerHTML = `<div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-4 space-y-3"><div class="flex items-center justify-between"><b class="text-sm text-slate-900">${T('Request to the nurse', 'طلب للممرضة')}</b><button onclick="d2Close()" class="text-slate-400"><i data-lucide="x" class="w-4 h-4"></i></button></div>
        <label class="block text-xs"><span class="font-semibold text-slate-600">${T('Patient', 'المريض')}</span><select onchange="window._d2sel=this.value" class="mt-1 w-full border border-slate-300 rounded-lg px-2 py-1.5 bg-white"><option value="">${T('— no patient —', '— من غير مريض —')}</option>${d2Patients().map(n => `<option ${n === cur ? 'selected' : ''}>${n}</option>`).join('')}</select></label>
        <div class="flex flex-wrap gap-1.5">${D2_PRESETS.map((p, i) => `<button onclick="d2ReqSend(${i})" class="text-[11px] font-semibold px-2.5 py-1.5 rounded-lg border border-indigo-300 text-indigo-800 bg-indigo-50">${T(p[0], p[1])}</button>`).join('')}</div>
        <textarea id="d2-free" rows="2" placeholder="${T('Or write your own…', 'أو اكتب طلبك…')}" class="w-full border border-slate-300 rounded-lg px-2 py-1.5 text-xs"></textarea>
        <div class="flex justify-end"><button onclick="d2ReqSend(-1)" class="px-4 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-semibold">${T('Send', 'ابعت')}</button></div></div>`;
      document.body.appendChild(m); lucide.createIcons();
    }
    function d2ReqSend(i) {
      let en, ar;
      if (i >= 0) { en = D2_PRESETS[i][0]; ar = D2_PRESETS[i][1]; }
      else { const v = ((document.getElementById('d2-free') || {}).value || '').trim(); if (!v) { showToast(T('Write the request first', 'اكتب الطلب الأول')); return; } en = v; ar = v; }
      d2ReqLoad(); D2.req.unshift({ id: Date.now(), en, ar, n: window._d2sel || '', t: Date.now(), st: 'open' }); d2ReqSave(); d2Close();
      mwLog('Doctor asked the nurse: ' + en, 'الدكتور طلب من الممرضة: ' + ar);
      showToast(T('Sent to the nurse. If nobody answers in 5 minutes it escalates.', 'اتبعت للممرضة. لو محدش رد خلال 5 دقايق بيتصعّد.')); d2ReqSync(); renderMyWork();
    }
    function d2ReqAnswer(id, st) {
      d2ReqLoad(); const r = D2.req.find(x => x.id === id); if (!r) return; r.st = st; r.at = docTm(); d2ReqSave();
      mwLog('Nurse answered the doctor: ' + r.en + ' — ' + (st === 'done' ? 'done' : 'not now'), 'الممرضة ردت على الدكتور: ' + r.ar + ' — ' + (st === 'done' ? 'تمام' : 'مش دلوقتي'));
      d2ReqSync(); renderMyWork();
    }
    const _d2PrevEscResolve = escResolve;
    escResolve = function (id) { if (D2.req.some(r => r.id === id)) { d2ReqAnswer(id, 'done'); return; } _d2PrevEscResolve(id); };
    function d2ReqStatus(r) {
      const m = d2ReqMin(r);
      if (r.st === 'done') return `<span class="text-emerald-700 font-bold">${T('Done ✓ ', 'تمام ✓ ')}${r.at || ''}</span>`;
      if (r.st === 'later') return `<span class="text-amber-700 font-bold">${T('Nurse: not now ', 'الممرضة: مش دلوقتي ')}${r.at || ''}</span>`;
      return `<span class="${m >= 5 ? 'text-rose-700' : 'text-slate-500'} font-bold">${T('Waiting ' + m + ' min', 'مستنية ' + m + ' دقيقة')}${m >= 5 ? T(' — escalated to reception', ' — اتصعّدت للاستقبال') : ''}</span>`;
    }
    const _d2PrevTop = docTop;
    docTop = function () {
      _d2PrevTop();
      const el = document.getElementById('doc-top'); if (!el || el.classList.contains('hidden')) return;
      d2ReqLoad();
      const rows = D2.req.slice(0, 3).map(r => `<div class="flex items-center justify-between gap-2 text-[11px]"><span class="text-slate-700">🩺 ${T(r.en, r.ar)}${r.n ? ' · <b class="patient-name hipaa-blur">' + r.n + '</b>' : ''}</span>${d2ReqStatus(r)}</div>`).join('');
      el.insertAdjacentHTML('beforeend', `<div class="mt-2 bg-white border border-slate-200 rounded-2xl px-3 py-2 space-y-1"><div class="flex items-center justify-between"><span class="text-[10px] font-bold text-slate-400">${T('YOUR REQUESTS TO THE NURSE', 'طلباتك للممرضة')}</span><button onclick="d2ReqOpen()" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg border border-slate-300 bg-white hover:bg-slate-50">${T('+ Request', '+ طلب')}</button></div>${rows || `<div class="text-[11px] text-slate-400">${T('Nothing sent yet.', 'لسه ما بعتش حاجة.')}</div>`}</div>`);
    };
    const _d2PrevRender = renderMyWork;
    renderMyWork = function () {
      _d2PrevRender();
      if (PM.who !== 'nurse') return;
      const box = document.getElementById('mw-need'); if (!box) return;
      d2ReqLoad(); const open = D2.req.filter(r => r.st === 'open'); if (!open.length) return;
      const html = open.map(r => `<div class="border border-sky-300 bg-sky-50 rounded-xl p-3"><div class="text-[10px] font-bold text-sky-800 mb-1">🩺 ${T('The doctor asks you', 'الدكتور بيطلب منك')}</div><div class="text-xs font-semibold text-slate-900">${T(r.en, r.ar)}${r.n ? ' · <span class="patient-name hipaa-blur">' + r.n + '</span>' : ''}</div><div class="text-[10px] text-slate-500">${T(d2ReqMin(r) + ' min ago', 'من ' + d2ReqMin(r) + ' دقيقة')}</div><div class="flex gap-1.5 mt-2"><button onclick="d2ReqAnswer(${r.id},'done')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-indigo-600 text-white">${T('Done', 'تمام')}</button><button onclick="d2ReqAnswer(${r.id},'later')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg border border-slate-300 bg-white">${T('Not now', 'مش دلوقتي')}</button></div></div>`).join('');
      if (box.querySelector('p.text-slate-400')) box.innerHTML = html; else box.insertAdjacentHTML('afterbegin', html);
      const c = document.getElementById('mw-count'); if (c) c.innerText = (+c.innerText || 0) + open.length;
    };
    // the request button inside the open file (patient column)
    const _d2PrevLeft = pfLeft;
    pfLeft = function () {
      const h = _d2PrevLeft();
      if (pfWho() !== 'doctor') return h;
      return h + `<button onclick="d2ReqOpen('${PF.name}')" class="w-full text-[11px] font-semibold px-3 py-2 rounded-xl border border-indigo-200 text-indigo-800 bg-indigo-50 hover:bg-indigo-100">🩺 ${T('Ask the nurse…', 'اطلب من الممرضة…')}</button>`;
    };

    // ---------- 2) «مستني ردهم» inside Patients
    function d2Waiting() {
      const plans = Object.keys(DOC.plans).filter(n => DOC.plans[n].st === 'presented');
      const labs = [];
      Object.keys(DOC.labs).forEach(n => DOC.labs[n].forEach(o => { if (o.late || o.status === 'waiting_owner') labs.push([n, o]); }));
      return { plans, labs };
    }
    function d2Remind(n) { mwLog('Sara reminded ' + n + ' about the plan on WhatsApp (text approved before)', 'سارة ذكّرت ' + n + ' بالخطة على واتساب (النص متوافق عليه قبل كده)'); showToast(T('Reminder sent to ' + n, 'التذكير اتبعت لـ ' + n)); }
    function d2Call(n, what) {
      MW.tasks.unshift({ id: 'dc' + Date.now(), en: 'Call ' + n + ' — ' + what, ar: 'اتصل بـ ' + n + ' — ' + what, act: 'Called', actAr: 'اتصلت', n });
      showToast(T('A call task went to reception', 'مهمة اتصال راحت للاستقبال')); apPatients();
    }
    function d2PtTab(t) { D2.ptTab = t; apPatients(); }
    const _d2PrevPatients = apPatients;
    apPatients = function () {
      _d2PrevPatients();
      if (PM.who !== 'doctor') return;
      const el = document.getElementById('view-patients'); if (!el) return;
      const w = d2Waiting(), cnt = w.plans.length + w.labs.length;
      const bar = `<div class="bg-white border border-slate-200 rounded-2xl p-1.5 shadow-xs flex flex-wrap gap-1">${[['all', T('All patients', 'كل المرضى')], ['wait', T('Waiting for them', 'مستني ردهم') + (cnt ? ' (' + cnt + ')' : '')]].map(t => `<button onclick="d2PtTab('${t[0]}')" class="text-xs font-semibold px-3 py-1.5 rounded-xl ${D2.ptTab === t[0] ? 'bg-indigo-600 text-white' : 'text-slate-600 hover:bg-slate-100'}">${t[1]}</button>`).join('')}</div>`;
      if (D2.ptTab !== 'wait') { el.insertAdjacentHTML('afterbegin', bar); return; }
      const card = (title, body) => `<div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs space-y-2"><h2 class="text-sm font-bold text-slate-900">${title}</h2>${body}</div>`;
      const pRows = w.plans.map(n => { const p = DOC.plans[n], d = d2Days(p.sentAt); return `<div class="flex flex-wrap items-center justify-between gap-2 border border-slate-200 rounded-xl px-3 py-2 text-xs"><div><b class="patient-name hipaa-blur">${n}</b><div class="text-slate-500">${p.steps.map(x => T(x.en, x.ar)).join(' + ')} · ${docE(docPlanTotal(p))} · ${T('sent ' + d + ' days ago', 'اتبعتت من ' + d + ' يوم')}${d >= 1 ? ' · <span class="text-rose-700 font-semibold">' + T('no answer after 24 h', 'ما ردش بعد 24 ساعة') + '</span>' : ''}</div></div><div class="flex gap-1.5"><button onclick="mwOpenByName('${n}');pfGo('plan')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg border border-slate-300 bg-white">${T('Open plan', 'افتح الخطة')}</button><button onclick="d2Remind('${n}')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg border border-slate-300 bg-white">${T('Remind', 'ذكّره')}</button><button onclick="d2Call('${n}','${T('treatment plan not answered', 'خطة العلاج ما اتردش عليها')}')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-indigo-600 text-white">${T('Call him', 'اتصل بيه')}</button></div></div>`; }).join('');
      const lRows = w.labs.map(x => { const n = x[0], o = x[1], l = DOC_LABS.find(z => z.k === o.lab), s = docLabStatus(o); return `<div class="flex flex-wrap items-center justify-between gap-2 border ${o.late ? 'border-rose-300 bg-rose-50' : 'border-amber-300 bg-amber-50'} rounded-xl px-3 py-2 text-xs"><div><b class="patient-name hipaa-blur">${n}</b> · ${T(o.svc.en, o.svc.ar)} #${o.tooth}<div class="text-slate-600">${T(l.en, l.ar)} · ${T(s[0], s[1])}${o.appt ? ' · ' + T('fitting ' + o.appt, 'التركيب ' + o.apptAr) : ''}</div></div><div class="flex gap-1.5"><button onclick="mwOpenByName('${n}');pfGo('lab')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg border border-slate-300 bg-white">${T('Open order', 'افتح الطلب')}</button><button onclick="d2Call('${l.en}','${T('order for ' + n + ' is late', 'طلب ' + n + ' متأخر')}')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-indigo-600 text-white">${T('Call the lab', 'اتصل بالمعمل')}</button></div></div>`; }).join('');
      el.innerHTML = `<div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs"><h1 class="text-lg font-bold text-slate-900">${T('Patients', 'المرضى')}</h1><p class="text-xs text-slate-500">${T('What is stuck outside the room: plans nobody answered and lab work that is late', 'اللي واقف برّه الأوضة: خطط محدش رد عليها وشغل معمل متأخر')}</p></div>${bar}
        ${card(T('Treatment plans waiting for the patient', 'خطط علاج مستنية رد المريض') + ' (' + w.plans.length + ')', pRows || `<p class="text-xs text-slate-400">${T('None.', 'مفيش.')}</p>`)}
        ${card(T('Lab orders that are stuck', 'طلبات معمل واقفة') + ' (' + w.labs.length + ')', lRows || `<p class="text-xs text-slate-400">${T('None.', 'مفيش.')}</p>`)}`;
      lucide.createIcons();
    };

    // ---------- 3) «مسودة AI جاهزة» in Messages
    MSGS.push({ id: 4, n: 'Gwen Stacy', to: 'doctor', why: 'Medical question before her consult', whyAr: 'سؤال طبي قبل الاستشارة', last: 'هل التبييض بيضر الأسنان؟ ولازم أجيب حد معايا؟', t: '10:30' });
    DOC.appr.find(a => a.id === 'a2').msgId = 4;
    function d2DraftOf(n) { return DOC.appr.find(a => a.kind === 'msg' && a.n === n && a.msgId); }
    function d2MsgF(f) { D2.msgF = f; apMessages(); }
    const _d2PrevMsgs = apMessages;
    apMessages = function () {
      _d2PrevMsgs();
      if (PM.who !== 'doctor') return;
      const el = document.getElementById('view-messages'); if (!el) return;
      const list = apMsgsFor(), nd = list.filter(m => d2DraftOf(m.n)).length;
      const grid = el.querySelector('.grid'); if (!grid) return;
      [...grid.children].forEach((card, i) => {
        const m = list[i], dr = m && d2DraftOf(m.n); if (!m) return;
        if (D2.msgF === 'draft' && !dr) { card.style.display = 'none'; return; }
        if (!dr) return;
        card.insertAdjacentHTML('afterbegin', `<div class="text-[10px] font-bold text-fuchsia-800 bg-fuchsia-50 border border-fuchsia-200 rounded-lg px-2 py-1 inline-block">✨ ${T('AI draft ready — in the box below, edit and approve', 'مسودة AI جاهزة — في الخانة تحت، عدّل ووافق')}</div>`);
        const ta = card.querySelector('textarea'); if (ta && !ta.value) ta.value = isRTL ? dr.textAr : dr.textEn;
      });
      const bar = `<div class="bg-white border border-slate-200 rounded-2xl p-1.5 shadow-xs flex flex-wrap gap-1">${[['all', T('All', 'الكل') + ' (' + list.length + ')'], ['draft', '✨ ' + T('AI draft ready', 'مسودة AI جاهزة') + ' (' + nd + ')']].map(t => `<button onclick="d2MsgF('${t[0]}')" class="text-xs font-semibold px-3 py-1.5 rounded-xl ${D2.msgF === t[0] ? 'bg-indigo-600 text-white' : 'text-slate-600 hover:bg-slate-100'}">${t[1]}</button>`).join('')}</div>`;
      grid.insertAdjacentHTML('beforebegin', bar);
    };
    const _d2PrevReply = apMsgReply;
    apMsgReply = function (id) { DOC.appr = DOC.appr.filter(a => a.msgId !== id); _d2PrevReply(id); renderMyWork(); };

    // ---------- 5) pre-visit forms
    PF_TABS.splice(PF_TABS.findIndex(t => t.k === 'hx') + 1, 0, { k: 'forms', en: 'Forms', ar: 'الاستمارات', ic: 'file-check' });
    function d2F(n) { return D2.forms[n] || (D2.forms[n] = { hx: 'none', cons: 'none', rev: false }); }
    function d2FSend(k) {
      const n = PF.name, f = d2F(n); f[k] = 'sent';
      mwLog((k === 'hx' ? 'Medical history form' : 'Procedure consent') + ' sent to ' + n + ' on WhatsApp', (k === 'hx' ? 'استمارة التاريخ المرضي' : 'موافقة الإجراء') + ' اتبعتت لـ ' + n + ' على واتساب');
      showToast(T('Sent on WhatsApp (fixed approved text with a form link)', 'اتبعتت على واتساب (نص ثابت متوافق عليه + لينك الاستمارة)')); renderPatientFile(); renderMyWork();
      setTimeout(() => { if (f[k] !== 'sent') return; f[k] = k === 'hx' ? 'filled' : 'signed'; f.rev = k === 'hx' ? false : f.rev; mwLog(n + ' ' + (k === 'hx' ? 'filled the medical history form' : 'signed the procedure consent'), n + (k === 'hx' ? ' ملا استمارة التاريخ المرضي' : ' وقّع موافقة الإجراء')); renderMyWork(); if (d2ChartOpen()) renderPatientFile(); }, 8000);
    }
    function d2FReview() { d2F(PF.name).rev = true; showToast(T('Reviewed and added to the medical history', 'اتراجعت واتضافت للتاريخ المرضي')); renderPatientFile(); }
    function d2FormsPane() {
      const n = PF.name, f = d2F(n), pp = PF_PEOPLE[n] || {}, first = pp.minor ? T('parent of ' + n, 'ولي أمر ' + n) : n;
      const st = { none: [T('Not sent', 'ما اتبعتتش'), 'bg-slate-100 text-slate-700'], sent: [T('Sent — not filled yet', 'اتبعتت — لسه ما اتملتش'), 'bg-amber-100 text-amber-800'], filled: [T('Filled ✓', 'اتملت ✓'), 'bg-emerald-100 text-emerald-800'], signed: [T('Signed ✓', 'اتوقّعت ✓'), 'bg-emerald-100 text-emerald-800'], na: [T('Not needed for this visit', 'مش مطلوبة للزيارة دي'), 'bg-slate-100 text-slate-500'] };
      const sendBtn = (k, s) => (s === 'none' || s === 'sent') ? `<button onclick="d2FSend('${k}')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg ${s === 'none' ? 'bg-indigo-600 text-white' : 'border border-slate-300 bg-white'}">${s === 'none' ? T('Send on WhatsApp', 'ابعتها على واتساب') : T('Send again', 'ابعتها تاني')}</button>` : '';
      const hxBody = f.hx === 'filled' ? `<div class="text-xs bg-slate-50 rounded-xl p-3 space-y-1"><div>${T('Allergy', 'الحساسية')}: <b>${pp.allergy ? T(pp.allergy, pp.allergyAr) : T('none', 'مفيش')}</b></div><div>${T('Chronic conditions', 'أمراض مزمنة')}: <b>${pp.cond ? T(pp.cond, pp.condAr) : T('none', 'مفيش')}</b></div><div>${T('Last dentist visit', 'آخر زيارة لدكتور أسنان')}: <b>${T('about a year ago', 'من سنة تقريباً')}</b></div>${f.rev ? `<div class="text-emerald-700 font-bold">${T('Reviewed by you ✓', 'انت راجعتها ✓')}</div>` : `<div class="flex justify-end"><button onclick="d2FReview()" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-indigo-600 text-white">${T('I reviewed it', 'راجعتها')}</button></div>`}</div>` : '';
      const msg = (k) => `<div class="text-[11px] text-slate-500 bg-slate-50 rounded-lg px-2 py-1.5">${T('Message: "Hello ' + first + ', before your visit please fill ' + (k === 'hx' ? 'the medical history form (2 minutes)' : 'the consent for today\'s procedure') + ': clinic.link/f/…"', 'الرسالة: «أهلاً ' + first + '، قبل زيارتك من فضلك ' + (k === 'hx' ? 'املا استمارة التاريخ المرضي (دقيقتين)' : 'وقّع موافقة إجراء النهارده') + ': clinic.link/f/…»')}</div>`;
      const row = (k, en, ar, s, extra) => `<div class="border border-slate-200 rounded-xl p-3 space-y-2"><div class="flex flex-wrap items-center justify-between gap-2"><b class="text-xs text-slate-900">${T(en, ar)}</b><div class="flex items-center gap-2">${docChip(st[s][1], st[s][0])}${sendBtn(k, s)}</div></div>${s === 'none' || s === 'sent' ? msg(k) : ''}${extra}</div>`;
      const note = pp.minor ? `<div class="text-[11px] bg-amber-50 border border-amber-200 rounded-xl px-3 py-2 text-amber-900">${T('The patient is ' + pp.age + ': the guardian fills and signs.', 'المريض عمره ' + pp.age + ': ولي الأمر هو اللي يملا ويوقّع.')}</div>` : '';
      return docCard(T('Forms before the visit', 'الاستمارات قبل الزيارة'), `${note}${row('hx', 'Medical history form', 'استمارة التاريخ المرضي', f.hx, hxBody)}${row('cons', 'Procedure consent', 'موافقة الإجراء', f.cons, '')}<p class="text-[10px] text-slate-400">${T('The form link is a fixed approved text — no medical advice is sent.', 'لينك الاستمارة نص ثابت متوافق عليه — مفيش نصيحة طبية بتتبعت.')}</p>`);
    }
    const _d2PrevPane = pfPane;
    pfPane = function () { return PF.tab === 'forms' ? d2FormsPane() : _d2PrevPane(); };
    // forms status shows in the brief, and a warning before «Start exam» if the consent is not signed
    const _d2PrevFacts = docFacts;
    docFacts = function (n) {
      const f = _d2PrevFacts(n), x = D2.forms[n]; if (!x) return f;
      f.push({ ic: 'file-check', c: x.hx === 'filled' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800', en: 'Medical form: ' + (x.hx === 'filled' ? 'filled' : x.hx === 'sent' ? 'sent, not filled' : 'not sent'), ar: 'استمارة التاريخ: ' + (x.hx === 'filled' ? 'اتملت' : x.hx === 'sent' ? 'اتبعتت ولسه ما اتملتش' : 'ما اتبعتتش') });
      if (x.cons !== 'na') f.push({ ic: 'pen-line', c: x.cons === 'signed' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800', en: 'Consent: ' + (x.cons === 'signed' ? 'signed before the visit' : x.cons === 'sent' ? 'sent, not signed' : 'not sent'), ar: 'الموافقة: ' + (x.cons === 'signed' ? 'متوقّعة قبل الزيارة' : x.cons === 'sent' ? 'اتبعتت ولسه ما اتوقّعتش' : 'ما اتبعتتش') });
      return f;
    };
    const _d2PrevAct = mwAct;
    mwAct = function (id, to) {
      if (to === 'inchair' && PM.who === 'doctor') {
        const a = MW.appts.find(x => x.id === id), x = a && D2.forms[a.n];
        if (a && (!x || x.cons === 'none' || x.cons === 'sent')) showToast(T('Heads up: ' + a.n + "'s consent is not signed yet — sign it from the plan tab before the procedure", 'تنبيه: موافقة ' + a.n + ' لسه ما اتوقّعتش — وقّعها من خطة العلاج قبل الإجراء'));
      }
      _d2PrevAct(id, to);
    };
    const _d2PrevCount = hdrCount;
    hdrCount = function () { d2ReqLoad(); return _d2PrevCount() + (PM.who === 'nurse' ? D2.req.filter(r => r.st === 'open').length : 0); };
    const _d2PrevToggle = toggleRTL;
    toggleRTL = function () { _d2PrevToggle(); renderMyWork(); };
    d2ReqLoad();

'''
anchor = '    // initial render\n'
assert s.count(anchor) == 1
s = s.replace(anchor, js + anchor)
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('patched', P)
