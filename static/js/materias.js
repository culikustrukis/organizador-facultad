(function () {
  'use strict';

  function openModal(id) { var m = document.getElementById(id); if (m) m.classList.remove('hidden'); }
  function closeModal(id) { var m = document.getElementById(id); if (m) m.classList.add('hidden'); }

  var btnOpen = document.getElementById('openModalBtn');
  if (btnOpen) btnOpen.addEventListener('click', function () {
    document.getElementById('form-materia').reset();
    document.getElementById('materia_id').value = '';
    document.getElementById('modalMateriaTitle').textContent = 'Nueva materia';
    setColor('indigo');
    openModal('modal-materia');
  });

  function setColor(key) {
    document.querySelectorAll('#color-picker label').forEach(function (l) {
      var input = l.querySelector('input[type="radio"]');
      if (input && input.value === key) { input.checked = true; l.style.boxShadow = '0 0 0 2px var(--c-primary, #3525cd)'; }
      else if (input) { l.style.boxShadow = 'none'; }
    });
  }
  document.getElementById('color-picker').addEventListener('change', function (e) {
    if (e.target.type === 'radio') setColor(e.target.value);
  });

  function fillForm(m) {
    var f = document.getElementById('form-materia');
    f.reset();
    document.getElementById('materia_id').value = m.id || '';
    document.getElementById('materia-codigo').value = m.codigo || '';
    document.getElementById('materia-nombre').value = m.nombre || '';
    document.getElementById('materia-profesor').value = m.profesor || '';
    var modalidad = document.querySelector('input[name="modalidad"][value="' + (m.modalidad || 'presencial') + '"]');
    if (modalidad) modalidad.checked = true;
    document.getElementById('materia-horas').value = m.horas_semana || 4;
    document.getElementById('materia-regimen').value = m.regimen || 'promocionable';
    document.getElementById('materia-aula').value = m.aula || '';
    document.getElementById('materia-comision').value = m.comision || '';
    setColor(m.color || 'indigo');
    document.getElementById('modalMateriaTitle').textContent = 'Editar materia';
  }

  function formData() {
    return {
      codigo: document.getElementById('materia-codigo').value,
      nombre: document.getElementById('materia-nombre').value,
      profesor: document.getElementById('materia-profesor').value,
      modalidad: (document.querySelector('input[name="modalidad"]:checked') || {}).value || 'presencial',
      horas_semana: document.getElementById('materia-horas').value,
      regimen: document.getElementById('materia-regimen').value,
      aula: document.getElementById('materia-aula').value,
      comision: document.getElementById('materia-comision').value,
      color: (document.querySelector('input[name="color"]:checked') || {}).value || 'indigo'
    };
  }

  document.addEventListener('click', function (e) {
    var editBtn = e.target.closest('[data-edit-materia]');
    if (editBtn) {
      var id = Number(editBtn.getAttribute('data-edit-materia'));
      var m = (window.MATERIAS_DATA || []).find(function (x) { return x.id === id; });
      if (m) { fillForm(m); openModal('modal-materia'); }
      return;
    }
    var delBtn = e.target.closest('[data-delete-materia]');
    if (delBtn) {
      var mid = Number(delBtn.getAttribute('data-delete-materia'));
      if (confirm('¿Eliminar esta materia y sus clases/tareas asociadas?')) {
        window.fetcher('/api/materias/' + mid, { method: 'DELETE' }).then(function (res) {
          if (res.ok) { window.location.reload(); }
          else { window.showToast('No se pudo eliminar.', 'error'); }
        });
      }
    }
  });

  var form = document.getElementById('form-materia');
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var id = document.getElementById('materia_id').value;
    var url = '/api/materias';
    var method = 'POST';
    if (id) { url += '/' + id; method = 'PUT'; }
    var btn = form.querySelector('[type="submit"]');
    if (btn) { btn.disabled = true; btn.classList.add('opacity-60'); }
    window.fetcher(url, { method: method, body: formData() }).then(function (res) {
      if (btn) { btn.disabled = false; btn.classList.remove('opacity-60'); }
      if (!res.ok) { window.showToast(res.message || 'No se pudo guardar.', 'error'); return; }
      closeModal('modal-materia');
      window.showToast('Materia guardada correctamente.');
      setTimeout(function () { window.location.reload(); }, 600);
    }).catch(function () { window.showToast('Error de conexión.', 'error'); });
  });

  var search = document.getElementById('search-materia');
  var filter = document.getElementById('filter-estado');
  function aplicarFiltro() {
    var q = (search.value || '').toLowerCase().trim();
    var est = filter ? (filter.value || 'todas') : 'todas';
    document.querySelectorAll('#tabla-materias tr[data-nombre]').forEach(function (tr) {
      var nombre = (tr.getAttribute('data-nombre') || '');
      var prof = (tr.getAttribute('data-profesor') || '');
      var estado = (tr.getAttribute('data-estado') || '');
      var matchQ = !q || nombre.indexOf(q) !== -1 || prof.indexOf(q) !== -1;
      var matchE = est === 'todas' ||
        (est === 'promocionable' && (estado === 'promocionable' || estado === 'promocional')) ||
        (est === 'con_final' && estado === 'con.final');
      tr.style.display = matchQ && matchE ? '' : 'none';
    });
  }
  if (search) search.addEventListener('input', aplicarFiltro);
  if (filter) filter.addEventListener('change', aplicarFiltro);
})();