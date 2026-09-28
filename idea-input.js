const ideaForm = document.querySelector('#idea-form');
const ideaField = document.querySelector('#startup-idea');
const errorMessage = document.querySelector('#idea-error');
const submitButton = document.querySelector('.continue-button');

function showValidationMessage(message) {
  if (!errorMessage) return;
  errorMessage.textContent = message;
  if (ideaField) {
    ideaField.setAttribute('aria-invalid', 'true');
    ideaField.focus();
  }
}

function clearValidationMessage() {
  if (!errorMessage) return;
  errorMessage.textContent = '';
  if (ideaField) {
    ideaField.removeAttribute('aria-invalid');
  }
}

function setSubmitState(isLoading) {
  if (!submitButton) return;

  submitButton.disabled = isLoading;
  submitButton.textContent = isLoading ? 'Saving...' : 'Continue';
  const arrow = submitButton.querySelector('span');

  if (arrow) {
    arrow.style.display = isLoading ? 'none' : 'inline';
  }
}

function deriveStartupName(idea) {
  if (!idea) return 'My Startup';
  // Trim to first sentence or 60 chars, then title-case key words
  const clean = idea.trim().replace(/[.!?].*$/s, '').trim();
  const words = clean.split(/\s+/).filter(Boolean);
  const stopWords = new Set(['a','an','the','and','or','but','for','in','on','at','to','of','with','where','that','is','are','can','will','how','which','this','my','your','our','their','its','by','as','from','into','about','through','over','between','after','when','so','than','be','has','have','had','it','we','they','i','you','he','she','do','did','does']);
  const keyWords = words.filter((w) => !stopWords.has(w.toLowerCase())).slice(0, 4);
  if (!keyWords.length) return words.slice(0, 3).map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  return keyWords.map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join(' ');
}

if (ideaField) {
  ideaField.addEventListener('input', clearValidationMessage);
}

if (ideaForm) {
  ideaForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const idea = ideaField ? ideaField.value.trim() : '';
    if (!idea) {
      showValidationMessage('Please describe your startup idea.');
      return;
    }

    setSubmitState(true);
    clearValidationMessage();

    try {
      const response = await fetch('/api/startups', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ idea, name: deriveStartupName(idea) })
      });

      let result;
      try {
        result = await response.json();
      } catch (jsonError) {
        console.error('Invalid JSON response from backend:', jsonError);
        throw new Error('Invalid response');
      }

      if (!response.ok || !result.success) {
        const message = result?.message || 'Unable to save your idea. Please try again.';
        showValidationMessage(message);
        return;
      }

      const startupPayload = result.startup || { idea };
      localStorage.setItem('startupData', JSON.stringify(startupPayload));
      if (result.startup && result.startup.id) {
        localStorage.setItem('selectedStartupId', result.startup.id);
      }
      window.location.href = 'business-details.html';
    } catch (error) {
      console.error('Startup submission failed:', error);
      showValidationMessage('Unable to save your idea. Please try again.');
    } finally {
      setSubmitState(false);
    }
  });
}
