const fallbackStartup = {
  name: 'My Startup',
  description: 'A startup idea being validated.',
  category: '',
  budget: '—',
  time: '—'
};

function parseStorage(key, fallback) {
  try {
    return JSON.parse(localStorage.getItem(key)) || fallback;
  } catch {
    return fallback;
  }
}

function loadStartupData() {
  const selectedStartup = parseStorage('selectedStartup', null);
  if (selectedStartup) return { ...fallbackStartup, ...selectedStartup };

  const selectedId = localStorage.getItem('selectedStartupId');
  const startups = parseStorage('startups', []);
  const startupFromCollection = startups.find((startup) => startup.id === selectedId);
  if (startupFromCollection) {
    return {
      ...fallbackStartup,
      ...startupFromCollection,
      description: startupFromCollection.description || startupFromCollection.idea || fallbackStartup.description,
      budget: startupFromCollection.budget || fallbackStartup.budget,
      time: startupFromCollection.time || startupFromCollection.timeAvailable || fallbackStartup.time
    };
  }

  const savedStartup = parseStorage('startupData', {});
  return {
    ...fallbackStartup,
    ...savedStartup,
    description: savedStartup.description || savedStartup.idea || fallbackStartup.description,
    budget: savedStartup.budget || fallbackStartup.budget,
    time: savedStartup.time || savedStartup.timeAvailable || fallbackStartup.time
  };
}

function renderStartupData(startup) {
  document.querySelector('#startup-title').textContent = startup.name || fallbackStartup.name;
  document.querySelector('#startup-description').textContent = startup.description || fallbackStartup.description;
  const categoryEl = document.querySelector('#startup-category');
  if (categoryEl) {
    const cat = startup.category || '';
    if (cat) {
      categoryEl.textContent = cat;
      categoryEl.style.display = '';
    } else {
      categoryEl.style.display = 'none';
    }
  }
  document.querySelector('#startup-budget').textContent = startup.budget || fallbackStartup.budget;
  document.querySelector('#startup-time').textContent = startup.time || fallbackStartup.time;
}

function setupInteractions() {
  document.querySelector('#edit-button').addEventListener('click', () => {
    window.location.href = 'idea-input.html';
  });
}

renderStartupData(loadStartupData());
setupInteractions();
