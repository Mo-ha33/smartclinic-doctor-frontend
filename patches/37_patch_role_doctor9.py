"""Doctor «المواعيد» round 9 (doctor view only; nurse/Sara calendar untouched): no chair floor grid, no «احجز موعد», ONE calendar
(يوم/أسبوع/شهر/سنة really switch it). «مرضاي» = his patients only; «كل العيادة» = clinic load, read-only (numbers, no patient names).
Idempotent.  Usage: python patch_role_doctor9.py [path-to-copy]   Backup: <copy>.bak_before_role_doctor9
"""
import io
import shutil
import sys

P = sys.argv[1] if len(sys.argv) > 1 else r'D:/craft/proto_doctor/index.html'
s = io.open(P, encoding='utf-8').read()
if 'ROLE_DOCTOR9_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'ROLE_MAKER8_V1' in s, 'needs ROLE_MAKER8_V1'
assert 'ROLE_DOCTOR7_V1' in s, 'needs ROLE_DOCTOR7_V1'
shutil.copyfile(P, P + '.bak_before_role_doctor9')

js = r'''    // ===== ROLE DOCTOR 9 ===== ROLE_DOCTOR9_V1
    const D9 = { range: 'week', off: 0 };
    function d9Set(r) { D9.range = r; D9.off = 0; d9Apply(); }
    function d9Shift(n) { D9.off = n === 0 ? 0 : D9.off + n; d9Apply(); }
    function d9Day(t) { D9.range = 'day'; D9.off = Math.round((t - calToday().getTime()) / 864e5); d9Apply(); }
    function d9Month(o) { D9.range = 'month'; D9.off = o; d9Apply(); }
    function d9Mine() { return D7.focus === 'mine'; }
    function d9Cnt(d) { return calOff(d) ? 0 : d9Mine() ? drCount(d) : calCount(d); }
    function d9Tone(n) { return calTone(d9Mine() ? n * 1.6 : n); }
    function d9Unit() { return d9Mine() ? T('patients', 'مريض') : T('visits', 'موعد'); }
    function d9Body() {
      const t0 = calToday(), L = calLoc(), unit = d9Unit(); let title = '', body = '';
      const pill = (d, n) => calOff(d) ? `<div class="text-xs text-slate-400 mt-1">${T('Day off', 'إجازة')}</div>` : `<div class="mt-1 text-xs font-bold px-1.5 py-0.5 rounded inline-block ${d9Tone(n)}">${n} ${unit}</div>`;
      if (D9.range === 'day') {
        const d = new Date(t0); d.setDate(d.getDate() + D9.off);
        title = d.toLocaleDateString(L, { weekday: 'long', day: 'numeric', month: 'long' });
        if (D9.off === 0 && d9Mine()) {
          const mine = drMine(), nx = mine.findIndex(a => ['ready', 'inchair', 'arrived'].includes(a.st));
          body = mine.map((a, i) => `<button onclick="mwOpenFile(${a.id})" class="w-full text-start flex items-center gap-3 p-3 rounded-xl border ${i === nx ? 'border-indigo-400 bg-indigo-50 ring-2 ring-indigo-200' : 'border-slate-200 hover:bg-slate-50'} ${['done', 'paid', 'noshow'].includes(a.st) ? 'opacity-60' : ''}" style="min-height:44px"><span class="font-mono text-slate-500 w-12 shrink-0">${a.t}</span><span class="flex-1"><b class="text-slate-900 hipaa-blur patient-name">${a.n}</b> <span class="text-slate-500">· ${T(a.proc, a.procAr)}</span>${i === nx ? ` <span class="text-xs font-bold text-indigo-700">${T('← next', '← عليه الدور')}</span>` : ''}</span>${mwFlag(a)}${mwChip(a.st)}</button>`).join('') || `<p class="text-slate-400">${T('No patients today.', 'مفيش مرضى النهارده.')}</p>`;
        } else if (D9.off === 0) {
          const ch = [[0, 'Major chair', 'الكرسي الرئيسي'], [1, 'Minor / recall', 'بسيط / متابعة'], [2, 'Hygiene', 'تنظيف'], [3, 'Emergency', 'طوارئ']];
          body = `<div class="grid grid-cols-2 md:grid-cols-4 gap-2">${ch.map(c => `<div class="border border-slate-200 rounded-xl p-3"><div class="text-xs text-slate-500">${T(c[1], c[2])}</div><div class="text-lg font-bold text-slate-900">${MW.appts.filter(a => a.c === c[0]).length}</div></div>`).join('')}</div><div class="text-xs text-slate-500">${T('Whole clinic today', 'العيادة كلها النهارده')}: <b>${MW.appts.length}</b> ${T('visits', 'موعد')} · ${T('read-only: names are for Sara and the nurse', 'للقراءة بس: الأسماء عند سارة والممرضة')}</div>`;
        } else {
          const n = d9Cnt(d);
          body = `<div class="border border-slate-200 rounded-xl p-4">${pill(d, n)}<p class="text-xs text-slate-500 mt-2">${T('The details of this day open on the day itself.', 'تفاصيل اليوم ده بتظهر يوم الزيارة.')}</p></div>`;
        }
      }
      if (D9.range === 'week') {
        const ws = new Date(t0); ws.setDate(ws.getDate() - ((ws.getDay() + 1) % 7) + D9.off * 7);
        title = ws.toLocaleDateString(L, { day: 'numeric', month: 'short' }); let tot = 0;
        body = '<div class="grid grid-cols-7 gap-2">' + Array.from({ length: 7 }, (_, i) => { const d = new Date(ws); d.setDate(ws.getDate() + i); const n = d9Cnt(d), isT = d.getTime() === t0.getTime(); tot += n;
          const pills = (isT && d9Mine()) ? drMine().map(a => `<div class="flex gap-1 text-xs bg-white border border-slate-200 rounded px-1 py-0.5"><span class="font-mono text-slate-500 shrink-0">${a.t}</span><span dir="auto" class="truncate hipaa-blur patient-name">${a.n.split(' ')[0]}</span></div>`).join('') : '';
          return `<button onclick="d9Day(${d.getTime()})" class="border ${isT ? 'border-indigo-400 ring-2 ring-indigo-200' : 'border-slate-200'} rounded-xl p-2 text-start hover:bg-slate-50 min-h-[110px] flex flex-col gap-1"><div class="font-bold">${d.toLocaleDateString(L, { weekday: 'short' })}</div><div class="text-xs text-slate-400">${d.toLocaleDateString(L, { day: 'numeric', month: 'short' })}</div>${pill(d, n)}${pills}</button>`; }).join('') + `</div><div class="text-xs text-slate-500">${T('This week', 'الأسبوع ده')}: <b>${tot}</b> ${unit} · ${T('tap a day to open it', 'دوس على يوم يفتحه')}</div>`;
      }
      if (D9.range === 'month') {
        const m0 = new Date(t0.getFullYear(), t0.getMonth() + D9.off, 1); title = m0.toLocaleDateString(L, { month: 'long', year: 'numeric' });
        const lead = (m0.getDay() + 1) % 7, dim = new Date(m0.getFullYear(), m0.getMonth() + 1, 0).getDate(); let tot = 0, cells = '';
        for (let i = 0; i < lead; i++) cells += '<div></div>';
        for (let k = 1; k <= dim; k++) { const d = new Date(m0.getFullYear(), m0.getMonth(), k), n = d9Cnt(d); tot += n; cells += `<button onclick="d9Day(${d.getTime()})" class="h-14 border ${d.getTime() === t0.getTime() ? 'border-indigo-400 ring-2 ring-indigo-200' : 'border-slate-200'} rounded-lg p-1 text-start hover:bg-slate-50 flex flex-col justify-between"><span class="text-xs ${calOff(d) ? 'text-slate-300' : 'text-slate-700'}">${k}</span>${calOff(d) ? '' : `<span class="text-xs font-bold px-1 rounded self-start ${d9Tone(n)}">${n}</span>`}</button>`; }
        body = `<div class="grid grid-cols-7 gap-1">${cells}</div><div class="text-xs text-slate-500">${T('This month', 'الشهر ده')}: <b>${tot}</b> ${unit}</div>`;
      }
      if (D9.range === 'year') {
        const y = t0.getFullYear() + D9.off; title = String(y); let ytot = 0;
        body = '<div class="grid grid-cols-3 md:grid-cols-4 gap-2">' + Array.from({ length: 12 }, (_, mi) => { const dim = new Date(y, mi + 1, 0).getDate(); let n = 0; for (let k = 1; k <= dim; k++) n += d9Cnt(new Date(y, mi, k)); ytot += n;
          return `<button onclick="d9Month(${(y - t0.getFullYear()) * 12 + mi - t0.getMonth()})" class="border ${y === t0.getFullYear() && mi === t0.getMonth() ? 'border-indigo-400 ring-2 ring-indigo-200' : 'border-slate-200'} rounded-xl p-2 text-start hover:bg-slate-50" style="min-height:56px"><div class="font-bold">${new Date(y, mi, 1).toLocaleDateString(L, { month: 'long' })}</div><div class="text-xs text-slate-500">${n} ${unit}</div></button>`; }).join('') + `</div><div class="text-xs text-slate-500">${T('This year', 'السنة دي')}: <b>${ytot}</b> ${unit}</div>`;
      }
      return [title, body];
    }
    function d9Render(box) {
      const [title, body] = d9Body();
      const ranges = [['day', 'Day', 'يوم'], ['week', 'Week', 'أسبوع'], ['month', 'Month', 'شهر'], ['year', 'Year', 'سنة']].map(r => `<button onclick="d9Set('${r[0]}')" class="px-3 rounded-lg ${D9.range === r[0] ? 'bg-white shadow-xs text-indigo-700' : 'text-slate-500'}" style="min-height:36px">${T(r[1], r[2])}</button>`).join('');
      const nav = `<button onclick="d9Shift(-1)" class="p-1.5 border border-slate-200 rounded-lg" style="min-width:36px;min-height:36px"><i data-lucide="chevron-right" class="w-4 h-4 ltr:rotate-180 mx-auto"></i></button><button onclick="d9Shift(0)" class="px-3 border border-slate-200 rounded-lg text-xs" style="min-height:36px">${D9.off ? T('Back to now', 'رجوع للحالي') : T('Now', 'دلوقتي')}</button><button onclick="d9Shift(1)" class="p-1.5 border border-slate-200 rounded-lg" style="min-width:36px;min-height:36px"><i data-lucide="chevron-left" class="w-4 h-4 ltr:rotate-180 mx-auto"></i></button>`;
      box.innerHTML = `<div class="flex flex-wrap items-center justify-between gap-2"><div class="flex items-center gap-2">${nav}<b class="text-sm text-slate-900">${d9Mine() ? T('My patients', 'مرضاي') : T('Whole clinic (read-only)', 'كل العيادة (للقراءة)')} · ${title}</b></div><div class="flex items-center gap-1 bg-slate-100 p-1 rounded-xl font-semibold text-xs">${ranges}</div></div>${body}`;
      lucide.createIcons();
    }
    function d9Apply() {
      const g = document.getElementById('mw-grid'); if (!g) return; const card = g.closest('.lg\\:col-span-2'); if (!card) return;
      let box = document.getElementById('d9-cal');
      if (!(PM.who === 'doctor' && MW.calPage)) { if (box) box.remove(); return; }
      if (!box) { box = document.createElement('div'); box.id = 'd9-cal'; box.className = 'p-4 space-y-3 text-sm'; card.prepend(box); }
      [...card.children].forEach(ch => { if (ch !== box) ch.style.display = 'none'; });
      box.style.display = ''; d9Render(box);
    }
    d7Focus = function (f) { D7.focus = f; d7Apply(); d9Apply(); };
    const _d9PrevRender = renderMyWork;
    renderMyWork = function () { _d9PrevRender(); d9Apply(); };
    const _d9PrevDr = drRender;
    drRender = function () { _d9PrevDr(); d9Apply(); };
    const _d9PrevSwitch = switchView;
    switchView = function (id) { _d9PrevSwitch(id); if (id === 'view-scheduler' || id === 'view-mywork') d9Apply(); };
    const _d9PrevToggle = toggleRTL;
    toggleRTL = function () { _d9PrevToggle(); d9Apply(); };

'''
anchor = '    // initial render\n'
assert s.count(anchor) == 1
s = s.replace(anchor, js + anchor)
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('patched', P)
