"""Doctor role pass: 10-second brief, treatment plan + WhatsApp quote, consent, lab order, AI approvals in "needs you",
end-of-day. Idempotent.  Usage: python patch_role_doctor.py [path-to-copy]   (default D:/craft/proto_doctor/index.html)
Backup: <copy>.bak_before_role_doctor
"""
import io
import shutil
import sys

P = sys.argv[1] if len(sys.argv) > 1 else r'D:/craft/proto_doctor/index.html'
s = io.open(P, encoding='utf-8').read()
if 'ROLE_DOCTOR_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'STOCK_FLOWS_V1' in s, 'run patch_prototype_stock_flows.py first'
shutil.copyfile(P, P + '.bak_before_role_doctor')

# 1) HTML hook: the doctor's "next patient" strip sits above the calendar
a1 = '        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">\n          <!-- Calendar: same look as the Scheduler -->'
assert s.count(a1) == 1
s = s.replace(a1, '        <div id="doc-top" class="hidden"></div><!-- ROLE_DOCTOR_V1 -->\n' + a1)

# 2) Peter's next visit is the crown fitting (the crown comes from the lab)
a2 = "T('Dec 2 · Root canal #14 (step 2)', '2 ديسمبر · علاج عصب #14 (الجلسة 2)')"
assert s.count(a2) == 1
s = s.replace(a2, "T('Dec 2 · Crown fitting #14', '2 ديسمبر · تركيب التاج #14')")

