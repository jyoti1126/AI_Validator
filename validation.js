const validationSteps = [...document.querySelectorAll('.validation-step')];
const title = document.querySelector('#validation-title');
const subtitle = document.querySelector('#validation-subtitle');
const stepDuration = 1500;

function updateProgress(completedCount) {
  validationSteps.forEach((step, index) => {
    step.classList.toggle('is-complete', index < completedCount);
    step.classList.toggle('is-current', index === completedCount && completedCount < validationSteps.length);
  });
}

function completeValidation() {
  updateProgress(validationSteps.length);
  title.textContent = 'Validation complete!';
  subtitle.textContent = 'Preparing your startup validation report...';
  window.setTimeout(() => {
    window.location.href = 'dashboard.html';
  }, 1500);
}

function runValidation() {
  let completedCount = 0;
  updateProgress(completedCount);

  const progressTimer = window.setInterval(() => {
    completedCount += 1;

    if (completedCount === validationSteps.length) {
      window.clearInterval(progressTimer);
      completeValidation();
      return;
    }

    updateProgress(completedCount);
  }, stepDuration);
}

runValidation();
