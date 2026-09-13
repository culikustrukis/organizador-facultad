(function () {
  'use strict';
  var btnSem = document.getElementById('btnVistaSemanal');
  var btnLista = document.getElementById('btnVistaLista');
  var viewSem = document.getElementById('vistaSemanal');
  var viewLista = document.getElementById('vistaLista');

  function switchView(lista) {
    var active = 'px-3.5 py-1.5 rounded-lg bg-surface-container-lowest text-primary font-semibold text-xs shadow-xs transition-all';
    var idle = 'px-3.5 py-1.5 rounded-lg text-on-surface-variant hover:text-on-surface font-medium text-xs transition-colors';
    if (lista) {
      viewSem.classList.add('hidden');
      viewLista.classList.remove('hidden');
      btnLista.className = active;
      btnSem.className = idle;
    } else {
      viewLista.classList.add('hidden');
      viewSem.classList.remove('hidden');
      btnSem.className = active;
      btnLista.className = idle;
    }
  }
  if (btnSem && btnLista) {
    btnSem.addEventListener('click', function () { switchView(false); });
    btnLista.addEventListener('click', function () { switchView(true); });
  }

  function openModal(id) { var m = document.getElementById(id); if (m) m.classList.remove('hidden'); }
  function closeModal(id) { var m = document.getElementById(id); if (m) m.classList.add('hidden'); }

  var btnNueva = document.getElementById('btnNuevaClase');
  if (btnNueva) btnNueva.addEventListener('click', function () {
    document.getElementById('form-clase').reset();
    document.getElementById('clase_id').value = '';
    document.getElementById('modalClaseTitle').textContent = 'Nueva clase u horario';
    openModal('modal-clase');
  });

  function fillForm(clase) {
    var f = document.getElementById('form-clase');
    f.reset();
    document.getElementById('clase_id').value = clase.id || '';
    if (clase.materia_id) document.getElementById('clase-materia').value = clase.materia_id;
    document.getElementById('clase-dia').value = clase.dia;
    document.getElementById('clase-inicio').value = clase.hora_inicio;
    document.getElementById('clase-fin').value = clase.hora_fin;
    if (clase.tipo) document.getElementById('clase-tipo').value = clase.tipo;
    document.getElementById('clase-aula').value = clase.aula || '';
    document.getElementById('modalClaseTitle').textContent = 'Editar clase';
  }

  document.addEventListener('click', function (e) {
    var editBtn = e.target.closest('[data-edit-clase]');
    if (editBtn) {
      var id = Number(editBtn.getAttribute('data-edit-clase'));
      var clase = (window.CLASES_DATA || []).find(function (c) { return c.id === id; });
      if (clase) { fillForm(clase); openModal('modal-clase'); }
      return;
    }
    var delBtn = e.target.closest('[data-delete-clase]');
    if (delBtn) {
      var cid = Number(delBtn.getAttribute('data-delete-clase'));
      if (confirm('¿Eliminar esta clase del horario?')) {
        window.fetcher('/api/clases/' + cid, { method: 'DELETE' }).then(function (res) {
          if (res.ok) { window.location.reload(); }
          else { window.showToast('No se pudo eliminar.', 'error'); }
        });
      }
    }
  });

  var form = document.getElementById('form-clase');
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var id = document.getElementById('clase_id').value;
    var body = {
      materia_id: document.getElementById('clase-materia').value,
      dia: document.getElementById('clase-dia').value,
      hora_inicio: document.getElementById('clase-inicio').value,
      hora_fin: document.getElementById('clase-fin').value,
      tipo: document.getElementById('clase-tipo').value,
      aula: document.getElementById('clase-aula').value
    };
    var url = '/api/clases';
    var method = 'POST';
    if (id) { url += '/' + id; method = 'PUT'; }
    var btn = form.querySelector('[type="submit"]');
    if (btn) { btn.disabled = true; btn.classList.add('opacity-60'); }
    window.fetcher(url, { method: method, body: body }).then(function (res) {
      if (btn) { btn.disabled = false; btn.classList.remove('opacity-60'); }
      if (!res.ok) { window.showToast(res.message || 'No se pudo guardar.', 'error'); return; }
      closeModal('modal-clase');
      if (res.conflicts && res.conflicts.length) {
        var names = res.conflicts.map(function (c) { return c.materia + ' (' + c.horario + ')'; });
        window.showToast('Guardado con aviso: se superpone con ' + names.join(', '), 'error');
      } else {
        window.showToast('Clase guardada correctamente.');
      }
      setTimeout(function () { window.location.reload(); }, 700);
    }).catch(function () { window.showToast('Error de conexión.', 'error'); });
  });
})();