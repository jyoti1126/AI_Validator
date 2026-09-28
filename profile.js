const defaultProfile = {
  name: 'Jyoti Patil',
  email: 'jyoti@example.com',
  phone: '+91 XXXXX XXXXX',
  bio: 'Student and aspiring entrepreneur interested in building and validating startup ideas.',
  role: 'Startup Validator',
  preferences: {
    emailNotifications: true,
    productUpdates: true,
    showProfile: false
  }
};

function parseStorage(key, fallback) {
  try {
    return JSON.parse(localStorage.getItem(key)) || fallback;
  } catch {
    return fallback;
  }
}

function loadProfile() {
  const savedProfile = parseStorage('userProfile', {});
  return { ...defaultProfile, ...savedProfile, preferences: { ...defaultProfile.preferences, ...(savedProfile.preferences || {}) } };
}

function getInitials(name) {
  return name.split(' ').map((part) => part[0]).join('').slice(0, 2).toUpperCase();
}

function renderProfile(profile) {
  document.querySelector('#profile-avatar').textContent = getInitials(profile.name);
  document.querySelector('#profile-role').textContent = profile.role;
  document.querySelector('#profile-email').textContent = profile.email;
  document.querySelector('#full-name').value = profile.name;
  document.querySelector('#email-address').value = profile.email;
  document.querySelector('#phone-number').value = profile.phone;
  document.querySelector('#bio').value = profile.bio;
  document.querySelectorAll('[data-preference]').forEach((input) => {
    input.checked = Boolean(profile.preferences[input.dataset.preference]);
  });
}

function getAccountStats() {
  const startups = parseStorage('startups', []);
  const progress = parseStorage('progressData', {});
  const experimentProgress = parseStorage('experimentProgress', {});
  const experimentsCompleted = Object.values(experimentProgress).filter(Boolean).length || 8;
  return {
    startups: startups.length || 4,
    experiments: experimentsCompleted,
    progress: typeof progress.overallProgress === 'number' ? progress.overallProgress : 35
  };
}

function renderAccountStats() {
  const stats = getAccountStats();
  document.querySelector('#startup-count').textContent = stats.startups;
  document.querySelector('#experiment-count').textContent = stats.experiments;
  document.querySelector('#overall-progress').textContent = `${stats.progress}%`;
}

function setEditing(isEditing) {
  document.querySelectorAll('.profile-form input, .profile-form textarea').forEach((field) => {
    field.disabled = !isEditing;
  });
  document.querySelector('#edit-button').textContent = isEditing ? 'Save Changes' : 'Edit Profile';
  document.querySelector('#edit-button').dataset.editing = String(isEditing);
}

function saveProfile() {
  const profile = {
    ...loadProfile(),
    name: document.querySelector('#full-name').value.trim(),
    email: document.querySelector('#email-address').value.trim(),
    phone: document.querySelector('#phone-number').value.trim(),
    bio: document.querySelector('#bio').value.trim()
  };
  localStorage.setItem('userProfile', JSON.stringify(profile));
  renderProfile(profile);
  setEditing(false);
}

function setupInteractions() {
  document.querySelector('#edit-button').addEventListener('click', (event) => {
    const isEditing = event.currentTarget.dataset.editing === 'true';
    if (isEditing) saveProfile();
    else setEditing(true);
  });
  document.querySelectorAll('[data-preference]').forEach((input) => {
    input.addEventListener('change', () => {
      const profile = loadProfile();
      profile.preferences[input.dataset.preference] = input.checked;
      localStorage.setItem('userProfile', JSON.stringify(profile));
    });
  });
  document.querySelector('.menu-button')?.addEventListener('click', () => {
    const sidebar = document.querySelector('.sidebar');
    const isOpen = sidebar.classList.toggle('is-open');
    document.querySelector('.menu-button').setAttribute('aria-expanded', String(isOpen));
  });
}

const profile = loadProfile();
renderProfile(profile);
renderAccountStats();
setupInteractions();
