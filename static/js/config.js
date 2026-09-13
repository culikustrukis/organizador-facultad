(function () {
  'use strict';

  var avatarInput = document.getElementById('avatar-file');
  var avatarPreview = document.getElementById('avatar-preview');

  function setAvatar(url) { if (avatarPreview) avatarPreview.src = url; }

  if (avatarInput) {
    avatarInput.addEventListener('change', function () {
      var file = avatarInput.files && avatarInput.files[0];
      if (!file) return;
      if (file.size > 5 * 1024 * 1024) {
        window.showToast('La foto supera los 5 MB.', 'error');
        avatarInput.value = '';
        return;
      }
      var fd = new FormData();
      fd.append('avatar', file);
      fetch('/api/avatar', { method: 'POST', body: fd }).then(function (r) {
        return r.json();
      }).then(function (res) {
        if (res.ok) {
          setAvatar(res.avatar);
          window.showToast('Foto actualizada.');
          setTimeout(function () { window.location.reload(); }, 800);
        } else {
          window.showToast(res.message || 'No se pudo subir.', 'error');
        }
      }).catch(function () { window.showToast('Error de conexión.', 'error'); });
    });
  }

  var btnRemove = document.getElementById('btn-remove-photo');
  if (btnRemove) {
    btnRemove.addEventListener('click', function () {
      if (!confirm('¿Quitar tu foto de perfil?')) return;
      window.fetcher('/api/avatar/remove', { method: 'POST', body: {} }).then(function (res) {
        if (res.ok) { window.location.reload(); }
        else { window.showToast('No se pudo quitar la foto.', 'error'); }
      });
    });
  }

  var btnSave = document.getElementById('btn-save-name');
  if (btnSave) {
    btnSave.addEventListener('click', function () {
      var fullName = document.getElementById('input-fullname').value;
      var carrera = document.getElementById('input-carrera').value;
      var btn = btnSave;
      btn.disabled = true;
      btn.classList.add('opacity-60');
      window.fetcher('/api/perfil', { method: 'POST', body: { full_name: fullName, carrera: carrera } }).then(function (res) {
        btn.disabled = false;
        btn.classList.remove('opacity-60');
        if (res.ok) { window.showToast(res.message || 'Cambios guardados.'); }
        else { window.showToast(res.message || 'No se pudo guardar.', 'error'); }
      }).catch(function () { btn.disabled = false; btn.classList.remove('opacity-60'); window.showToast('Error de conexión.', 'error'); });
    });
  }

  document.querySelectorAll('input[name="tema"]').forEach(function (radio) {
    radio.addEventListener('change', function () {
      window.fetcher('/api/tema', { method: 'POST', body: { tema: radio.value } }).then(function (res) {
        if (res.ok) {
          document.documentElement.classList.toggle('dark', radio.value === 'dark');
          window.showToast('Tema aplicado.');
        } else {
          window.showToast('No se pudo aplicar el tema.', 'error');
          window.location.reload();
        }
      });
    });
  });
})();