(function () {
  'use strict';

  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('/sw.js').catch(function () {});
    });
  }

  function fetchJson(url, opts) {
    opts = opts || {};
    opts.headers = Object.assign({}, opts.headers || {});
    if (opts.body && typeof opts.body === 'object') {
      opts.headers['Content-Type'] = 'application/json';
      opts.body = JSON.stringify(opts.body);
    }
    return fetch(url, opts).then(function (r) {
      return r.json().catch(function () { return { ok: false, message: 'Respuesta inválida del servidor.' }; });
    });
  }

  function toast(message, kind) {
    kind = kind || 'ok';
    var container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'fixed bottom-5 right-5 z-[100] flex flex-col gap-2';
      document.body.appendChild(container);
    }
    var el = document.createElement('div');
    var icon = kind === 'error' ? 'error' : 'check_circle';
    var accent = kind === 'error' ? 'text-error' : 'text-primary';
    el.className = 'flex items-center gap-2 px-4 py-3 rounded-xl bg-surface-container-lowest border border-outline-variant/40 shadow-lg animate-fade-in';
    el.innerHTML = '<span class="material-symbols-outlined text-[18px] ' + accent + '">' + icon + '</span><span class="font-body-sm text-body-sm text-on-surface">' + message + '</span>';
    container.appendChild(el);
    setTimeout(function () {
      el.classList.add('opacity-0', 'transition-opacity');
      setTimeout(function () { el.remove(); }, 250);
    }, 2600);
  }

  window.OpenModal = function (id) {
    var el = document.getElementById(id);
    if (el) el.classList.remove('hidden');
  };
  window.CloseModal = function (id) {
    var el = document.getElementById(id);
    if (el) el.classList.add('hidden');
  };

  document.addEventListener('click', function (e) {
    var anchor = e.target.closest('a[href^="#modal-"]');
    if (anchor) {
      var id = anchor.getAttribute('href').slice(1);
      e.preventDefault();
      window.OpenModal(id);
      return;
    }
    var closer = e.target.closest('[data-close-modal]');
    if (closer) {
      window.CloseModal(closer.getAttribute('data-close-modal'));
      return;
    }
    var backdrop = e.target.closest('.modal-backdrop');
    if (backdrop && e.target === backdrop && backdrop.classList.contains('hidden') === false) {
      backdrop.classList.add('hidden');
    }
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal-backdrop:not(.hidden)').forEach(function (b) {
        b.classList.add('hidden');
      });
    }
  });

  var themeBtn = document.getElementById('theme-toggle');
  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      var isDark = document.documentElement.classList.contains('dark');
      var next = isDark ? 'light' : 'dark';
      fetchJson('/api/tema', { method: 'POST', body: { tema: next } }).then(function (res) {
        if (res.ok) {
          document.documentElement.classList.toggle('dark', next === 'dark');
          var icon = themeBtn.querySelector('.material-symbols-outlined');
          if (icon) icon.textContent = next === 'dark' ? 'light_mode' : 'dark_mode';
        }
      });
    });
  }

  var sidebarEl = document.getElementById('app-sidebar');
  var backdropEl = document.getElementById('sidebar-backdrop');
  var sidebarToggle = document.getElementById('sidebar-toggle');
  var sidebarClose = document.getElementById('app-sidebar-close');

  function openSidebar() {
    document.body.classList.add('sidebar-open');
  }
  function closeSidebar() {
    document.body.classList.remove('sidebar-open');
  }
  if (sidebarToggle) sidebarToggle.addEventListener('click', openSidebar);
  if (sidebarClose) sidebarClose.addEventListener('click', closeSidebar);
  if (backdropEl) backdropEl.addEventListener('click', closeSidebar);

  if (sidebarEl) {
    sidebarEl.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', closeSidebar);
    });
  }

  window.addEventListener('resize', function () {
    if (window.innerWidth >= 768) closeSidebar();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeSidebar();
  });

  window.fetcher = fetchJson;
  window.showToast = toast;
})();