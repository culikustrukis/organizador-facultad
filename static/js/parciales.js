(function () {
  'use strict';
  var DATA = window.EXAMENES_DATA || [];

  function openModal(id) { var m = document.getElementById(id); if (m) m.classList.remove('hidden'); }
  function closeModal(id) { var m = document.getElementById(id); if (m) m.classList.add('hidden'); }

  var btnNuevo = document.getElementById('btnNuevoExamen');
  if (btnNuevo) btnNuevo.addEventListener('click', function () {
    document.getElementById('form-examen').reset();
    document.getElementById('examen_id').value = '';
    document.getElementById('modalExamenTitle').textContent = 'Nuevo examen';
    openModal('modal-examen');
  });

  var currentFilter = 'all';
  document.querySelectorAll('.filter-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      currentFilter = btn.getAttribute('data-filter');
      document.querySelectorAll('.filter-btn').forEach(function (b) {
        b.className = 'filter-btn px-3.5 py-1.5 rounded-lg font-label-md text-label-md transition-all ' +
          (b === btn ? 'bg-surface-container-lowest text-primary font-semibold shadow-sm' : 'text-on-surface-variant hover:text-on-surface font-medium');
      });
      document.querySelectorAll('.exam-card').forEach(function (card) {
        var cat = card.getAttribute('data-category');
        card.style.display = currentFilter === 'all' || cat === currentFilter ? '' : 'none';
      });
    });
  });

  function fillForm(e) {
    var f = document.getElementById('form-examen');
    f.reset();
    document.getElementById('examen_id').value = e.id || '';
    if (e.materia_id) document.getElementById('exam-subject').value = e.materia_id;
    document.getElementById('exam-name').value = e.nombre || '';
    if (e.categoria) document.getElementById('exam-category').value = e.categoria;
    document.getElementById('exam-date').value = e.fecha ? e.fecha.slice(0, 10) : '';
    document.getElementById('exam-time').value = e.hora || '08:00';
    document.getElementById('exam-aula').value = e.aula || '';
    document.getElementById('modalExamenTitle').textContent = 'Editar examen';
  }

  function formData() {
    return {
      materia_id: document.getElementById('exam-subject').value,
      nombre: document.getElementById('exam-name').value,
      categoria: document.getElementById('exam-category').value,
      fecha: document.getElementById('exam-date').value,
      hora: document.getElementById('exam-time').value,
      aula: document.getElementById('exam-aula').value
    };
  }

  document.addEventListener('click', function (e) {
    var editBtn = e.target.closest('[data-edit-examen]');
    if (editBtn) {
      var id = Number(editBtn.getAttribute('data-edit-examen'));
      var ex = DATA.find(function (x) { return x.id === id; });
      if (ex) { fillForm(ex); openModal('modal-examen'); }
      return;
    }
    var delBtn = e.target.closest('[data-delete-examen]');
    if (delBtn) {
      var eid = Number(delBtn.getAttribute('data-delete-examen'));
      if (confirm('¿Eliminar este examen?')) {
        window.fetcher('/api/examenes/' + eid, { method: 'DELETE' }).then(function (res) {
          if (res.ok) { window.location.reload(); }
          else { window.showToast('No se pudo eliminar.', 'error'); }
        });
      }
    }
  });

  var form = document.getElementById('form-examen');
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var id = document.getElementById('examen_id').value;
    var url = '/api/examenes';
    var method = 'POST';
    if (id) { url += '/' + id; method = 'PUT'; }
    var btn = form.querySelector('[type="submit"]');
    if (btn) { btn.disabled = true; btn.classList.add('opacity-60'); }
    window.fetcher(url, { method: method, body: formData() }).then(function (res) {
      if (btn) { btn.disabled = false; btn.classList.remove('opacity-60'); }
      if (!res.ok) { window.showToast(res.message || 'No se pudo guardar.', 'error'); return; }
      closeModal('modal-examen');
      window.showToast('Examen guardado correctamente.');
      setTimeout(function () { window.location.reload(); }, 600);
    }).catch(function () { window.showToast('Error de conexión.', 'error'); });
  });
})();