/*
 * Shared runtime for toolkit evidence cards.
 *
 * A page opts in by putting data-tk-key (storage key) and data-tk-title on <body>
 * and marking its structure inside .tk-doc with these hooks:
 *   .tk-field[data-k] > .lbl + .ed        single labelled answer
 *   .tk-field.tk-list                     free list, exported as "- line"
 *   .tk-field.tk-titlefield               record title, exported as "# Label — value"
 *   .tk-group[data-g][data-rep]           block of fields that can be repeated
 *   table.tk-table[data-t][data-tpl]      table; data-tpl = JSON placeholders for added rows
 *   .pick[data-k]                         0/1/2 score picker inside a table cell
 *   .tk-checks input[data-k]              checklist
 *   .tk-prompt pre                        copyable prompt text
 * Everything else (.tk-hint etc.) is guidance and is not exported.
 * window.Toolkit.toMarkdown() returns the current page as markdown.
 */
(function () {
  'use strict';
  var body = document.body;
  var KEY = body.dataset.tkKey;
  var TITLE = body.dataset.tkTitle || document.title;
  var doc = document.querySelector('.tk-doc');
  if (!KEY || !doc) return;

  // Storage can throw (private mode, blocked site data), so every access is guarded
  // and the page keeps working in memory when it does.
  var st = {};
  var canSave = true;
  try { st = JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { st = {}; }
  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(st)); canSave = true; }
    catch (e) { canSave = false; }
  }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  /* ---------- binding ---------- */

  function bindEd(el) {
    var k = el.dataset.k;
    if (st[k]) el.innerText = st[k];
    el.addEventListener('input', function () {
      var v = el.innerText.replace(/\n$/, '');
      if (v.trim()) st[k] = v; else { delete st[k]; el.innerHTML = ''; }
      save(); refresh();
    });
    // Rich paste would smuggle fonts/colours into the card; keep plain text only.
    el.addEventListener('paste', function (e) {
      e.preventDefault();
      var t = (e.clipboardData || window.clipboardData).getData('text');
      if (!document.execCommand('insertText', false, t)) {
        el.innerText += t;
        el.dispatchEvent(new Event('input'));
      }
    });
  }

  function bindPick(el) {
    var k = el.dataset.k;
    function paint() {
      el.querySelectorAll('button').forEach(function (b) {
        var on = st[k] === b.dataset.v;
        b.classList.toggle('on', on);
        b.setAttribute('aria-pressed', on ? 'true' : 'false');
      });
    }
    el.querySelectorAll('button').forEach(function (b) {
      b.addEventListener('click', function () {
        if (st[k] === b.dataset.v) delete st[k]; else st[k] = b.dataset.v;
        save(); paint(); refresh();
      });
    });
    paint();
  }

  function bindCheck(el) {
    var k = el.dataset.k;
    el.checked = !!st[k];
    el.addEventListener('change', function () {
      if (el.checked) st[k] = true; else delete st[k];
      save(); refresh();
    });
  }

  // Added rows/groups bind themselves on creation; the flag stops the later
  // page-wide pass from attaching a second set of listeners to them.
  function once(fn) {
    return function (el) { if (el._tkBound) return; el._tkBound = true; fn(el); };
  }
  function bindAll(root) {
    root.querySelectorAll('.ed[data-k]').forEach(once(bindEd));
    root.querySelectorAll('.pick[data-k]').forEach(once(bindPick));
    root.querySelectorAll('input[type=checkbox][data-k]').forEach(once(bindCheck));
  }

  function pickHtml(k) {
    return '<div class="pick" data-k="' + k + '" role="group" aria-label="0-2 分">' +
      '<button type="button" data-v="0">0</button><button type="button" data-v="1">1</button>' +
      '<button type="button" data-v="2">2</button></div>';
  }

  /* ---------- table rows ---------- */

  function setupTable(table) {
    var id = table.dataset.t;
    var tpl = JSON.parse(table.dataset.tpl || '[]');
    var heads = Array.prototype.map.call(table.querySelectorAll('thead th'), function (th) { return th.textContent; });
    var tbody = table.tBodies[0];
    var base = tbody.rows.length;
    var actions = document.createElement('div');
    actions.className = 'tk-actions';
    actions.innerHTML = '<button type="button" class="btn small" data-a="add">+ 添加一行</button>' +
      '<button type="button" class="btn small danger" data-a="del" hidden>删除最后添加的一行</button>';
    table.parentNode.appendChild(actions);
    var delBtn = actions.querySelector('[data-a="del"]');

    function addRow(r) {
      var tr = document.createElement('tr');
      tr.className = 'added';
      tr.innerHTML = tpl.map(function (c, ci) {
        var k = id + '.r' + r + '.c' + ci;
        var inner = c.pick ? pickHtml(k) :
          '<div class="ed" contenteditable="true" data-k="' + k + '" data-ph="' + esc(c.ph || '') + '"></div>';
        return '<td data-h="' + esc(heads[ci] || '') + '">' + inner + '</td>';
      }).join('');
      tbody.appendChild(tr);
      bindAll(tr);
    }
    var extra = +st['#' + id] || 0;
    for (var i = 0; i < extra; i++) addRow(base + i);
    delBtn.hidden = extra === 0;

    actions.querySelector('[data-a="add"]').addEventListener('click', function () {
      var n = +st['#' + id] || 0;
      addRow(base + n);
      st['#' + id] = n + 1;
      delBtn.hidden = false;
      save(); refresh();
    });
    delBtn.addEventListener('click', function () {
      var n = +st['#' + id] || 0;
      if (!n) return;
      var r = base + n - 1;
      var prefix = id + '.r' + r + '.';
      var hasData = Object.keys(st).some(function (k) { return k.indexOf(prefix) === 0; });
      if (hasData && !confirm('最后添加的一行里已经有内容，确定删除吗？')) return;
      Object.keys(st).forEach(function (k) { if (k.indexOf(prefix) === 0) delete st[k]; });
      tbody.removeChild(tbody.rows[tbody.rows.length - 1]);
      if (n - 1) st['#' + id] = n - 1; else delete st['#' + id];
      delBtn.hidden = n - 1 === 0;
      save(); refresh();
    });
  }

  /* ---------- repeatable field groups ---------- */

  function setupGroup(group) {
    var id = group.dataset.g;
    var label = group.dataset.rep || '一组';
    var tplHtml = group.innerHTML;
    var head = document.createElement('div');
    head.className = 'grp-head';
    head.textContent = label + ' 1';
    group.classList.add('rep');
    group.insertBefore(head, group.firstChild);
    var actions = document.createElement('div');
    actions.className = 'tk-actions';
    actions.innerHTML = '<button type="button" class="btn small" data-a="add">+ 再加' + esc(label) + '</button>' +
      '<button type="button" class="btn small danger" data-a="del" hidden>删除最后一个' + esc(label) + '</button>';
    group.parentNode.insertBefore(actions, group.nextSibling);
    var delBtn = actions.querySelector('[data-a="del"]');
    var copies = [];

    function addCopy(n) {
      var g = document.createElement('div');
      g.className = 'tk-group rep';
      g.dataset.copyOf = id;
      // Copies reuse the template markup but get suffixed keys, so the original stays untouched.
      g.innerHTML = '<div class="grp-head">' + esc(label) + ' ' + n + '</div>' +
        tplHtml.replace(/data-k="([^"]+)"/g, 'data-k="$1~' + n + '"');
      var anchor = copies.length ? copies[copies.length - 1] : group;
      anchor.parentNode.insertBefore(g, anchor.nextSibling);
      copies.push(g);
      bindAll(g);
    }
    var extra = +st['#' + id] || 0;
    for (var i = 0; i < extra; i++) addCopy(i + 2);
    delBtn.hidden = extra === 0;

    actions.querySelector('[data-a="add"]').addEventListener('click', function () {
      var n = +st['#' + id] || 0;
      addCopy(n + 2);
      st['#' + id] = n + 1;
      delBtn.hidden = false;
      save(); refresh();
    });
    delBtn.addEventListener('click', function () {
      var n = +st['#' + id] || 0;
      if (!n) return;
      var suffix = '~' + (n + 1);
      var keys = Object.keys(st).filter(function (k) { return k.slice(-suffix.length) === suffix && k.indexOf('~') > 0; });
      if (keys.length && !confirm('最后一组里已经有内容，确定删除吗？')) return;
      keys.forEach(function (k) { delete st[k]; });
      var g = copies.pop();
      g.parentNode.removeChild(g);
      if (n - 1) st['#' + id] = n - 1; else delete st['#' + id];
      delBtn.hidden = n - 1 === 0;
      save(); refresh();
    });
  }

  /* ---------- progress ---------- */

  var fill = document.getElementById('tk-fill');
  var count = document.getElementById('tk-count');
  function refresh() {
    var units = doc.querySelectorAll('.ed[data-k], .pick[data-k], input[type=checkbox][data-k]');
    var done = 0;
    units.forEach(function (u) { if (st[u.dataset.k]) done++; });
    doc.querySelectorAll('.tk-field').forEach(function (f) {
      var ed = f.querySelector('.ed[data-k]');
      f.classList.toggle('filled', !!(ed && st[ed.dataset.k]));
    });
    var total = units.length || 1;
    if (fill) fill.style.width = (done / total * 100) + '%';
    if (count) count.textContent = '已填 ' + done + ' / ' + units.length + (canSave ? ' · 自动保存' : ' · 浏览器禁止存储，刷新会丢失');
  }

  /* ---------- markdown export ---------- */

  function val(k) { return st[k] == null ? '' : String(st[k]); }
  function cellMd(s) { return String(s).replace(/\|/g, '\\|').replace(/\n/g, '<br>'); }
  function text(el) { return el.textContent.replace(/\s+/g, ' ').trim(); }

  function tableMd(table) {
    var out = [];
    var heads = Array.prototype.map.call(table.querySelectorAll('thead th'), text);
    out.push('| ' + heads.map(cellMd).join(' | ') + ' |');
    out.push('| ' + heads.map(function (_, i) {
      var th = table.querySelectorAll('thead th')[i];
      return th.classList.contains('num') ? '---:' : '---';
    }).join(' | ') + ' |');
    Array.prototype.forEach.call(table.tBodies[0].rows, function (tr) {
      var cells = Array.prototype.map.call(tr.cells, function (td) {
        var w = td.querySelector('[data-k]');
        if (!w) return cellMd(text(td));
        // Criterion cells keep the template's wording so the export still reads as the original card.
        var hint = td.querySelector('.cell-hint');
        var v = val(w.dataset.k);
        return cellMd(hint ? text(hint) + (v ? '\n→ ' + v : '') : v);
      });
      out.push('| ' + cells.join(' | ') + ' |');
    });
    return out.join('\n');
  }

  function fieldMd(f) {
    var ed = f.querySelector('.ed[data-k]');
    var label = text(f.querySelector('.lbl') || f);
    var v = ed ? val(ed.dataset.k) : '';
    if (f.classList.contains('tk-titlefield')) return '### ' + label + (v ? ' — ' + v : '');
    if (f.classList.contains('tk-list')) {
      var lines = v.split('\n').filter(function (l) { return l.trim(); });
      if (!lines.length) return '- ' + label;
      return lines.map(function (l) { return '- ' + l.replace(/^\s*-\s*/, ''); }).join('\n');
    }
    return '- **' + label.replace(/[：:]\s*$/, '') + '**：' + v.replace(/\n/g, '\n  ');
  }

  function toMarkdown() {
    var out = ['# ' + TITLE, '', '> 导出时间：' + new Date().toLocaleString() + '｜改编自 byoungd/up 模板（CC BY-NC 4.0）'];
    function push(block, gap) { if (gap !== false) out.push(''); out.push(block); }
    var lastWasField = false;
    function walk(node) {
      Array.prototype.forEach.call(node.children, function (el) {
        var tag = el.tagName;
        if (el.matches('.tk-hint, .tk-related')) { lastWasField = false; return; }
        if (el.matches('.tk-actions, script, template')) return;
        if (tag === 'H2') { push('## ' + text(el)); lastWasField = false; return; }
        if (tag === 'H3') { push('### ' + text(el)); lastWasField = false; return; }
        if (tag === 'H4') { push('#### ' + text(el)); lastWasField = false; return; }
        if (el.classList.contains('tk-caption')) { push('### ' + text(el)); lastWasField = false; return; }
        if (el.classList.contains('grp-head')) { push('**' + text(el) + '**'); lastWasField = false; return; }
        if (el.classList.contains('tk-field')) {
          // Consecutive fields form one list, so no blank line between them.
          push(fieldMd(el), !lastWasField || el.classList.contains('tk-titlefield'));
          lastWasField = !el.classList.contains('tk-titlefield');
          return;
        }
        if (tag === 'TABLE') { push(tableMd(el)); lastWasField = false; return; }
        if (el.classList.contains('tk-checks')) {
          push(Array.prototype.map.call(el.querySelectorAll('input[data-k]'), function (i) {
            return '- [' + (st[i.dataset.k] ? 'x' : ' ') + '] ' + text(i.parentNode);
          }).join('\n'));
          lastWasField = false; return;
        }
        if (el.classList.contains('tk-prompt')) {
          push('```text\n' + el.querySelector('pre').textContent.trim() + '\n```'); lastWasField = false; return;
        }
        walk(el);
      });
    }
    walk(doc);
    return out.join('\n').replace(/\n{3,}/g, '\n\n') + '\n';
  }

  /* ---------- export dialog ---------- */

  function copyText(t, done) {
    function fallback() {
      var ta = document.createElement('textarea');
      ta.value = t; ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select();
      var ok = false;
      try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
      document.body.removeChild(ta);
      done(ok);
    }
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(t).then(function () { done(true); }, fallback);
    } else fallback();
  }

  function download(t) {
    var name = (KEY.replace(/^up-toolkit-/, '').replace(/-v\d+$/, '') || 'toolkit') + '-' +
      new Date().toISOString().slice(0, 10) + '.md';
    var a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([t], { type: 'text/markdown;charset=utf-8' }));
    a.download = name;
    document.body.appendChild(a); a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500);
  }

  var dlg;
  function openExport() {
    var md = toMarkdown();
    if (!dlg) {
      dlg = document.createElement('dialog');
      dlg.className = 'tk-dlg';
      dlg.innerHTML = '<div class="dh"><b>导出为 Markdown</b><span class="msg" aria-live="polite"></span>' +
        '<div class="btns"><button type="button" class="btn primary" data-a="copy">复制</button>' +
        '<button type="button" class="btn" data-a="dl">下载 .md</button>' +
        '<button type="button" class="btn" data-a="close">关闭</button></div></div><textarea spellcheck="false"></textarea>';
      document.body.appendChild(dlg);
      var msg = dlg.querySelector('.msg');
      dlg.querySelector('[data-a="copy"]').addEventListener('click', function () {
        copyText(dlg.querySelector('textarea').value, function (ok) { msg.textContent = ok ? '已复制到剪贴板' : '复制失败，请手动全选复制'; });
      });
      dlg.querySelector('[data-a="dl"]').addEventListener('click', function () { download(dlg.querySelector('textarea').value); });
      dlg.querySelector('[data-a="close"]').addEventListener('click', function () { dlg.close(); });
    }
    dlg.querySelector('.msg').textContent = '';
    dlg.querySelector('textarea').value = md;
    if (dlg.showModal) dlg.showModal(); else dlg.setAttribute('open', '');
  }

  /* ---------- init ---------- */

  doc.querySelectorAll('table.tk-table[data-t]').forEach(setupTable);
  doc.querySelectorAll('.tk-group[data-rep]').forEach(setupGroup);
  bindAll(doc);

  document.querySelectorAll('.tk-prompt').forEach(function (p) {
    var b = p.querySelector('[data-a="copy"]');
    if (!b) return;
    b.addEventListener('click', function () {
      copyText(p.querySelector('pre').textContent.trim(), function (ok) {
        b.textContent = ok ? '已复制' : '复制失败';
        setTimeout(function () { b.textContent = '复制'; }, 1500);
      });
    });
  });

  var ex = document.querySelector('[data-tk="export"]');
  if (ex) ex.addEventListener('click', openExport);
  var rs = document.querySelector('[data-tk="reset"]');
  if (rs) rs.addEventListener('click', function () {
    if (!confirm('确定清空本页的全部填写内容吗？清空后无法恢复，建议先导出一份 Markdown。')) return;
    st = {};
    try { localStorage.removeItem(KEY); } catch (e) {}
    // Reload rebuilds the page from the static template, dropping added rows and groups.
    location.reload();
  });

  refresh();
  window.Toolkit = { toMarkdown: toMarkdown, refresh: refresh };
})();
