const businessForm = document.querySelector('#business-form');
const skillTags = document.querySelector('#skill-tags');
const customSkillInput = document.querySelector('#custom-skill');
const addCustomSkillBtn = document.querySelector('#add-custom-skill');

const requiredFields = [
  { id: 'target-customers', message: 'Choose your target customers.' },
  { id: 'problem', message: 'Describe the problem you are solving.' },
  { id: 'business-model', message: 'Choose a business model.' },
  { id: 'budget', message: 'Enter your available budget.' },
  { id: 'time-available', message: 'Choose the time you have available.' }
];

function getSavedStartupData() {
  // Not needed, we just PUT data to the active startup ID
  return {};
}

function getSkills() {
  return [...skillTags.querySelectorAll('[data-skill]')].map((tag) => tag.dataset.skill);
}

function showFieldError(fieldId, message) {
  const field = document.querySelector(`#${fieldId}`);
  const group = field.closest('.field-group');
  const error = document.querySelector(`#${fieldId}-error`);
  group.classList.add('has-error');
  error.textContent = message;
}

function clearFieldError(field) {
  const group = field.closest('.field-group');
  const error = document.querySelector(`#${field.id}-error`);
  group.classList.remove('has-error');
  error.textContent = '';
}

function addSkill(skill) {
  if (!skill || getSkills().includes(skill)) return;

  const tag = document.createElement('button');
  tag.className = 'skill-tag';
  tag.type = 'button';
  tag.dataset.skill = skill;
  tag.innerHTML = `${skill} <span aria-hidden="true">×</span>`;
  skillTags.append(tag);
  skillPicker.value = '';
  document.querySelector('.skills-group').classList.remove('has-error');
  document.querySelector('#skills-error').textContent = '';
}

function validateForm() {
  let isValid = true;

  requiredFields.forEach(({ id, message }) => {
    const field = document.querySelector(`#${id}`);
    if (!field.value.trim()) {
      showFieldError(id, message);
      isValid = false;
    } else {
      clearFieldError(field);
    }
  });

  const skillsError = document.querySelector('#skills-error');
  const skillsGroup = document.querySelector('.skills-group');
  if (!getSkills().length) {
    skillsGroup.classList.add('has-error');
    skillsError.textContent = 'Add at least one skill.';
    isValid = false;
  } else {
    skillsGroup.classList.remove('has-error');
    skillsError.textContent = '';
  }

  return isValid;
}

function handleAddCustomSkill() {
  const skill = customSkillInput.value.trim();
  if (skill) {
    addSkill(skill);
    customSkillInput.value = '';
  }
}

addCustomSkillBtn.addEventListener('click', handleAddCustomSkill);

customSkillInput.addEventListener('keypress', (event) => {
  if (event.key === 'Enter') {
    event.preventDefault();
    handleAddCustomSkill();
  }
});

skillTags.addEventListener('click', (event) => {
  const tag = event.target.closest('[data-skill]');
  if (tag) tag.remove();
});

requiredFields.forEach(({ id }) => {
  const field = document.querySelector(`#${id}`);
  field.addEventListener('input', () => clearFieldError(field));
  field.addEventListener('change', () => clearFieldError(field));
});

businessForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (!validateForm()) return;

  const startupData = {
    targetCustomers: document.querySelector('#target-customers').value,
    problem: document.querySelector('#problem').value.trim(),
    businessModel: document.querySelector('#business-model').value,
    budget: document.querySelector('#budget').value.trim(),
    timeAvailable: document.querySelector('#time-available').value,
    skills: getSkills()
  };

  const submitButton = event.submitter || document.querySelector('.continue-button');
  const originalText = submitButton ? submitButton.textContent : 'Continue';
  if (submitButton) {
    submitButton.disabled = true;
    submitButton.textContent = 'Saving...';
  }

  try {
    let id = localStorage.getItem('selectedStartupId');
    if (id && id.startsWith('startup-')) id = id.replace('startup-', '');
    
    if (!id) {
      alert("No active startup found. Please submit your idea first.");
      window.location.href = "idea-input.html";
      return;
    }
    
    const response = await fetch(`/api/startups/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(startupData)
    });
    
    if (!response.ok) throw new Error("Failed to save");
    window.location.href = 'validation.html';
  } catch (error) {
    console.error(error);
    alert('Unable to save business details. Please try again.');
    if (submitButton) {
      submitButton.disabled = false;
      submitButton.textContent = originalText;
    }
  }
});
