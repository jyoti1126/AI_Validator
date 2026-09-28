function getSavedStartupData() {
  try {
    return JSON.parse(localStorage.getItem('startupData')) || {};
  } catch {
    return {};
  }
}

function createStartupCard(startup) {
  return `
    <article class="startup-card" data-startup-id="${startup.id}">
      <div class="card-header">
        <span class="startup-icon" aria-hidden="true">✦</span>
        <h2>${startup.name}</h2>
      </div>
      <div class="card-menu-wrap">
        <button class="menu-trigger" type="button" data-action="menu" aria-label="Manage ${startup.name}">⋮</button>
        <div class="card-dropdown">
          <button type="button" data-action="show-delete-modal" data-startup-id="${startup.id}">Delete</button>
        </div>
      </div>
      <div class="progress-section">
        <div class="progress-label"><span>Validation:</span><strong>${startup.validation}%</strong></div>
        <progress class="progress-track validation-progress" value="${startup.validation}" max="100" aria-label="Validation ${startup.validation}%">${startup.validation}%</progress>
      </div>
      <div class="progress-section">
        <div class="progress-label"><span>Progress:</span><strong>${startup.progress}%</strong></div>
        <progress class="progress-track overall-progress" value="${startup.progress}" max="100" aria-label="Progress ${startup.progress}%">${startup.progress}%</progress>
      </div>
      <div class="card-footer">
        <span class="category-badge">${startup.category}</span>
        <button class="open-button" type="button" data-action="open" data-startup-id="${startup.id}">Open <span aria-hidden="true">→</span></button>
      </div>
    </article>
  `;
}

function renderStartups(startups) {
  const grid = document.querySelector('#startup-grid');
  const emptyState = document.querySelector('#empty-state');
  grid.innerHTML = startups.map(createStartupCard).join('');
  grid.style.display = startups.length ? 'grid' : 'none';
  emptyState.classList.toggle('is-visible', startups.length === 0);
}

function openStartup(id) {
  localStorage.setItem('selectedStartupId', id);
  window.location.href = 'dashboard.html';
}

let startupToDelete = null;

function showDeleteModal(id) {
  startupToDelete = id;
  document.getElementById('delete-modal').classList.add('is-visible');
}

function hideDeleteModal() {
  startupToDelete = null;
  document.getElementById('delete-modal').classList.remove('is-visible');
}

document.getElementById('cancel-delete').addEventListener('click', hideDeleteModal);
document.getElementById('confirm-delete').addEventListener('click', async () => {
  if (startupToDelete) {
    try {
      await fetch(`/api/startups/${startupToDelete}`, { method: 'DELETE' });
      hideDeleteModal();
      initStartups();
    } catch (err) {
      console.error(err);
    }
  }
});
function setupCardActions(startups) {
  document.addEventListener('click', (event) => {
    // Hide dropdowns when clicking outside
    if (!event.target.closest('.card-menu-wrap')) {
      document.querySelectorAll('.card-dropdown.is-visible').forEach(d => d.classList.remove('is-visible'));
    }
  });

  document.querySelector('#startup-grid').addEventListener('click', (event) => {
    const actionTarget = event.target.closest('[data-action]');
    if (!actionTarget) return;
    const id = actionTarget.dataset.startupId || actionTarget.closest('.startup-card').dataset.startupId;

    if (actionTarget.dataset.action === 'open') openStartup(id);
    if (actionTarget.dataset.action === 'menu') {
      const dropdown = actionTarget.nextElementSibling;
      const wasVisible = dropdown.classList.contains('is-visible');
      document.querySelectorAll('.card-dropdown.is-visible').forEach(d => d.classList.remove('is-visible'));
      if (!wasVisible) dropdown.classList.add('is-visible');
    }
    if (actionTarget.dataset.action === 'show-delete-modal') {
      actionTarget.closest('.card-dropdown').classList.remove('is-visible');
      showDeleteModal(id);
    }
  });
}

async function initStartups() {
  try {
    const res = await fetch('/api/startups');
    const data = await res.json();
    if (data.success && data.startups) {
      renderStartups(data.startups);
      setupCardActions();
    }
  } catch (err) {
    console.error(err);
    renderStartups([]);
  }
}
initStartups();
