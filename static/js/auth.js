(function () {
  'use strict';

  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('/sw.js').catch(function () {});
    });
  }

  function setError(form, message) {
    var el = form.querySelector('[data-form-error]');
    if (!el) {
      el = document.createElement('div');
      el.setAttribute('data-form-error', '');
      el.className = 'rounded-lg bg-error-container/50 border border-error/30 px-4 py-3 font-body-sm text-body-sm text-on-error-container flex items-start gap-2';
      el.innerHTML = '<span class="material-symbols-outlined text-[18px] text-error flex-shrink-0">error</span><span></span>';
      form.insertBefore(el, form.firstChild);
    }
    el.querySelector('span:last-child').textContent = message;
  }

  function clearErrors(form) {
    var el = form.querySelector('[data-form-error]');
    if (el) el.remove();
  }

  function submitForm(form, url, body, onOk) {
    clearErrors(form);
    var btn = form.querySelector('[type="submit"]');
    if (btn) { btn.disabled = true; btn.classList.add('opacity-60', 'cursor-wait'); }

    fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    }).then(function (r) {
      return r.json().catch(function () { return { ok: false, message: 'Error de conexión.' }; });
    }).then(function (res) {
      if (btn) { btn.disabled = false; btn.classList.remove('opacity-60', 'cursor-wait'); }
      if (res.ok && res.redirect) { window.location.href = res.redirect; return; }
      if (res.ok) { onOk && onOk(res); }
      else { setError(form, res.message || 'No se pudo completar la operación.'); }
    }).catch(function () {
      if (btn) { btn.disabled = false; btn.classList.remove('opacity-60', 'cursor-wait'); }
      setError(form, 'No se pudo conectar con el servidor.');
    });
  }

  var loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', function (e) {
      e.preventDefault();
      submitForm(loginForm, '/api/login', {
        username: document.getElementById('login-user').value,
        password: document.getElementById('login-password').value
      });
    });
  }

  var registerForm = document.getElementById('register-form');
  if (registerForm) {
    registerForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var pwd = document.getElementById('reg-password');
      var conf = document.getElementById('reg-confirm');
      if (pwd && conf && pwd.value !== conf.value) {
        setError(registerForm, 'Las contraseñas no coinciden.');
        return;
      }
      submitForm(registerForm, '/api/register', {
        full_name: document.getElementById('reg-fullname').value,
        email: document.getElementById('reg-email').value,
        username: document.getElementById('reg-user').value,
        password: pwd.value
      });
    });
  }

  document.querySelectorAll('[id^="toggle"]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var targetId = btn.getAttribute('data-target');
      var input = document.getElementById(targetId || btn.id.replace('toggle', ''));
      if (!input) return;
      input.type = input.type === 'password' ? 'text' : 'password';
      var icon = btn.querySelector('.material-symbols-outlined');
      if (icon) icon.textContent = input.type === 'password' ? 'visibility' : 'visibility_off';
    });
  });
})();