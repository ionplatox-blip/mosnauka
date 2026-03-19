/**
 * МОСНАУКА — Переиспользуемая модалка «Связаться / Направить запрос»
 * 
 * Использование: подключить <script src="contact-modal.js"></script> перед </body>.
 * Вызов: openRequestModal('Контекст запроса')
 * 
 * Модалка автоматически создается при первом вызове (lazy injection).
 */

(function () {
  'use strict';

  let _injected = false;

  function injectModal() {
    if (_injected) return;
    _injected = true;

    const modal = document.createElement('div');
    modal.id = 'requestModal';
    modal.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.7);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);z-index:9999;display:none;align-items:center;justify-content:center;padding:1rem';
    modal.innerHTML = `
      <div style="background:#111;border:1px solid rgba(255,255,255,0.1);border-radius:1.5rem;max-width:32rem;width:100%;padding:2.5rem;position:relative;max-height:90vh;overflow-y:auto">
        <button onclick="closeRequestModal()" style="position:absolute;top:1.25rem;right:1.25rem;background:none;border:none;color:#52525b;font-size:1.5rem;cursor:pointer;z-index:1" aria-label="Закрыть">&times;</button>
        <div id="modalForm">
          <h2 style="font-size:1.25rem;font-weight:900;margin-bottom:0.25rem;color:white">📨 Направить запрос</h2>
          <div id="modalContext" style="font-size:0.75rem;color:#71717a;margin-bottom:1.5rem">через платформу МОСНАУКА</div>
          <label style="display:block;font-size:10px;text-transform:uppercase;font-weight:900;color:#71717a;margin-bottom:0.25rem;letter-spacing:0.15em">Ваше ФИО *</label>
          <input type="text" id="reqName" placeholder="Иванов Иван Иванович" style="width:100%;padding:0.75rem;border-radius:0.75rem;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);font-size:0.875rem;color:white;margin-bottom:0.75rem;outline:none;box-sizing:border-box">
          <label style="display:block;font-size:10px;text-transform:uppercase;font-weight:900;color:#71717a;margin-bottom:0.25rem;letter-spacing:0.15em">Организация</label>
          <input type="text" id="reqOrg" placeholder="ООО «Компания»" style="width:100%;padding:0.75rem;border-radius:0.75rem;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);font-size:0.875rem;color:white;margin-bottom:0.75rem;outline:none;box-sizing:border-box">
          <label style="display:block;font-size:10px;text-transform:uppercase;font-weight:900;color:#71717a;margin-bottom:0.25rem;letter-spacing:0.15em">Email *</label>
          <input type="email" id="reqEmail" placeholder="email@example.com" style="width:100%;padding:0.75rem;border-radius:0.75rem;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);font-size:0.875rem;color:white;margin-bottom:0.75rem;outline:none;box-sizing:border-box">
          <label style="display:block;font-size:10px;text-transform:uppercase;font-weight:900;color:#71717a;margin-bottom:0.5rem;letter-spacing:0.15em">Тип запроса <span style="text-transform:none;letter-spacing:normal;color:#52525b">(можно выбрать несколько)</span></label>
          <div id="reqType" style="display:grid;grid-template-columns:1fr;gap:0.5rem;margin-bottom:0.75rem">
            <label style="display:flex;align-items:center;gap:0.75rem;padding:0.75rem;border-radius:0.75rem;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);cursor:pointer"><input type="checkbox" value="Запрос на НИОКР" checked style="width:1rem;height:1rem;accent-color:#ef4444"><span style="font-size:0.875rem;color:#d4d4d8">Запрос на НИОКР</span></label>
            <label style="display:flex;align-items:center;gap:0.75rem;padding:0.75rem;border-radius:0.75rem;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);cursor:pointer"><input type="checkbox" value="Консультация" style="width:1rem;height:1rem;accent-color:#ef4444"><span style="font-size:0.875rem;color:#d4d4d8">Консультация</span></label>
            <label style="display:flex;align-items:center;gap:0.75rem;padding:0.75rem;border-radius:0.75rem;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);cursor:pointer"><input type="checkbox" value="Сотрудничество / Партнёрство" style="width:1rem;height:1rem;accent-color:#ef4444"><span style="font-size:0.875rem;color:#d4d4d8">Сотрудничество / Партнёрство</span></label>
            <label style="display:flex;align-items:center;gap:0.75rem;padding:0.75rem;border-radius:0.75rem;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);cursor:pointer"><input type="checkbox" value="Использование оборудования" style="width:1rem;height:1rem;accent-color:#ef4444"><span style="font-size:0.875rem;color:#d4d4d8">Использование оборудования</span></label>
            <label style="display:flex;align-items:center;gap:0.75rem;padding:0.75rem;border-radius:0.75rem;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);cursor:pointer"><input type="checkbox" value="Другое" style="width:1rem;height:1rem;accent-color:#ef4444"><span style="font-size:0.875rem;color:#d4d4d8">Другое</span></label>
          </div>
          <label style="display:block;font-size:10px;text-transform:uppercase;font-weight:900;color:#71717a;margin-bottom:0.25rem;letter-spacing:0.15em">Сообщение *</label>
          <textarea id="reqMsg" placeholder="Опишите ваш запрос..." style="width:100%;padding:0.75rem;border-radius:0.75rem;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);font-size:0.875rem;color:white;margin-bottom:1rem;min-height:5rem;resize:vertical;outline:none;box-sizing:border-box;font-family:inherit"></textarea>
          <button onclick="submitContactRequest()" style="width:100%;padding:0.75rem;border-radius:0.75rem;background:#ef4444;color:white;font-size:11px;font-weight:900;text-transform:uppercase;letter-spacing:0.15em;border:none;cursor:pointer;transition:background 0.2s" onmouseover="this.style.background='#dc2626'" onmouseout="this.style.background='#ef4444'">Отправить запрос</button>
        </div>
        <div id="modalSuccess" style="display:none;text-align:center;padding:2rem 0">
          <div style="font-size:3rem;margin-bottom:1rem">✅</div>
          <h3 style="font-size:1.125rem;font-weight:900;margin-bottom:0.5rem;color:white">Запрос отправлен!</h3>
          <p style="font-size:0.875rem;color:#a1a1aa">Ваш запрос направлен в личный кабинет организации через платформу МОСНАУКА. Ожидайте ответа в течение 3 рабочих дней.</p>
          <button onclick="closeRequestModal()" style="margin-top:1.5rem;width:100%;padding:0.75rem;border-radius:0.75rem;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);font-size:0.875rem;font-weight:700;color:#a1a1aa;cursor:pointer;transition:background 0.2s" onmouseover="this.style.background='rgba(255,255,255,0.1)'" onmouseout="this.style.background='rgba(255,255,255,0.05)'">Закрыть</button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);

    // Click backdrop to close
    modal.addEventListener('click', function (e) {
      if (e.target === modal) closeRequestModal();
    });

    // Escape to close
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && modal.style.display === 'flex') {
        closeRequestModal();
      }
    });
  }

  // ── Public API ──

  window.openRequestModal = function (context, prefillMessage) {
    injectModal();
    document.getElementById('modalContext').textContent = context || 'через платформу МОСНАУКА';
    document.getElementById('modalForm').style.display = '';
    document.getElementById('modalSuccess').style.display = 'none';
    // Reset fields
    document.getElementById('reqName').value = '';
    document.getElementById('reqOrg').value = '';
    document.getElementById('reqEmail').value = '';
    document.getElementById('reqMsg').value = prefillMessage || '';
    // Reset checkboxes — only first checked
    document.querySelectorAll('#reqType input[type=checkbox]').forEach(function (cb, i) {
      cb.checked = (i === 0);
    });
    document.getElementById('requestModal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
  };

  window.closeRequestModal = function () {
    var el = document.getElementById('requestModal');
    if (el) el.style.display = 'none';
    document.body.style.overflow = '';
  };

  // Backward compat: some passport pages call closeModal()
  if (typeof window.closeModal === 'undefined') {
    window.closeModal = window.closeRequestModal;
  }

  window.submitContactRequest = function () {
    var n = document.getElementById('reqName').value.trim();
    var e = document.getElementById('reqEmail').value.trim();
    var m = document.getElementById('reqMsg').value.trim();
    if (!n || !e || !m) {
      alert('Пожалуйста, заполните обязательные поля (ФИО, Email, Сообщение)');
      return;
    }
    // ── Save request to localStorage (universal) ──
    var o = document.getElementById('reqOrg').value.trim();
    var ctx = document.getElementById('modalContext').textContent || 'Не указан';
    var rid = 'REQ-' + Math.random().toString(36).substr(2, 8).toUpperCase();
    var req = {
      id: rid,
      date: new Date().toISOString(),
      task: m,
      executor: ctx,
      contact: { name: n, company: o, phone: '', email: e },
      status: 'processing'
    };
    try {
      var reqs = JSON.parse(localStorage.getItem('mosnauka_requests') || '[]');
      reqs.push(req);
      localStorage.setItem('mosnauka_requests', JSON.stringify(reqs));
    } catch (_) {}
    document.getElementById('modalForm').style.display = 'none';
    document.getElementById('modalSuccess').style.display = '';
  };

})();
