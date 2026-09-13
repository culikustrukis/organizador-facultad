(function () {
  'use strict';
  var DATA = window.TAREAS_DATA || [];

  function openModal(id) { var m = document.getElementById(id); if (m) m.classList.remove('hidden'); }
  function closeModal(id) { var m = document.getElementById(id); if (m) m.classList.add('hidden'); }

  var btnList = document.getElementById('btn-view-list');
  var btnKanban = document.getElementById('btn-view-kanban');
  var viewList = document.getElementById('view-list');
  var viewKanban = document.getElementById('view-kanban');
  function switchView(kanban) {
    var active = 'flex items-center gap-1.5 px-space-md py-1.5 rounded-lg bg-surface-container-lowest text-primary font-label-md text-label-md shadow-sm transition-all';
    var idle = 'flex items-center gap-1.5 px-space-md py-1.5 rounded-lg text-on-surface-variant font-label-md text-label-md hover:text-on-surface transition-all';
    if (kanban) {
      viewList.classList.add('hidden');
      viewKanban.classList.remove('hidden');
      viewKanban.classList.add('grid');
      btnKanban.className = active;
      btnList.className = idle;
    } else {
      viewKanban.classList.add('hidden');
      viewKanban.classList.remove('grid');
      viewList.classList.remove('hidden');
      btnList.className = active;
      btnKanban.className = idle;
    }
  }
  if (btnList && btnKanban) {
    btnList.addEventListener('click', function () { switchView(false); });
    btnKanban.addEventListener('click', function () { switchView(true); });
  }

  function taskById(id) { return DATA.find(function (t) { return t.id === id; }); }
  function isUrgent(t) {
    if (!t || t.estado !== 'pendiente') return false;
    if (t.prioridad === 'alta') return true;
    if (!t.fecha_limite) return false;
    var dt = new Date(t.fecha_limite.replace('T', 'T'));
    var now = new Date();
    return !isNaN(dt) && dt <= now;
  }

  var currentFilter = 'all';
  var searchTerm = '';
  function rowMatches(row) {
    var id = Number(row.getAttribute('data-id'));
    var t = taskById(id);
    var estado = row.getAttribute('data-estado');
    var warmatch = true;
    if (currentFilter === 'pending' && estado !== 'pendiente') warmatch = false;
    else if (currentFilter === 'done' && estado !== 'completada') warmatch = false;
    else if (currentFilter === 'urgent' && !(estado === 'pendiente' && isUrgent(t))) warmatch = false;
    if (!warmatch) return false;
    if (searchTerm) {
      var haystack = row.getAttribute('data-busqueda') || '';
      return haystack.indexOf(searchTerm) !== -1;
    }
    return true;
  }

  function applyListFilter() {
    document.querySelectorAll('#view-list .task-row').forEach(function (row) {
      row.style.display = rowMatches(row) ? '' : 'none';
    });
  }

  document.querySelectorAll('#filtros .filter-tab').forEach(function (btn) {
    btn.addEventListener('click', function () {
      currentFilter = btn.getAttribute('data-filter');
      document.querySelectorAll('#filtros .filter-tab').forEach(function (b) {
        b.className = 'filter-tab px-space-md py-1.5 rounded-lg font-label-md text-label-md transition-colors ' +
          (b === btn ? 'bg-surface-container-high text-primary font-semibold' : 'text-on-surface-variant hover:bg-surface-container');
      });
      applyListFilter();
    });
  });

  var search = document.getElementById('task-search');
  if (search) search.addEventListener('input', function () {
    searchTerm = search.value.toLowerCase().trim();
    applyListFilter();
  });

  function updateKanbanCounts() {
    document.querySelectorAll('.kanban-col').forEach(function (col) {
      col.querySelector('.kanban-count').textContent = col.querySelectorAll('.kanban-card').length;
    });
  }
  updateKanbanCounts();

  function resetForm() {
    document.getElementById('form-tarea').reset();
    document.getElementById('tarea_id').value = '';
    document.getElementById('modalTareaTitle').textContent = 'Nueva Tarea o TP';
  }

  var btnNueva = document.getElementById('btnNuevaTarea');
  if (btnNueva) btnNueva.addEventListener('click', function () { resetForm(); openModal('modal-tarea'); });

  function fillForm(t) {
    var f = document.getElementById('form-tarea');
    f.reset();
    document.getElementById('tarea_id').value = t.id || '';
    document.getElementById('task-title').value = t.titulo || '';
    if (t.materia_id) document.getElementById('task-subject').value = t.materia_id;
    if (t.fecha_limite) document.getElementById('task-deadline').value = t.fecha_limite;
    var prio = document.querySelector('input[name="prioridad"][value="' + ((t.prioridad) || 'media') + '"]');
    if (prio) prio.checked = true;
    var tipo = document.querySelector('input[name="tipo_entrega"][value="' + ((t.tipo_entrega) || 'individual') + '"]');
    if (tipo) tipo.checked = true;
    document.getElementById('task-notes').value = t.descripcion || '';
    document.getElementById('modalTareaTitle').textContent = 'Editar tarea';
  }

  function formData() {
    return {
      titulo: document.getElementById('task-title').value,
      materia_id: document.getElementById('task-subject').value,
      fecha_limite: document.getElementById('task-deadline').value,
      prioridad: (document.querySelector('input[name="prioridad"]:checked') || {}).value || 'media',
      tipo_entrega: (document.querySelector('input[name="tipo_entrega"]:checked') || {}).value || 'individual',
      descripcion: document.getElementById('task-notes').value
    };
  }

  var form = document.getElementById('form-tarea');
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var id = document.getElementById('tarea_id').value;
    var url = '/api/tareas';
    var method = 'POST';
    if (id) { url += '/' + id; method = 'PUT'; }
    var btn = form.querySelector('[type="submit"]');
    if (btn) { btn.disabled = true; btn.classList.add('opacity-60'); }
    window.fetcher(url, { method: method, body: formData() }).then(function (res) {
      if (btn) { btn.disabled = false; btn.classList.remove('opacity-60'); }
      if (!res.ok) { window.showToast(res.message || 'No se pudo guardar.', 'error'); return; }
      closeModal('modal-tarea');
      window.showToast('Tarea guardada correctamente.');
      setTimeout(function () { window.location.reload(); }, 600);
    }).catch(function () { window.showToast('Error de conexión.', 'error'); });
  });

  var togglingIds = {};

  function applyTaskState(tarea, estado) {
    tarea.estado = estado;
    var esCompletada = estado === 'completada';
    var id = tarea.id;

    var row = document.querySelector('.task-row[data-id="' + id + '"]');
    if (row) {
      row.setAttribute('data-estado', estado);
      var btn = row.querySelector('[data-toggle-tarea]');
      if (btn) {
        btn.className = 'mt-1 flex-shrink-0 w-5 h-5 rounded-md flex items-center justify-center transition-colors ' +
          (esCompletada ? 'bg-primary text-on-primary' : 'bg-surface-container-highest text-transparent hover:text-primary');
        btn.setAttribute('title', esCompletada ? 'Marcar como pendiente' : 'Marcar como completada');
      }
      var titleEl = row.querySelector('h2');
      if (titleEl) {
        titleEl.classList.toggle('line-through', esCompletada);
        titleEl.classList.toggle('text-on-surface-variant', esCompletada);
      }
      var header = titleEl ? titleEl.parentElement : null;
      if (header) {
        var chips = Array.prototype.filter.call(header.children, function (el) { return el !== titleEl; });
        var doneBadge = header.querySelector('.badge-completada-optimistic');
        if (esCompletada) {
          chips.forEach(function (el) { el.style.display = 'none'; });
          if (!doneBadge) {
            var span = document.createElement('span');
            span.className = 'px-1.5 py-0.2 rounded bg-primary/10 text-primary font-label-sm text-label-sm font-semibold badge-completada-optimistic';
            span.textContent = 'Completada';
            header.appendChild(span);
          }
        } else {
          if (doneBadge) doneBadge.remove();
          chips.forEach(function (el) { el.style.display = ''; });
        }
      }
    }

    var card = null;
    document.querySelectorAll('#view-kanban .kanban-card').forEach(function (c) {
      var del = c.querySelector('[data-delete-tarea]');
      if (del && Number(del.getAttribute('data-delete-tarea')) === id) card = c;
    });
    if (card) {
      card.setAttribute('data-estado', estado);
      var h3 = card.querySelector('h3');
      if (h3) {
        h3.classList.toggle('line-through', esCompletada);
        h3.classList.toggle('text-on-surface-variant', esCompletada);
      }
      var target = estado === 'completada' ? 'done'
        : (isUrgent(tarea) ? 'urgente' : (tarea.prioridad === 'media' ? 'media' : 'baja'));
      var col = card.closest('.kanban-col');
      if (col && col.getAttribute('data-kcol') !== target) {
        var dest = document.querySelector('#view-kanban .kanban-col[data-kcol="' + target + '"] .kanban-cards');
        if (dest) dest.appendChild(card);
      }
      updateKanbanCounts();
    }

    applyListFilter();
  }

  document.addEventListener('click', function (e) {
    var editBtn = e.target.closest('[data-edit-tarea]');
    if (editBtn) {
      var id = Number(editBtn.getAttribute('data-edit-tarea'));
      var t = taskById(id);
      if (t && t.estado === 'pendiente') { fillForm(t); openModal('modal-tarea'); }
      else if (t) { fillForm(t); openModal('modal-tarea'); }
      return;
    }
    var delBtn = e.target.closest('[data-delete-tarea]');
    if (delBtn) {
      var tid = Number(delBtn.getAttribute('data-delete-tarea'));
      if (confirm('¿Eliminar esta tarea?')) {
        window.fetcher('/api/tareas/' + tid, { method: 'DELETE' }).then(function (res) {
          if (res.ok) { window.location.reload(); }
          else { window.showToast('No se pudo eliminar.', 'error'); }
        });
      }
      return;
    }
    var togBtn = e.target.closest('[data-toggle-tarea]');
    if (togBtn) {
      var gid = Number(togBtn.getAttribute('data-toggle-tarea'));
      if (togglingIds[gid]) return;
      var gt = taskById(gid);
      if (!gt) return;
      var anterior = gt.estado;
      var nuevo = anterior === 'completada' ? 'pendiente' : 'completada';
      togglingIds[gid] = true;
      applyTaskState(gt, nuevo);
      window.fetcher('/api/tareas/' + gid, { method: 'PUT', body: { estado: nuevo } }).then(function (res) {
        togglingIds[gid] = false;
        if (!res.ok) {
          applyTaskState(gt, anterior);
          window.showToast(res.message || 'No se pudo actualizar.', 'error');
        }
      }).catch(function () {
        togglingIds[gid] = false;
        applyTaskState(gt, anterior);
        window.showToast('Error de conexión.', 'error');
      });
    }
  });
})();