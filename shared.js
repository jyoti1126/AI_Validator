

function getActiveStartupId() {
  let id = localStorage.getItem('selectedStartupId');
  if (id && id.startsWith('startup-')) id = id.replace('startup-', '');
  return id;
}

async function getStartupDataAsync() {
  const id = getActiveStartupId();
  if (!id) return null;
  try {
    const res = await fetch(`/api/startups/${id}`);
    const data = await res.json();
    if (data.success && data.startup) {
      return data.startup;
    }
    return null;
  } catch (err) {
    console.error("Error fetching startup data:", err);
    return null;
  }
}

async function getSavedAnalysisAsync() {
  const id = getActiveStartupId();
  if (!id) return null;
  try {
    const res = await fetch(`/api/startups/${id}/analysis`);
    if (res.status === 404) return null;
    const data = await res.json();
    if (data.success && data.analysis) {
      return data.analysis;
    }
    return null;
  } catch (err) {
    console.error(err);
    return null;
  }
}

function setupMobileNavigation() {
  const menuButton = document.querySelector('.menu-button');
  const sidebar = document.querySelector('.sidebar');
  if (!menuButton || !sidebar) return;
  if (menuButton.dataset.navAttached) return;
  menuButton.dataset.navAttached = 'true';
  menuButton.addEventListener('click', () => {
    const isOpen = sidebar.classList.toggle('is-open');
    menuButton.setAttribute('aria-expanded', String(isOpen));
  });
}
