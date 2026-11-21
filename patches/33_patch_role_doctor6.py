"""Doctor «الرسائل» round 6 (doctor view only; Sara's side and the calls tab are untouched): medical context + red flags on each card,
full readable AI draft with an «edited» mark, two-step send with an allergy check, «I will answer myself» / «hand back to Sara»,
touch/text floor. Idempotent.  Usage: python patch_role_doctor6.py [path-to-copy]   Backup: <copy>.bak_before_role_doctor6
"""
import io
import shutil
import sys

P = sys.argv[1] if len(sys.argv) > 1 else r'D:/craft/proto_doctor/index.html'
s = io.open(P, encoding='utf-8').read()
if 'ROLE_DOCTOR6_V1' in s:
    print('already patched')
    sys.exit(0)
assert 'ROLE_DOCTOR5_V1' in s, 'needs ROLE_DOCTOR5_V1'
shutil.copyfile(P, P + '.bak_before_role_doctor6')

js = r'''    // ===== ROLE DOCTOR 6 ===== ROLE_DOCTOR6_V1
    const D6 = { txt: {}, orig: {} };
    (function () { const st = document.createElement('style'); st.id = 'd6-style'; st.textContent = '.d3-doc #view-messages [class*="text-[9px]"], .d3-doc #view-messages [class*="text-[10px]"], .d3-doc #view-messages [class*="text-[11px]"] { font-size: 12px !important; }'; document.head.appendChild(st); })();
    const D6_FLAG = /نزيف|دم|ورم|ألم (جامد|شديد)|حرارة|صعوبة|اختناق|bleed|swell|fever|severe|breath/i;
    const D6_ALLERGEN = { penicillin: /penicillin|بنسلين|amoxi|أموكس|اموكس|augmentin|أوجمنتين|اوجمنتين/i };
    function d6Flag(m) { return D6_FLAG.test(m.last || ''); }
    function d6Conflict(n, text) {
      const p = PF_PEOPLE[n] || {}; if (!p.allergy) return '';
      const re = D6_ALLERGEN[(p.allergy || '').toLowerCase()] || new RegExp((p.allergy || '') + '|' + (p.allergyAr || ''), 'i');
      return re.test(text || '') ? T(p.allergy, p.allergyAr) : '';
    }
    function d6Id(m, dr) { return dr ? dr.id : 'm' + m.id; }
    function d6Text(m, dr) { const id = d6Id(m, dr); if (D6.txt[id] != null) return D6.txt[id]; const t = dr ? (isRTL ? dr.textAr : dr.textEn) : ''; D6.orig[id] = t; return t; }
    function d6Check(id, n) {
      const ta = document.getElementById('d6-ta-' + id); if (!ta) return;
      if (D6.orig[id] != null && D6.orig[id] === ta.value) delete D6.txt[id]; else D6.txt[id] = ta.value;
      const ed = document.getElementById('d6-ed-' + id); if (ed) ed.style.display = (D6.orig[id] != null && D6.orig[id] !== ta.value) ? '' : 'none';
      const bad = d6Conflict(n, ta.value), w = document.getElementById('d6-warn-' + id);
      if (w) { w.style.display = bad ? '' : 'none'; if (bad) w.innerText = T('⚠ The reply mentions ' + bad + ' and the patient is allergic. Edit before sending.', '⚠ الرد بيذكر ' + bad + ' والمريض عنده حساسية منه. عدّل قبل الإرسال.'); }
    }
    function d6Send(id, n, msgId, hasDraft) {
      const ta = document.getElementById('d6-ta-' + id), btn = document.getElementById('d6-send-' + id); if (!ta || !btn) return;
      if (!ta.value.trim()) { showToast(T('Write the reply first', 'اكتب الرد الأول')); return; }
      d6Check(id, n); if (d6Conflict(n, ta.value)) { showToast(T('Blocked: the reply conflicts with the allergy', 'اتمنع: الرد بيناقض الحساسية')); return; }
      if (btn.dataset.armed !== '1') {
        btn.dataset.armed = '1'; btn.dataset.lbl = btn.innerText; btn.innerText = T('Confirm: send to ' + n, 'تأكيد الإرسال لـ ' + n); btn.classList.replace('bg-indigo-600', 'bg-rose-600');
        setTimeout(() => { if (btn.isConnected && btn.dataset.armed === '1') { btn.dataset.armed = '0'; btn.innerText = btn.dataset.lbl; btn.classList.replace('bg-rose-600', 'bg-indigo-600'); } }, 5000); return;
      }
      delete D6.txt[id];
      if (hasDraft) docApprSend(id); else apMsgReply(msgId);
    }
    function d6Own(id) { const dr = docApprFind(id); if (dr) docApprReject(id); }
    function d6Hand(msgId) {
      const m = MSGS.find(x => x.id === msgId); if (!m) return; m.to = 'desk'; DOC.appr = DOC.appr.filter(a => a.msgId !== msgId);
      mwLog('Doctor handed the chat with ' + m.n + ' back to Sara', 'الدكتور رجّع محادثة ' + m.n + ' لسارة');
      showToast(T('Handed back to Sara', 'اتحوّلت لسارة')); apMessages(); apBadge(); renderMyWork();
    }
    function d6Card(m) {
      const dr = d2DraftOf(m.n), id = d6Id(m, dr), flag = d6Flag(m), txt = d6Text(m, dr), taId = 'd6-ta-' + id, p = PF_PEOPLE[m.n] || {}, d = DOCP[m.n];
      const rows = Math.max(5, Math.min(12, Math.ceil((txt.length || 120) / 55) + 1));
      const wait = dr ? d3Wait(dr) : '';
      const safe = ` oninput="d6Check('${id}','${m.n}')"`;
      return `<div class="bg-white border ${flag ? 'border-rose-300' : 'border-slate-200'} rounded-2xl p-4 shadow-xs space-y-2">
        <div class="flex flex-wrap items-center justify-between gap-2"><div class="flex flex-wrap items-center gap-2"><b class="text-sm text-slate-900 hipaa-blur patient-name">${m.n}</b><span class="text-xs font-mono text-slate-400">${m.t}</span>${flag ? d5Chip('bg-rose-600 text-white', '🚩 ' + T('Warning sign — answer today', 'علامة خطر — رد النهارده')) : ''}${wait}</div><button onclick="mwOpenByName('${m.n}')" class="text-xs font-semibold px-3 rounded-lg border border-slate-300 bg-white" style="min-height:36px">${T('Open file', 'افتح الملف')}</button></div>
        <div class="flex flex-wrap gap-1.5">${d5Chips(m.n)}</div>${d ? `<div class="text-xs text-slate-500">${T('Last: ' + d.last[0], 'آخر زيارة: ' + d.last[1])}</div>` : ''}
        <div class="text-xs text-amber-800 bg-amber-50 border border-amber-200 rounded-lg px-2 py-1 inline-block">${T('Why it reached you: ' + m.why, 'وصلتلك ليه: ' + m.whyAr)}</div>
        <div class="space-y-1"><div class="bg-slate-100 rounded-xl px-3 py-2 text-sm text-slate-800">${m.last}</div><div class="text-xs text-slate-400 ps-2">✨ ${T('Sara (AI): I passed your question to the doctor', 'سارة (AI): حوّلت سؤالك للدكتور')}</div></div>
        <div>${dr ? `<div class="flex items-center justify-between mb-1"><span class="text-xs font-bold text-fuchsia-800">✨ ${T('AI draft — read all of it, then approve', 'مسودة AI — اقراها كلها وبعدين وافق')}</span><span id="d6-ed-${id}" style="display:none" class="text-xs font-bold bg-sky-100 text-sky-800 px-2 py-0.5 rounded-full">${T('Edited by you', 'انت عدّلتها')}</span></div>` : `<div class="text-xs font-bold text-slate-500 mb-1">${T('No draft — write your reply', 'مفيش مسودة — اكتب ردّك')}</div>`}
          <textarea id="${taId}" rows="${rows}" ${safe} class="w-full border ${dr ? 'border-fuchsia-300 bg-fuchsia-50/40' : 'border-slate-300'} rounded-lg px-3 py-2 text-sm leading-relaxed">${txt}</textarea>
          <div id="d6-warn-${id}" style="display:none" class="mt-1 text-xs font-bold text-rose-700 bg-rose-50 border border-rose-200 rounded-lg px-2 py-1"></div></div>
        <div class="flex flex-wrap justify-end gap-2">${dr ? `<button onclick="d6Own('${id}')" class="text-xs font-semibold px-3 rounded-lg border border-slate-300 bg-white" style="min-height:36px">${T('I will answer myself', 'هرد بنفسي')}</button>` : ''}<button onclick="d6Hand(${m.id})" class="text-xs font-semibold px-3 rounded-lg border border-slate-300 bg-white" style="min-height:36px">${T('Hand back to Sara', 'رجّعها لسارة')}</button><button id="d6-send-${id}" onclick="d6Send('${id}','${m.n}',${m.id},${dr ? 'true' : 'false'})" class="text-sm font-bold px-4 rounded-lg bg-indigo-600 text-white" style="min-height:44px">${dr ? T('Approve & send on WhatsApp', 'وافق وابعت على واتساب') : T('Send', 'ابعت')}</button></div></div>`;
    }
    function d6Filter(f) { D2.msgF = f; apMessages(); }
    const _d6PrevMsgs = apMessages;
    apMessages = function () {
      _d6PrevMsgs();
      if (PM.who !== 'doctor' || (typeof RN2 !== 'undefined' && RN2.tab === 'calls')) return;
      const el = document.getElementById('view-messages'); if (!el) return;
      const grid = el.querySelector('.grid'); if (!grid) return;
      const prev = grid.previousElementSibling; if (prev && /d2MsgF/.test(prev.innerHTML)) prev.remove();
      const all = apMsgsFor().slice().sort((a, b) => (d6Flag(b) - d6Flag(a)) || (!!d2DraftOf(b.n) - !!d2DraftOf(a.n)) || a.t.localeCompare(b.t));
      const nUrg = all.filter(d6Flag).length, nDr = all.filter(m => d2DraftOf(m.n)).length, f = D2.msgF;
      const list = all.filter(m => f === 'urgent' ? d6Flag(m) : f === 'draft' ? d2DraftOf(m.n) : true);
      const bar = `<div class="bg-white border border-slate-200 rounded-2xl p-1.5 shadow-xs flex flex-wrap gap-1">${[['all', T('All', 'الكل') + ' (' + all.length + ')'], ['urgent', '🚩 ' + T('Warning signs', 'علامات خطر') + ' (' + nUrg + ')'], ['draft', '✨ ' + T('AI draft ready', 'مسودة AI جاهزة') + ' (' + nDr + ')']].map(t => `<button onclick="d6Filter('${t[0]}')" class="text-sm font-semibold px-4 rounded-xl ${f === t[0] ? 'bg-indigo-600 text-white' : 'text-slate-600 hover:bg-slate-100'}" style="min-height:44px">${t[1]}</button>`).join('')}</div>`;
      grid.outerHTML = bar + `<div id="d6-list" class="grid grid-cols-1 lg:grid-cols-2 gap-3 items-start">${list.map(d6Card).join('') || `<p class="text-sm text-slate-400">${T('No conversation matches.', 'مفيش محادثة مطابقة.')}</p>`}</div>`;
      list.forEach(m => { const dr = d2DraftOf(m.n); d6Check(d6Id(m, dr), m.n); });
      lucide.createIcons();
    };

'''
anchor = '    // initial render\n'
assert s.count(anchor) == 1
s = s.replace(anchor, js + anchor)
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('patched', P)