js = r'''    // ===== ROLE DOCTOR ===== ROLE_DOCTOR_V1
    Object.assign(PF_PEOPLE, {
      'Miles Morales': { dob: '2011-08-03', age: 15, sex: 'M', phone: '0100 909 9094', bal: 0 },
      'Gwen Stacy': { dob: '2009-04-12', age: 17, sex: 'F', phone: '0100 909 9095', bal: 0 }
    });
    Object.assign(PF_PEOPLE['Mary Jane'], { minor: true, gEn: 'her mother', gAr: 'والدتها' });
    Object.assign(PF_PEOPLE['Miles Morales'], { minor: true, gEn: 'his mother', gAr: 'والدته' });
    Object.assign(PF_PEOPLE['Gwen Stacy'], { minor: true, gEn: 'her father', gAr: 'والدها' });
    PF_TABS.splice(2, 0, { k: 'plan', en: 'Treatment plan', ar: 'خطة العلاج', ic: 'clipboard-list' });
    PF_TABS.splice(4, 0, { k: 'lab', en: 'Lab', ar: 'المعمل', ic: 'flask-conical' });
    const _docPrevTabs = pfTabsFor;
    pfTabsFor = function () { return _docPrevTabs().filter(t => !((t.k === 'plan' || t.k === 'lab') && pfWho() === 'nurse')); };

    const DOCP = {  // brief data per patient (demo). Real: last visit + plan + allergy come from clinical_visits / treatment_plans.
      'Peter Parker': { last: ['Nov 3 · Root canal #14 done, temporary filling', '3 نوفمبر · علاج العصب #14 خلص وحشو مؤقت'], xr: ['Periapical #14 taken today', 'أشعة حول الجذر #14 اتصوّرت النهارده'],
        ai: ['Root canal is done and healed well on the X-ray. Today: crown prep #14, then an impression for the lab (zirconia). Asthma: keep the inhaler close.', 'العصب خلص والأشعة كويسة. النهارده تحضير التاج #14 وبعده بصمة للمعمل (زيركون). عنده ربو: البخاخة قريبة منك.'] },
      'Mary Jane': { last: ['Oct 12 · Check-up, caries found on #19', '12 أكتوبر · كشف، لقينا تسوس في #19'], ai: ['Small caries #19, composite today. She is 16: the guardian signs consent.', 'تسوس صغير في #19، حشو تجميلي النهارده. عمرها 16: ولي الأمر يوقّع الموافقة.'] },
      'Miles Morales': { last: ['First visit for this tooth — pain #30 for a week, booked by Sara on WhatsApp', 'أول زيارة للسن ده — ألم في #30 من أسبوع، سارة حجزتله على واتساب'], xr: ['No X-ray yet — take a periapical #30 first', 'مفيش أشعة — صوّر حول الجذر #30 الأول'],
        ai: ['Pain on biting #30 suggests deep caries. Likely a root canal, then a crown. He is 15: the guardian signs consent.', 'الألم مع العضّ في #30 يرجّح تسوس عميق. غالباً علاج عصب وبعده تاج. عمره 15: ولي الأمر يوقّع.'],
        sug: [{ en: 'Root canal', ar: 'علاج عصب', tooth: 30, price: 2000 }, { en: 'Zirconia crown', ar: 'تاج زيركون', tooth: 30, price: 3500, lab: true }] },
      'Ben Wayne': { last: ['Apr 2 · Cleaning, gums healthy', '2 أبريل · تنظيف، اللثة سليمة'], ai: ['Routine cleaning + bitewing. No open plan.', 'تنظيف عادي + أشعة جانبية. مفيش خطة مفتوحة.'], sug: [{ en: 'Scaling & polishing', ar: 'تنظيف وتلميع', tooth: 0, price: 400 }, { en: 'Bitewing X-ray', ar: 'أشعة جانبية', tooth: 0, price: 150 }] },
      'Gwen Stacy': { last: ['No visit yet — asked about whitening on WhatsApp', 'مفيش زيارة قبل كده — سألت عن التبييض على واتساب'], ai: ['Whitening consult. Check gums and old fillings first. She is 17: guardian signs.', 'استشارة تبييض. افحص اللثة والحشوات القديمة الأول. عمرها 17: ولي الأمر يوقّع.'], sug: [{ en: 'In-office whitening', ar: 'تبييض بالعيادة', tooth: 0, price: 2500 }] },
      'Mona Hassan': { last: ['Extraction 2 days ago · now asking about bleeding', 'خلع من يومين · بتسأل عن النزيف دلوقتي'], ai: ['Diabetic: slower healing. Her bleeding question is waiting for your approval below.', 'سكر: الالتئام أبطأ. سؤالها عن النزيف مستني موافقتك تحت.'], sug: [{ en: 'Post-extraction review', ar: 'متابعة بعد الخلع', tooth: 0, price: 0 }] }
    };
    const DOC = {
      plans: {
        'Peter Parker': { st: 'accepted', at: '2026-11-03', steps: [
          { id: 1, en: 'Root canal', ar: 'علاج عصب', tooth: 14, price: 1800, st: 'done' },
          { id: 2, en: 'Zirconia crown', ar: 'تاج زيركون', tooth: 14, price: 3500, st: 'accepted', lab: true },
          { id: 3, en: 'Composite filling', ar: 'حشو تجميلي', tooth: 19, price: 600, st: 'accepted' }] },
        'Mary Jane': { st: 'accepted', at: '2026-10-12', steps: [{ id: 1, en: 'Composite filling', ar: 'حشو تجميلي', tooth: 19, price: 600, st: 'accepted' }] }
      },
      consents: {}, cons: null, labs: {}, labForm: {}, labDec: {}, seq: 100, sentPlanMsg: {},
      next: { 'Peter Parker': { en: 'Dec 2', ar: '2 ديسمبر', days: 11, whatEn: 'Crown fitting #14', whatAr: 'تركيب التاج #14' } },
      appr: [
        { id: 'a1', kind: 'msg', n: 'Mona Hassan', msgId: 1, whyEn: 'Medical question from a patient', whyAr: 'سؤال طبي من مريضة', textAr: 'أهلاً مدام منى، نزيف بسيط بعد الخلع في أول 24 ساعة ممكن يحصل. اضغطي على شاش نظيف مكان الخلع 20 دقيقة من غير ما تفتحي بقك، وماتعمليش مضمضة قوية. لو النزيف زاد أو ما وقفش، كلمينا فوراً على نفس الرقم وهنحجزلك النهارده.', textEn: 'Hello Mona, light bleeding in the first 24 hours after an extraction can happen. Press clean gauze on the spot for 20 minutes without opening your mouth, and avoid strong rinsing. If it increases or does not stop, message us right away and we will see you today.' },
        { id: 'a2', kind: 'msg', n: 'Gwen Stacy', whyEn: 'Medical question before her consult', whyAr: 'سؤال طبي قبل الاستشارة', textAr: 'أهلاً Gwen، التبييض بيتعمل بعد ما الدكتور يفحص اللثة والحشوات. ممكن تحسي بحساسية مؤقتة يومين تلاتة وده طبيعي. لما تيجي النهارده الساعة 11 الدكتور هيقولك لو مناسب ليكي ولا لأ، ومعاها ولي أمرك لأن عمرك أقل من 18.', textEn: 'Hi Gwen, whitening is done after the doctor checks your gums and fillings. Mild sensitivity for 2–3 days is normal. At 11 today the doctor will tell you if it suits you, please come with a parent as you are under 18.' }
      ]
    };
    const DOC_LABS = [
      { k: 'a', en: 'Al Nour Dental Lab', ar: 'معمل النور', days: 7, svc: [['Zirconia crown', 'تاج زيركون', 1400], ['PFM crown', 'تاج بورسلين على معدن', 900], ['Night guard', 'واقي ليلي', 700]] },
      { k: 'b', en: 'Digital Smile Lab (express)', ar: 'ديجيتال سمايل (سريع)', days: 4, svc: [['Zirconia crown', 'تاج زيركون', 1900], ['PFM crown', 'تاج بورسلين على معدن', 1200], ['Night guard', 'واقي ليلي', 900]] }
    ];
    const DOC_LAB_LIMIT = 1500;
    const docWork = () => PM.who === 'doctor' && PM.mode === 'work';
    const docE = n => T('EGP ', '') + Math.round(n).toLocaleString() + T('', ' ج');
    const docTm = () => { const d = new Date(); return String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0'); };
    const docCard = (title, body) => `<div class="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-3"><h3 class="font-bold text-slate-900 text-sm flex flex-wrap items-center gap-2">${title}</h3>${body}</div>`;
    const docChip = (tone, txt) => `<span class="text-[10px] font-bold ${tone} px-2 py-0.5 rounded-full">${txt}</span>`;
    function docPlanTotal(p) { return p.steps.reduce((a, x) => a + (+x.price || 0), 0); }

    // ---- 10-second brief
    function docFacts(n) {
      const p = PF_PEOPLE[n] || {}, d = DOCP[n] || { last: ['No earlier visit', 'مفيش زيارة قبل كده'] }, pl = DOC.plans[n], f = [];
      f.push(p.allergy ? { ic: 'triangle-alert', c: 'bg-rose-100 text-rose-800', en: 'Allergy: ' + p.allergy, ar: 'حساسية: ' + p.allergyAr } : { ic: 'check', c: 'bg-emerald-100 text-emerald-800', en: 'No known allergies', ar: 'مفيش حساسية معروفة' });
      if (p.cond) f.push({ ic: 'heart-pulse', c: 'bg-amber-100 text-amber-800', en: p.cond, ar: p.condAr });
      if (p.minor) f.push({ ic: 'users', c: 'bg-amber-100 text-amber-800', en: 'Minor (' + p.age + ') — guardian signs consent', ar: 'قاصر (' + p.age + ' سنة) — ولي الأمر يوقّع الموافقة' });
      f.push({ ic: 'history', c: 'bg-slate-100 text-slate-700', en: 'Last: ' + d.last[0], ar: 'آخر زيارة: ' + d.last[1] });
      if (pl) {
        const cur = pl.steps.find(x => x.st === 'in_progress') || pl.steps.find(x => x.st === 'accepted'), i = cur ? pl.steps.indexOf(cur) + 1 : 0;
        if (pl.st === 'accepted' && cur) f.push({ ic: 'clipboard-list', c: 'bg-indigo-100 text-indigo-800', en: 'Plan accepted · step ' + i + '/' + pl.steps.length + ': ' + cur.en + (cur.tooth ? ' #' + cur.tooth : ''), ar: 'الخطة متوافق عليها · الخطوة ' + i + ' من ' + pl.steps.length + ': ' + cur.ar + (cur.tooth ? ' #' + cur.tooth : '') });
        else if (pl.st === 'accepted') f.push({ ic: 'clipboard-check', c: 'bg-emerald-100 text-emerald-800', en: 'Plan finished', ar: 'الخطة خلصت' });
        else f.push({ ic: 'clipboard-list', c: 'bg-amber-100 text-amber-800', en: pl.st === 'presented' ? 'Plan sent — waiting for the patient' : 'Plan is a draft', ar: pl.st === 'presented' ? 'الخطة اتبعتت — مستنيين رد المريض' : 'الخطة لسه مسودة' });
      } else f.push({ ic: 'clipboard-list', c: 'bg-slate-100 text-slate-600', en: 'No treatment plan yet', ar: 'مفيش خطة علاج لسه' });
      if (d.xr) f.push({ ic: 'scan', c: 'bg-slate-100 text-slate-700', en: d.xr[0], ar: d.xr[1] });
      if (p.bal > 0) f.push({ ic: 'wallet', c: 'bg-amber-100 text-amber-800', en: 'Unpaid balance' + (PM.mode === 'manage' ? ' ' + docE(p.bal) : '') + ' — reception handles it, not you', ar: 'فيه متبقي على الحساب' + (PM.mode === 'manage' ? ' ' + docE(p.bal) : '') + ' — الاستقبال هو اللي يتكلم فيه مش انت' });
      const lo = (DOC.labs[n] || [])[0];
      if (lo) f.push({ ic: 'flask-conical', c: 'bg-sky-100 text-sky-800', en: 'Lab: ' + lo.svc.en + ' ' + docLabStatus(lo)[0], ar: 'المعمل: ' + lo.svc.ar + ' ' + docLabStatus(lo)[1] });
      else if (pl && pl.steps.some(x => x.lab && x.st !== 'done')) f.push({ ic: 'flask-conical', c: 'bg-sky-100 text-sky-800', en: 'Needs a lab order after today', ar: 'محتاج طلب معمل بعد النهارده' });
      return f;
    }
    function docBrief(n, compact) {
      const d = DOCP[n], f = docFacts(n);
      const rows = f.map(x => `<div class="flex items-start gap-2 text-[11px]"><i data-lucide="${x.ic}" class="w-3.5 h-3.5 mt-0.5 shrink-0 ${x.c.split(' ')[1]}"></i><span class="${x.c.includes('rose') ? 'font-bold text-rose-800' : 'text-slate-700'}">${T(x.en, x.ar)}</span></div>`).join('');
      const ai = d ? `<div class="mt-2 bg-fuchsia-50 border border-fuchsia-200 rounded-xl px-3 py-2 text-[11px] text-slate-700"><b class="text-fuchsia-800">✨ ${T('Read in 10 seconds', 'اقرأها في 10 ثواني')}:</b> ${T(d.ai[0], d.ai[1])}</div>` : '';
      return `<div class="bg-white border border-indigo-200 rounded-2xl p-3 shadow-xs"><div class="text-[10px] font-bold text-indigo-700 mb-1.5">${T('BEFORE YOU WALK IN', 'قبل ما تدخل')}</div><div class="space-y-1">${rows}</div>${compact ? '' : ai}</div>`;
    }
    function docNextAppt() {
      const live = MW.appts.filter(a => !['done', 'paid', 'noshow'].includes(a.st));
      return live.find(a => a.st === 'inchair') || live.find(a => a.st === 'ready') || live.find(a => a.st === 'arrived') || live[0] || null;
    }
    function docTop() {
      const el = document.getElementById('doc-top'); if (!el) return;
      if (!docWork()) { el.classList.add('hidden'); el.innerHTML = ''; return; }
      const a = docNextAppt(), eod = `<button onclick="docEod()" class="text-[11px] font-semibold px-3 py-1.5 rounded-lg border border-slate-300 bg-white hover:bg-slate-50 flex items-center gap-1"><i data-lucide="moon" class="w-3.5 h-3.5"></i>${T('End of day', 'قفلة اليوم')}</button>`;
      el.classList.remove('hidden');
      if (!a) { el.innerHTML = `<div class="bg-white border border-slate-200 rounded-2xl p-3 flex items-center justify-between"><span class="text-xs text-slate-600">${T('All patients seen. Close your day.', 'خلّصت كل المرضى. اقفل يومك.')}</span>${eod}</div>`; lucide.createIcons(); return; }
      const lbl = a.st === 'inchair' ? T('IN THE CHAIR NOW', 'في الكرسي دلوقتي') : T('NEXT PATIENT', 'المريض الجاي');
      const chips = docFacts(a.n).filter(x => !x.c.includes('emerald') || x.ic === 'check').slice(0, 5).map(x => `<span class="inline-flex items-center gap-1 text-[10px] font-bold ${x.c} px-2 py-0.5 rounded-full"><i data-lucide="${x.ic}" class="w-3 h-3"></i>${T(x.en, x.ar)}</span>`).join('');
      el.innerHTML = `<div class="bg-indigo-50 border border-indigo-200 rounded-2xl p-3 space-y-2">
        <div class="flex flex-wrap items-center justify-between gap-2"><div class="flex items-center gap-2 text-xs"><span class="text-[10px] font-bold text-indigo-700">${lbl}</span><b class="text-slate-900 text-sm hipaa-blur patient-name">${a.n}</b><span class="text-slate-500">${a.t} · ${T(a.proc, a.procAr)}</span>${mwChip(a.st)}</div>
          <div class="flex items-center gap-1.5">${mwActions(a).map(x => mwBtn(a, x)).join('')}<button onclick="mwOpenFile(${a.id})" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg border border-slate-300 bg-white hover:bg-slate-50">${T('Open file', 'افتح الملف')}</button>${eod}</div></div>
        <div class="flex flex-wrap gap-1.5">${chips}</div></div>`;
      lucide.createIcons();
    }

    // ---- AI items that need the doctor's clinical approval (AI drafts, the doctor signs)
    function docApprCard(a, inline) {
      const txt = isRTL ? a.textAr : a.textEn;
      const head = a.kind === 'plan' ? T('Treatment plan message for ' + a.n, 'رسالة خطة العلاج لـ ' + a.n) : a.kind === 'note' ? T('Exam note draft for ' + a.n, 'مسودة ملاحظة الكشف لـ ' + a.n) : T('Reply to ' + a.n, 'رد على ' + a.n);
      const why = a.kind === 'plan' ? T('The patient hears the plan and prices only after you approve', 'المريض مش هيسمع الخطة والأسعار غير بعد موافقتك') : a.kind === 'note' ? T('AI listened to the exam — nothing is saved until you sign', 'الـ AI سمع الكشف — مفيش حاجة بتتحفظ غير بتوقيعك') : T(a.whyEn, a.whyAr);
      const body = a.kind === 'note' ? '' : `<textarea id="docap-${a.id}" rows="${inline ? 5 : 4}" class="mt-2 w-full border border-fuchsia-300 bg-white rounded-lg px-2 py-1.5 text-[11px] leading-relaxed">${txt}</textarea>`;
      const btns = a.kind === 'note'
        ? `<button onclick="docApprOpen('${a.id}')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-indigo-600 text-white">${T('Open and review', 'افتح وراجع')}</button>`
        : `<button onclick="docApprSend('${a.id}')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-indigo-600 text-white">${T('Approve & send on WhatsApp', 'وافق وابعت على واتساب')}</button><button onclick="docApprReject('${a.id}')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg border border-slate-300 bg-white">${a.kind === 'plan' ? T('Back to edit', 'رجّعها أعدّل') : T('I will answer myself', 'هرد بنفسي')}</button>`;
      return `<div class="border border-fuchsia-300 bg-fuchsia-50/60 rounded-xl p-3"><div class="text-[10px] font-bold text-fuchsia-800">✨ ${T('Needs your clinical approval', 'محتاج موافقتك الطبية')}</div><div class="text-xs font-bold text-slate-900 mt-0.5">${head}</div><div class="text-[10px] text-slate-500">${why}</div>${body}<div class="flex flex-wrap gap-1.5 mt-2">${btns}</div></div>`;
    }
    function docApprFind(id) { return DOC.appr.find(x => x.id === id); }
    function docApprOpen(id) { const a = docApprFind(id); if (!a) return; mwOpenByName(a.n); PF.tab = 'exam'; renderPatientFile(); }
    function docApprReject(id) {
      const a = docApprFind(id); if (!a) return;
      DOC.appr = DOC.appr.filter(x => x.id !== id);
      if (a.kind === 'plan') { const p = DOC.plans[a.n]; if (p) p.st = 'draft'; showToast(T('Plan is back to draft — nothing was sent', 'الخطة رجعت مسودة — ما اتبعتش حاجة')); }
      else showToast(T('Draft dropped — the chat stays with you', 'المسودة اتلغت — المحادثة فاضلة معاك'));
      mwLog('Doctor did not approve an AI draft for ' + a.n, 'الدكتور ما وافقش على مسودة AI لـ ' + a.n);
      docRefresh();
    }
    function docApprSend(id) {
      const a = docApprFind(id); if (!a) return;
      DOC.appr = DOC.appr.filter(x => x.id !== id);
      if (a.kind === 'plan') {
        const p = DOC.plans[a.n]; p.st = 'presented'; p.sentAt = docTm();
        mwLog('Sara sent the treatment plan to ' + a.n + ' on WhatsApp (approved by the doctor)', 'سارة بعتت خطة العلاج لـ ' + a.n + ' على واتساب (بعد موافقة الدكتور)');
        showToast(T('Sent. Waiting for ' + a.n + ' to accept', 'اتبعتت. مستنيين ' + a.n + ' يوافق'));
        setTimeout(() => { // demo: the patient answers "موافق" (24 h in real life)
          if (!DOC.plans[a.n] || DOC.plans[a.n].st !== 'presented') return; docAccept(a.n, true);
        }, 6000);
      } else {
        if (a.msgId) { const i = MSGS.findIndex(x => x.id === a.msgId); if (i > -1) MSGS.splice(i, 1); }
        mwLog('Reply to ' + a.n + ' sent on WhatsApp (approved by the doctor)', 'الرد على ' + a.n + ' اتبعت على واتساب (بعد موافقة الدكتور)');
        showToast(T('Approved and sent to ' + a.n, 'اتوافق عليه واتبعت لـ ' + a.n));
      }
      docRefresh();
    }
    function docAccept(n, auto) {
      const p = DOC.plans[n]; if (!p) return;
      p.st = 'accepted'; p.at = '2026-11-21'; p.steps.forEach(x => { if (x.st === 'proposed') x.st = 'accepted'; });
      mwLog(n + ' accepted the treatment plan (' + (auto ? 'WhatsApp reply' : 'at the clinic') + ')', n + ' وافق على خطة العلاج (' + (auto ? 'رد واتساب' : 'في العيادة') + ')');
      showToast(T(n + ' accepted the plan' + (auto ? ' on WhatsApp (6 s in the demo)' : ''), n + ' وافق على الخطة' + (auto ? ' على واتساب (6 ثواني في التجربة)' : '')));
      docRefresh();
    }
    function docRefresh() { renderMyWork(); apMessages(); apBadge(); if (document.getElementById('view-chart') && !document.getElementById('view-chart').classList.contains('hidden')) renderPatientFile(); hdrRefresh(); }

    // ---- treatment plan
    function docSuggest() {
      const n = PF.name, d = DOCP[n] || {}, src = d.sug || [{ en: 'Composite filling', ar: 'حشو تجميلي', tooth: 19, price: 600 }];
      DOC.plans[n] = { st: 'draft', ai: true, steps: src.map((x, i) => Object.assign({ id: i + 1, st: 'proposed' }, x)) };
      showToast(T('✨ Draft plan from the chart and exam — edit prices, then approve', '✨ مسودة خطة من الشارت والكشف — عدّل الأسعار وبعدين اعتمد'));
      renderPatientFile();
    }
    function docPrice(i, v) { const p = DOC.plans[PF.name]; p.steps[i].price = Math.max(0, parseInt(v, 10) || 0); const el = document.getElementById('doc-total'); if (el) el.innerHTML = docE(docPlanTotal(p)); }
    function docDropStep(i) { const p = DOC.plans[PF.name]; p.steps.splice(i, 1); renderPatientFile(); }
    function docPlanMsg(n, p) {
      const pp = PF_PEOPLE[n] || {}, tot = docPlanTotal(p), k = tot > 3000 ? 3 : 2;
      const ar = p.steps.map((x, i) => (i + 1) + ') ' + x.ar + (x.tooth ? ' (سن ' + x.tooth + ')' : '') + ' — ' + (+x.price).toLocaleString() + ' ج').join('\n');
      const en = p.steps.map((x, i) => (i + 1) + ') ' + x.en + (x.tooth ? ' (tooth ' + x.tooth + ')' : '') + ' — EGP ' + (+x.price).toLocaleString()).join('\n');
      const who = pp.minor ? 'ولي أمر ' + n : n;
      return { ar: 'أهلاً ' + who + '، بعد الكشف الدكتور جهّز خطة العلاج:\n' + ar + '\nالإجمالي ' + tot.toLocaleString() + ' ج، وممكن يتقسّم على ' + k + ' دفعات. السعر ده ثابت للخطة دي. لو موافق رد بـ «موافق» وهنحجزلك أقرب مواعيد، ولو عندك أي سؤال اكتبلنا وسارة معاك.',
        en: 'Hello ' + (pp.minor ? 'parent of ' : '') + n + ', after the exam the doctor prepared your treatment plan:\n' + en + '\nTotal EGP ' + tot.toLocaleString() + ', which can be split into ' + k + ' payments. These prices are fixed for this plan. Reply «OK» to accept and we will book the nearest slots, or write to us with any question.' };
    }
    function docApprovePlan() {
      const n = PF.name, p = DOC.plans[n]; if (!p || !p.steps.length) return;
      const m = docPlanMsg(n, p);
      p.st = 'approved';  // doctor signed the plan; the message waits for him too
      DOC.appr = DOC.appr.filter(x => x.id !== 'plan:' + n);
      DOC.appr.push({ id: 'plan:' + n, kind: 'plan', n, textAr: m.ar, textEn: m.en });
      mwLog('Doctor approved the treatment plan for ' + n + ' — Sara wrote the WhatsApp explanation', 'الدكتور اعتمد خطة علاج ' + n + ' — سارة كتبت شرحها على واتساب');
      showToast(T('Plan approved. Review the message to the patient, then send', 'الخطة اتعتمدت. راجع الرسالة للمريض وبعدين ابعت'));
      docRefresh();
    }
    function docPlanPane() {
      const n = PF.name, p = DOC.plans[n];
      if (DOC.cons && DOC.cons.n === n) return docConsentPane();
      const title = T('Treatment plan', 'خطة العلاج');
      if (!p) return docCard(title, `<p class="text-xs text-slate-500">${T('No plan for this patient yet. The AI can draft one from the chart and your exam — you edit, you approve.', 'مفيش خطة للمريض ده لسه. الـ AI يقدر يجهّز مسودة من الشارت والكشف — انت تعدّل وانت تعتمد.')}</p><button onclick="docSuggest()" class="text-xs font-bold px-4 py-2 rounded-lg bg-gradient-to-r from-rose-500 to-fuchsia-600 text-white">✨ ${T('Draft a plan', 'جهّز مسودة خطة')}</button>`);
      const stTxt = { draft: [T('Draft — not shown to the patient', 'مسودة — المريض ما شافهاش'), 'bg-slate-100 text-slate-700'], approved: [T('You approved — message waiting for you', 'انت اعتمدتها — الرسالة مستنياك'), 'bg-fuchsia-100 text-fuchsia-800'], presented: [T('Sent to the patient — waiting for the answer', 'اتبعتت للمريض — مستنيين رده'), 'bg-amber-100 text-amber-800'], accepted: [T('Patient accepted ✓', 'المريض وافق ✓'), 'bg-emerald-100 text-emerald-800'] }[p.st];
      const edit = p.st === 'draft';
      const rows = p.steps.map((x, i) => {
        const hasLab = (DOC.labs[n] || []).some(o => o.tooth === x.tooth);
        let act = '';
        if (p.st === 'accepted') {
          if (x.st === 'accepted') act = `<button onclick="docStart(${i})" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-indigo-600 text-white">${T('Start procedure', 'ابدأ الإجراء')}</button>`;
          else if (x.st === 'in_progress') act = `<button onclick="docFinish(${i})" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg border border-emerald-400 text-emerald-800 bg-emerald-50">${T('Mark done', 'خلّصت الخطوة')}</button>`;
          else act = docChip('bg-emerald-100 text-emerald-800', T('Done', 'خلصت'));
        } else if (edit) act = `<button onclick="docDropStep(${i})" class="text-slate-400 hover:text-rose-600"><i data-lucide="x" class="w-4 h-4"></i></button>`;
        const lab = x.lab && x.st !== 'done' ? `<button onclick="docToLab(${i})" class="text-[10px] font-bold ${hasLab ? 'bg-sky-100 text-sky-800' : 'bg-white border border-sky-300 text-sky-800'} px-2 py-0.5 rounded-full">${hasLab ? T('Lab ordered ✓', 'اتطلب من المعمل ✓') : T('Needs lab · order', 'محتاج معمل · اطلب')}</button>` : '';
        const cons = DOC.consents[n + ':' + x.id] ? docChip('bg-emerald-100 text-emerald-800', T('Consent signed', 'الموافقة اتوقّعت')) : '';
        const price = edit ? `<input value="${x.price}" oninput="docPrice(${i}, this.value)" class="w-20 border border-slate-300 rounded-lg px-2 py-1 text-xs text-end">` : `<b>${docE(x.price)}</b>`;
        return `<tr class="border-t border-slate-100 align-middle"><td class="py-2 pe-2 text-slate-400">${i + 1}</td><td class="py-2 pe-2"><div class="font-semibold text-slate-900">${T(x.en, x.ar)}${x.tooth ? ' <span class="text-slate-500">#' + x.tooth + '</span>' : ''}</div><div class="flex flex-wrap gap-1 mt-0.5">${lab}${cons}</div></td><td class="py-2 pe-2 whitespace-nowrap">${price}</td><td class="py-2 text-end">${act}</td></tr>`;
      }).join('');
      let foot = '';
      if (p.st === 'draft') foot = `<div class="flex flex-wrap justify-end gap-2"><button onclick="docApprovePlan()" class="px-4 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-semibold">${T('Approve plan & prepare the WhatsApp message', 'اعتمد الخطة وجهّز رسالة الواتساب')}</button></div><p class="text-[10px] text-slate-400">${T('Nothing reaches the patient until you approve the message too.', 'مفيش حاجة بتوصل للمريض غير بعد ما توافق على الرسالة كمان.')}</p>`;
      if (p.st === 'approved') { const a = docApprFind('plan:' + n); foot = a ? docApprCard(a, true) : ''; }
      if (p.st === 'presented') foot = `<div class="flex flex-wrap items-center justify-between gap-2 bg-amber-50 border border-amber-200 rounded-xl px-3 py-2 text-xs text-amber-900"><span>${T('Sent ' + (p.sentAt || '') + '. If he says no answer in 24 h, it becomes a call task for reception.', 'اتبعتت ' + (p.sentAt || '') + '. لو ما ردش خلال 24 ساعة بتتحول لمهمة اتصال للاستقبال.')}</span><button onclick="docAccept('${n.replace(/'/g, '')}', false)" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg border border-amber-400 bg-white">${T('He agreed at the clinic', 'وافق في العيادة')}</button></div>`;
      const note = p.st === 'accepted' ? `<p class="text-[10px] text-slate-400">${T('Accepted ' + p.at + '. Prices are frozen on each step. Consent is signed before each procedure.', 'اتوافق عليها ' + p.at + '. السعر متثبّت على كل خطوة. الموافقة بتتوقّع قبل كل إجراء.')}</p>` : '';
      return docCard(title + ' ' + docChip(stTxt[1], stTxt[0]) + (p.ai && p.st === 'draft' ? docChip('bg-fuchsia-100 text-fuchsia-800', '✨ ' + T('AI draft', 'مسودة AI')) : ''),
        `<table class="w-full text-xs"><tbody>${rows}</tbody></table><div class="flex items-center justify-between border-t border-slate-200 pt-2 text-xs"><span class="text-slate-500">${T('Total', 'الإجمالي')}</span><b id="doc-total" class="text-base text-slate-900">${docE(docPlanTotal(p))}</b></div>${foot}${note}`);
    }

    // ---- consent before a procedure
    function docConsentTxt(s) {
      const k = (s.en || '').toLowerCase();
      if (/root canal/.test(k)) return { what: ['Clean and fill the root canals of the tooth, 1–2 sessions', 'تنضيف وحشو قنوات الجذر للسن، جلسة أو اتنين'], risks: ['Pain or swelling for a few days; a tooth may need a crown afterwards; rarely a canal cannot be cleaned and extraction is needed', 'ألم أو ورم كام يوم؛ السن ممكن يحتاج تاج بعدها؛ نادراً قناة ما تتنضفش ويبقى لازم خلع'], alt: ['Extraction (and an implant or bridge later)', 'خلع السن (وزراعة أو جسر بعدين)'] };
      if (/crown/.test(k)) return { what: ['Shave the tooth, take an impression, place a temporary crown, fit the final crown in a later visit', 'برد السن، بصمة، تاج مؤقت، وتركيب التاج النهائي في زيارة تانية'], risks: ['Cold sensitivity for some days; the nerve may react and need a root canal; the temporary crown can come off', 'حساسية للبارد كام يوم؛ العصب ممكن يتأثر ويحتاج علاج عصب؛ التاج المؤقت ممكن يقع'], alt: ['A large filling (shorter life)', 'حشو كبير (عمره أقصر)'] };
      if (/extract|خلع/.test(k)) return { what: ['Remove the tooth under local anaesthesia', 'خلع السن بتخدير موضعي'], risks: ['Bleeding, swelling, dry socket; numbness for a few hours', 'نزيف، ورم، التهاب الحفرة؛ تنميل كام ساعة'], alt: ['Save the tooth if possible', 'إنقاذ السن لو ممكن'] };
      if (/whiten|تبييض/.test(k)) return { what: ['Bleaching gel in the clinic', 'جيل تبييض في العيادة'], risks: ['Temporary sensitivity; results differ between people; fillings and crowns do not whiten', 'حساسية مؤقتة؛ النتيجة بتختلف؛ الحشوات والتيجان ما بتتبيّضش'], alt: ['Cleaning only', 'تنضيف بس'] };
      return { what: ['Treat the tooth with local anaesthesia', 'علاج السن بتخدير موضعي'], risks: ['Mild pain or sensitivity for a few days; the work may need repair later', 'ألم أو حساسية بسيطة كام يوم؛ ممكن يحتاج تصليح بعدين'], alt: ['No treatment (the problem can grow)', 'من غير علاج (المشكلة ممكن تكبر)'] };
    }
    function docStart(i) {
      const n = PF.name, p = DOC.plans[n], x = p.steps[i];
      if (DOC.consents[n + ':' + x.id]) { x.st = 'in_progress'; renderPatientFile(); return; }
      DOC.cons = { n, i }; renderPatientFile();
    }
    function docConsentPane() {
      const n = DOC.cons.n, x = DOC.plans[n].steps[DOC.cons.i], c = docConsentTxt(x), pp = PF_PEOPLE[n] || {};
      const li = a => `<li>${T(a[0], a[1])}</li>`;
      const signer = pp.minor ? T('The guardian (' + pp.gEn + ') signs — the patient is ' + pp.age, 'ولي الأمر (' + pp.gAr + ') هو اللي يوقّع — المريض عمره ' + pp.age) : T('The patient signs', 'المريض هو اللي يوقّع');
      return docCard(T('Consent', 'موافقة المريض') + ' · ' + T(x.en, x.ar) + (x.tooth ? ' #' + x.tooth : ''),
        `<div class="text-xs space-y-2"><div><b>${T('What we will do', 'هنعمل إيه')}</b><ul class="list-disc ps-5 text-slate-600">${li(c.what)}</ul></div><div><b>${T('Possible problems', 'مشاكل ممكنة')}</b><ul class="list-disc ps-5 text-slate-600">${li(c.risks)}</ul></div><div><b>${T('Other options', 'بدائل')}</b><ul class="list-disc ps-5 text-slate-600">${li(c.alt)}</ul></div><div><b>${T('Cost', 'التكلفة')}</b>: ${docE(x.price)} ${T('(as in the accepted plan)', '(زي الخطة المتوافق عليها)')}</div></div>
        <label class="flex items-start gap-2 text-xs"><input id="docc-ok" type="checkbox" class="mt-0.5"><span>${T('I explained this in plain Arabic and answered the questions', 'شرحت ده بالعربي البسيط وجاوبت على الأسئلة')}</span></label>
        <div class="bg-amber-50 border border-amber-200 rounded-xl px-3 py-2 text-xs text-amber-900">${signer}</div>
        <div class="flex flex-wrap justify-end gap-2"><button onclick="DOC.cons=null;renderPatientFile()" class="px-3 py-1.5 rounded-lg border border-slate-300 text-xs font-semibold">${T('Not now', 'مش دلوقتي')}</button><button onclick="docSign()" class="px-4 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-semibold">${T('Hand the tablet — signed', 'سلّمت التابلت — اتوقّعت')}</button></div>`);
    }
    function docSign() {
      const ok = document.getElementById('docc-ok'); if (!ok || !ok.checked) { showToast(T('Tick that you explained it first', 'علّم إنك شرحتله الأول')); return; }
      const n = DOC.cons.n, x = DOC.plans[n].steps[DOC.cons.i], pp = PF_PEOPLE[n] || {};
      DOC.consents[n + ':' + x.id] = { at: docTm(), by: pp.minor ? 'guardian' : 'patient' }; x.st = 'in_progress'; DOC.cons = null;
      mwLog('Consent signed by ' + (pp.minor ? 'the guardian of ' : '') + n + ' for ' + x.en + (x.tooth ? ' #' + x.tooth : ''), 'موافقة ' + (pp.minor ? 'ولي أمر ' : '') + n + ' اتوقّعت على ' + x.ar + (x.tooth ? ' #' + x.tooth : ''));
      showToast(T('Consent saved in the file — procedure started', 'الموافقة اتحفظت في الملف — الإجراء بدأ')); docRefresh();
    }
    function docFinish(i) {
      const n = PF.name, p = DOC.plans[n], x = p.steps[i]; x.st = 'done';
      mwLog(x.en + (x.tooth ? ' #' + x.tooth : '') + ' marked done for ' + n, x.ar + (x.tooth ? ' #' + x.tooth : '') + ' اتعلّمت خلصت لـ ' + n);
      if (x.lab && !(DOC.labs[n] || []).length) showToast(T('Done. Now order the crown from the lab', 'خلصت. دلوقتي اطلب التاج من المعمل'));
      else showToast(T('Step done and recorded', 'الخطوة خلصت واتسجّلت'));
      docRefresh();
    }
    function docToLab(i) {
      const x = DOC.plans[PF.name].steps[i];
      DOC.labForm = { n: PF.name, lab: 'a', svc: 0, tooth: x.tooth, shade: 'A2', fromPlan: true }; PF.tab = 'lab'; renderPatientFile();
    }

    // ---- lab order linked to the next appointment
    function docLabStatus(o) { return { waiting_owner: ['waiting for the owner', 'مستني موافقة صاحب العيادة'], sent_to_lab: ['sent to the lab', 'اتبعت للمعمل'], cancelled: ['cancelled', 'اتلغى'] }[o.status] || ['sent', 'اتبعت']; }
    function docFmtDay(d) { try { return d.toLocaleDateString(isRTL ? 'ar-EG' : 'en-US', { day: 'numeric', month: 'long' }); } catch (e) { return ''; } }
    function docLabF() {
      const n = PF.name, pl = DOC.plans[n], st = pl && pl.steps.find(x => x.lab && x.st !== 'done');
      if (!DOC.labForm || DOC.labForm.n !== n) DOC.labForm = Object.assign({ n, lab: 'a', svc: 0, tooth: st ? st.tooth : 0, shade: 'A2', fromPlan: !!st }, {});
      return DOC.labForm;
    }
    function docLabSet(k, v) { DOC.labForm[k] = (k === 'svc') ? +v : (k === 'tooth' ? (parseInt(v, 10) || 0) : v); renderPatientFile(); }
    function docLabSend() {
      const n = PF.name, f = docLabF(), lab = DOC_LABS.find(l => l.k === f.lab), sv = lab.svc[f.svc], nx = DOC.next[n];
      const o = { id: ++DOC.seq, lab: lab.k, tooth: f.tooth, shade: f.shade, cost: sv[2], svc: { en: sv[0], ar: sv[1] }, status: 'sent_to_lab', appt: nx ? nx.en : '', apptAr: nx ? nx.ar : '', at: docTm() };
      if (sv[2] > DOC_LAB_LIMIT) {
        o.status = 'waiting_owner'; const id = ++DOC.seq; o.dec = id; DOC.labDec[id] = o;
        OW.decisions.unshift({ id, en: 'Lab order ' + sv[0] + ' for ' + n + ' costs EGP ' + sv[2].toLocaleString() + ' (above the EGP ' + DOC_LAB_LIMIT.toLocaleString() + ' limit)', ar: 'طلب معمل ' + sv[1] + ' لـ ' + n + ' تكلفته ' + sv[2].toLocaleString() + ' ج (أعلى من حد ' + DOC_LAB_LIMIT.toLocaleString() + ' ج)', who: 'Doctor', whoAr: 'الدكتور', ok: 'Approve', okAr: 'وافق', no: 'Refuse', noAr: 'ارفض' });
        showToast(T('Order saved. The cost is above the limit, so it went to «Needs your decision» in clinic management', 'الطلب اتسجّل. التكلفة أعلى من الحد فراح «محتاج قرارك» في إدارة العيادة'));
      } else showToast(T('Order sent to ' + lab.en + ' — linked to the next appointment', 'الطلب اتبعت لـ ' + lab.ar + ' — ومربوط بالموعد الجاي'));
      (DOC.labs[n] = DOC.labs[n] || []).unshift(o); DOC.labForm = null;
      mwLog('Lab order ' + sv[0] + ' #' + f.tooth + ' for ' + n + (o.status === 'sent_to_lab' ? ' sent to ' + lab.en : ' waiting for the owner'), 'طلب معمل ' + sv[1] + ' #' + f.tooth + ' لـ ' + n + (o.status === 'sent_to_lab' ? ' اتبعت لـ ' + lab.ar : ' مستني الأونر'));
      docRefresh();
    }
    function docLabPane() {
      const n = PF.name, f = docLabF(), lab = DOC_LABS.find(l => l.k === f.lab), sv = lab.svc[f.svc], nx = DOC.next[n], orders = DOC.labs[n] || [];
      const sel = (id, opts, cur, fn) => `<select onchange="${fn}(this.value)" class="mt-1 w-full border border-slate-300 rounded-lg px-2 py-1.5 text-xs bg-white">${opts.map(o => `<option value="${o[0]}" ${String(o[0]) === String(cur) ? 'selected' : ''}>${o[1]}</option>`).join('')}</select>`;
      let link;
      if (nx) {
        const ready = new Date(Date.now() + lab.days * 864e5), due = new Date(Date.now() + (nx.days - 1) * 864e5), ok = lab.days <= nx.days - 1;
        link = `<div class="rounded-xl px-3 py-2 text-xs ${ok ? 'bg-emerald-50 border border-emerald-200 text-emerald-900' : 'bg-rose-50 border border-rose-200 text-rose-800'}"><b>${T('Linked to the next appointment', 'مربوط بالموعد الجاي')}: ${T(nx.en, nx.ar)} · ${T(nx.whatEn, nx.whatAr)}</b><div>${T('The lab delivers about ' + docFmtDay(ready) + (ok ? ' — in time (needed by ' + docFmtDay(due) + ')' : ' — too late for the visit (needed by ' + docFmtDay(due) + ')'), 'المعمل بيسلّم حوالي ' + docFmtDay(ready) + (ok ? ' — في الميعاد (مطلوب قبل ' + docFmtDay(due) + ')' : ' — متأخر على الزيارة (مطلوب قبل ' + docFmtDay(due) + ')'))}</div>${ok ? '' : `<button onclick="docLabSet('lab','b')" class="mt-1 text-[11px] font-semibold px-2 py-0.5 rounded border border-rose-300 bg-white">${T('Use the express lab', 'استخدم المعمل السريع')}</button>`}</div>`;
      } else link = `<div class="rounded-xl px-3 py-2 text-xs bg-amber-50 border border-amber-200 text-amber-900 flex flex-wrap items-center justify-between gap-2"><span>${T('No fitting visit booked yet. Book it so the lab date matches.', 'لسه مفيش موعد تركيب. احجزه عشان ميعاد المعمل يتظبط عليه.')}</span><button onclick="mwBook('${n}')" class="text-[11px] font-semibold px-2.5 py-1 rounded-lg border border-amber-400 bg-white">${T('Book', 'احجز')}</button></div>`;
      const over = sv[2] > DOC_LAB_LIMIT ? `<div class="text-[11px] text-amber-700">${T('Above EGP ' + DOC_LAB_LIMIT.toLocaleString() + ' — will go to the owner to approve', 'أعلى من ' + DOC_LAB_LIMIT.toLocaleString() + ' ج — هيروح لصاحب العيادة يوافق')}</div>` : '';
      const form = `${f.fromPlan ? `<div class="text-[11px] bg-fuchsia-50 border border-fuchsia-200 rounded-xl px-3 py-2 text-slate-700">✨ ${T('Prepared from the accepted plan — check and sign', 'اتجهّز من الخطة المتوافق عليها — راجع ووقّع')}</div>` : ''}
        <div class="grid grid-cols-2 gap-3 text-xs"><label><span class="font-semibold text-slate-600">${T('Lab', 'المعمل')}</span>${sel('lab', DOC_LABS.map(l => [l.k, T(l.en, l.ar) + ' · ' + l.days + T(' days', ' أيام')]), f.lab, 'docLabSet.bind(null,"lab")')}</label>
        <label><span class="font-semibold text-slate-600">${T('Work', 'الشغل')}</span>${sel('svc', lab.svc.map((x, i) => [i, T(x[0], x[1]) + ' · ' + docE(x[2])]), f.svc, 'docLabSet.bind(null,"svc")')}</label>
        <label><span class="font-semibold text-slate-600">${T('Tooth', 'السن')}</span><input value="${f.tooth || ''}" onchange="docLabSet('tooth',this.value)" class="mt-1 w-full border border-slate-300 rounded-lg px-2 py-1.5"></label>
        <label><span class="font-semibold text-slate-600">${T('Shade', 'اللون')}</span>${sel('shade', ['A1', 'A2', 'A3', 'B1', 'B2'].map(x => [x, x]), f.shade, 'docLabSet.bind(null,"shade")')}</label></div>
        ${link}${over}<div class="flex justify-end"><button onclick="docLabSend()" class="px-4 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-semibold">${T('Sign & send to the lab', 'وقّع وابعت للمعمل')}</button></div>`;
      const list = orders.map(o => { const l = DOC_LABS.find(x => x.k === o.lab), s = docLabStatus(o); return `<div class="flex flex-wrap items-center justify-between gap-2 border border-slate-200 rounded-xl px-3 py-2 text-xs"><div><b>${T(o.svc.en, o.svc.ar)} #${o.tooth} · ${o.shade}</b><div class="text-slate-500">${T(l.en, l.ar)} · ${docE(o.cost)} · ${o.at}${o.appt ? ' · ' + T('for ' + o.appt, 'لموعد ' + o.apptAr) : ''}</div></div>${docChip(o.status === 'waiting_owner' ? 'bg-amber-100 text-amber-800' : 'bg-sky-100 text-sky-800', T(s[0], s[1]))}</div>`; }).join('');
      return docCard(T('Lab', 'المعمل'), `<div class="space-y-3">${form}</div>${list ? `<div class="space-y-2 pt-1"><div class="text-[10px] font-bold text-slate-400">${T('ORDERS FOR THIS PATIENT', 'طلبات المريض ده')}</div>${list}</div>` : ''}`);
    }
    const _docPrevOw = owDecide;
    owDecide = function (id, yes) {
      const o = DOC.labDec[id]; _docPrevOw(id, yes);
      if (o) { o.status = yes ? 'sent_to_lab' : 'cancelled'; docRefresh(); }
    };

    // ---- file: brief on top, compact on tablets so the chart is not pushed below the fold
    const _docPrevLeft = pfLeft;
    pfLeft = function () {
      if (pfWho() !== 'doctor') return _docPrevLeft();
      if (window.innerWidth >= 1280) return docBrief(PF.name) + _docPrevLeft();
      const p = pfP(), n = PF.name, a = pfAppt();
      const voice = [['Exam', 'كشف'], ['Recall', 'متابعة'], ['Limited', 'كشف سريع']].map(v => `<button onclick="pfVoice('${T(v[0], v[1])}')" class="text-[11px] font-bold px-3 py-1.5 rounded-lg bg-gradient-to-r from-rose-500 to-fuchsia-600 text-white flex items-center gap-1"><i data-lucide="mic" class="w-3.5 h-3.5"></i>${T(v[0], v[1])}</button>`).join('');
      return `<div class="bg-white border border-slate-200 rounded-2xl p-3 shadow-xs space-y-2">
        <div class="flex items-center justify-between gap-2"><div class="flex items-center gap-3"><div class="w-9 h-9 rounded-full bg-emerald-600 text-white font-bold flex items-center justify-center text-xs">${mwInit(n)}</div><div><div class="font-bold text-slate-900 hipaa-blur patient-name">${n}</div><div class="text-[11px] text-slate-500">${p.age} ${T('yrs', 'سنة')} · ${p.sex === 'F' ? T('Female', 'أنثى') : T('Male', 'ذكر')} · <span class="font-mono">${p.phone}</span>${a ? ' · ' + a.t + ' ' + T(a.proc, a.procAr) : ''}</div></div></div>
        <div class="flex items-center gap-1.5 flex-wrap justify-end">${voice}<button onclick="mwShowBar(null);switchView('view-mywork')" title="${T('Close', 'اقفل')}" class="text-slate-400 hover:text-slate-700 ms-1"><i data-lucide="x" class="w-4 h-4"></i></button></div></div>
        <details open class="group"><summary class="text-[10px] font-bold text-indigo-700 cursor-pointer select-none">${T('BEFORE YOU WALK IN (tap to hide)', 'قبل ما تدخل (دوس تخفي)')}</summary><div class="mt-1.5 flex flex-wrap gap-1.5">${docFacts(n).map(x => `<span class="inline-flex items-center gap-1 text-[10px] font-bold ${x.c} px-2 py-0.5 rounded-full"><i data-lucide="${x.ic}" class="w-3 h-3"></i>${T(x.en, x.ar)}</span>`).join('')}</div>${DOCP[n] ? `<div class="mt-1.5 text-[11px] text-slate-700 bg-fuchsia-50 border border-fuchsia-200 rounded-lg px-2 py-1.5"><b class="text-fuchsia-800">✨</b> ${T(DOCP[n].ai[0], DOCP[n].ai[1])}</div>` : ''}</details></div>`;
    };
    let _docRz; window.addEventListener('resize', () => { clearTimeout(_docRz); _docRz = setTimeout(() => { const v = document.getElementById('view-chart'); if (PM.who === 'doctor' && v && !v.classList.contains('hidden')) renderPatientFile(); }, 200); });
    const _docPrevPane = pfPane;
    pfPane = function () { return PF.tab === 'plan' ? docPlanPane() : PF.tab === 'lab' ? docLabPane() : _docPrevPane(); };
    const _docPrevGo = pfGo;
    pfGo = function (k) { if (k !== 'plan') DOC.cons = null; _docPrevGo(k); };
    const _docPrevOpenChart = openPatientChart;
    openPatientChart = function (name, i, d) { if (!DOC.cons || DOC.cons.n !== name) DOC.cons = null; _docPrevOpenChart(name, i, d); };

    // voice exam -> AI note draft waits in «needs you» until signed; finishing a visit drafts the after-care message
    const _docPrevVoice = pfVoice;
    pfVoice = function (kind) {
      _docPrevVoice(kind);
      if (!DOC.appr.some(x => x.id === 'note:' + PF.name)) DOC.appr.push({ id: 'note:' + PF.name, kind: 'note', n: PF.name });
      renderMyWork();
    };
    const _docPrevSave = pfSaveNote;
    pfSaveNote = function () { _docPrevSave(); DOC.appr = DOC.appr.filter(x => x.id !== 'note:' + PF.name); renderMyWork(); };
    const _docPrevAct = mwAct;
    mwAct = function (id, to) {
      _docPrevAct(id, to);
      if (to !== 'done' || PM.who !== 'doctor') return;
      const a = MW.appts.find(x => x.id === id); if (!a || DOC.appr.some(x => x.id === 'care:' + a.n)) return;
      DOC.appr.push({ id: 'care:' + a.n, kind: 'msg', n: a.n, whyEn: 'After-care instructions after today\'s visit', whyAr: 'تعليمات ما بعد زيارة النهارده',
        textAr: 'أهلاً ' + a.n + '، شكراً لزيارتك النهارده. ممكن تحس بحساسية بسيطة كام يوم، وخد المسكن لو احتجت. تجنّب الأكل الساخن أو الصلب لحد ما التنميل يروح. لو الألم زاد أو ظهر ورم كلمنا فوراً.',
        textEn: 'Hello ' + a.n + ', thank you for visiting today. Mild sensitivity for a few days is normal, take the painkiller if needed. Avoid hot or hard food until the numbness goes. If the pain increases or a swelling appears, message us right away.' });
      renderMyWork();
    };

    // «محتاجك دلوقتي»: the doctor's clinical approvals come first
    const _docPrevRender = renderMyWork;
    renderMyWork = function () {
      _docPrevRender(); docTop();
      if (!docWork()) return;
      const box = document.getElementById('mw-need'); if (!box) return;
      if (DOC.appr.length) {
        const html = DOC.appr.map(a => docApprCard(a)).join('');
        if (box.querySelector('p.text-slate-400')) box.innerHTML = html; else box.insertAdjacentHTML('afterbegin', html);
        const c = document.getElementById('mw-count'); if (c) c.innerText = (+c.innerText || 0) + DOC.appr.length;
        DOC.appr.filter(a => a.msgId).forEach(a => box.querySelectorAll('.border-emerald-300').forEach(el => { if (el.innerText.includes(a.n)) { el.remove(); if (c) c.innerText = Math.max(0, (+c.innerText || 0) - 1); } }));  // the AI draft replaces the plain «waiting for your reply» card
      }
      lucide.createIcons();
    };
    const _docPrevCount = hdrCount;
    hdrCount = function () { return _docPrevCount() + (docWork() ? DOC.appr.length : 0); };

    // end of day: what is still open, in one list
    function docEod() {
      const unsigned = MW.appts.filter(a => ['inchair', 'done', 'paid'].includes(a.st) && !(PF.notes[a.n] || {}).signed).map(a => a.n);
      const plansWait = Object.keys(DOC.plans).filter(n => ['presented', 'approved'].includes(DOC.plans[n].st));
      const labsWait = [].concat(...Object.keys(DOC.labs).map(n => DOC.labs[n].filter(o => o.status === 'waiting_owner').map(() => n)));
      const draftPlans = Object.keys(DOC.plans).filter(n => DOC.plans[n].st === 'draft');
      const seen = MW.appts.filter(a => ['done', 'paid'].includes(a.st)).length;
      const row = (ok, en, ar) => `<div class="flex items-start gap-2 text-xs"><span class="${ok ? 'text-emerald-600' : 'text-amber-600'} font-bold">${ok ? '✓' : '●'}</span><span class="text-slate-700">${T(en, ar)}</span></div>`;
      const m = document.createElement('div'); m.id = 'doc-eod'; m.className = 'fixed inset-0 z-[90] bg-slate-900/40 flex items-center justify-center p-4';
      m.innerHTML = `<div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-5 space-y-3"><div class="flex items-center justify-between"><h3 class="font-bold text-slate-900">${T('End of day', 'قفلة اليوم')}</h3><button onclick="document.getElementById('doc-eod').remove()" class="text-slate-400"><i data-lucide="x" class="w-4 h-4"></i></button></div>
        ${row(true, seen + ' patients seen today', seen + ' مريض اتكشف عليهم النهارده')}
        ${row(!unsigned.length, unsigned.length ? 'Exam notes not signed: ' + unsigned.join(', ') : 'All exam notes are signed', unsigned.length ? 'ملاحظات كشف ما اتوقّعتش: ' + unsigned.join('، ') : 'كل ملاحظات الكشف متوقّعة')}
        ${row(!DOC.appr.length, DOC.appr.length + ' AI drafts waiting for your approval', DOC.appr.length + ' مسودة AI مستنية موافقتك')}
        ${row(!draftPlans.length && !plansWait.length, (draftPlans.length ? 'Plans still draft: ' + draftPlans.join(', ') + '. ' : '') + (plansWait.length ? 'Waiting for patients: ' + plansWait.join(', ') : 'No plan waiting on a patient'), (draftPlans.length ? 'خطط لسه مسودة: ' + draftPlans.join('، ') + '. ' : '') + (plansWait.length ? 'مستنيين رد: ' + plansWait.join('، ') : 'مفيش خطة مستنية رد مريض'))}
        ${row(!labsWait.length, labsWait.length ? 'Lab orders waiting for the owner: ' + labsWait.length : 'No lab order stuck', labsWait.length ? 'طلبات معمل مستنية الأونر: ' + labsWait.length : 'مفيش طلب معمل واقف')}
        <label class="block text-xs"><span class="font-semibold text-slate-600">${T('Note for tomorrow (Sara reads it in the morning)', 'ملاحظة لبكرة (سارة بتقراها الصبح)')}</span><textarea id="doc-eod-note" rows="2" class="mt-1 w-full border border-slate-200 rounded-lg px-2 py-1.5"></textarea></label>
        <div class="flex justify-end"><button onclick="docEodClose()" class="px-4 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-semibold">${T('Close my day', 'اقفل يومي')}</button></div></div>`;
      document.body.appendChild(m); lucide.createIcons();
    }
    function docEodClose() {
      const t = (document.getElementById('doc-eod-note') || {}).value; document.getElementById('doc-eod').remove();
      mwLog('Doctor closed the day' + (t ? ' — note for tomorrow saved' : ''), 'الدكتور قفل اليوم' + (t ? ' — ملاحظة بكرة اتحفظت' : ''));
      showToast(T('Day closed. Open items stay in «Needs you» tomorrow.', 'اليوم اتقفل. اللي لسه مفتوح هيفضل في «محتاجك دلوقتي» بكرة.')); renderMyWork();
    }
    const _docPrevToggle = toggleRTL;
    toggleRTL = function () { _docPrevToggle(); renderMyWork(); };

'''
anchor = '    // initial render\n'
assert s.count(anchor) == 1
s = s.replace(anchor, js + anchor)
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('patched', P)
