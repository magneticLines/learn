/* ══════════════════════════════════════════════════════════
   24-英语 · 提示词一键复制
   注意：navigator.clipboard 在 file:// 下不是安全上下文（isSecureContext
   为 false），直接调用会静默失败。所以必须保留 textarea + execCommand
   这条老路径 —— 本地双击打开 HTML 时走的就是它。
   ══════════════════════════════════════════════════════════ */

function flash(btn, ok) {
  var raw = btn.getAttribute('data-label') || btn.textContent;
  btn.setAttribute('data-label', raw);
  btn.textContent = ok ? '✓ 已复制' : '× 请手动选择';
  btn.classList.add(ok ? 'done' : 'fail');
  setTimeout(function () {
    btn.textContent = raw;
    btn.classList.remove('done', 'fail');
  }, 1800);
}

function legacyCopy(text) {
  var ta = document.createElement('textarea');
  ta.value = text;
  // 固定定位 + 不透明度 0：避免复制时页面跳动，也避免 display:none 导致选不中
  ta.style.cssText = 'position:fixed;top:0;left:0;opacity:0;';
  document.body.appendChild(ta);
  ta.focus();
  ta.select();
  var ok = false;
  try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
  document.body.removeChild(ta);
  return ok;
}

function writeClipboard(text, btn) {
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(text).then(
      function () { flash(btn, true); },
      function () { flash(btn, legacyCopy(text)); }
    );
  } else {
    flash(btn, legacyCopy(text));
  }
}

/* 复制单个提示词卡片 */
function copyPrompt(btn) {
  var body = btn.closest('.prompt-card').querySelector('.prompt-body');
  writeClipboard(body.textContent.trim(), btn);
}

/* 复制本页所有提示词，按卡片标题分节 —— 想一次性丢给 AI 时用 */
function copyAll(btn) {
  var blocks = [];
  document.querySelectorAll('.prompt-card').forEach(function (card) {
    var title = card.querySelector('.pc-title');
    var body = card.querySelector('.prompt-body');
    blocks.push('### ' + (title ? title.textContent.trim() : '') + '\n\n' + body.textContent.trim());
  });
  writeClipboard(blocks.join('\n\n---\n\n'), btn);
}
