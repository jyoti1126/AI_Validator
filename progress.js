const defaultProgressData = {
  overallProgress: 35,
  points: 350,
  maxPoints: 1000,
  level: 1,
  tasks: [
    { id: 'business-details', title: 'Market & Business Details', completed: 5, total: 5 },
    { id: 'market-analysis', title: 'Market Analysis', completed: 2, total: 5 },
    { id: 'customer-survey', title: 'Customer Survey', completed: 0, total: 3 }
  ]
};

function parseStorage(key, fallback) {
  try {
    return JSON.parse(localStorage.getItem(key)) || fallback;
  } catch {
    return fallback;
  }
}

function calculateTaskProgress(tasks) {
  const totals = tasks.reduce((summary, task) => ({
    completed: summary.completed + task.completed,
    total: summary.total + task.total
  }), { completed: 0, total: 0 });
  return totals.total ? Math.round((totals.completed / totals.total) * 100) : 0;
}

function loadProgressData() {
  const savedData = parseStorage('progressData', {});
  const progressData = {
    ...defaultProgressData,
    ...savedData,
    tasks: Array.isArray(savedData.tasks) ? savedData.tasks : defaultProgressData.tasks
  };
  if (typeof savedData.overallProgress !== 'number') progressData.overallProgress = calculateTaskProgress(progressData.tasks);
  return progressData;
}

function renderProgressCircle(overallProgress) {
  const circle = document.querySelector('#progress-circle');
  circle.style.setProperty('--progress', `${overallProgress}%`);
  circle.setAttribute('aria-label', `Overall progress ${overallProgress} percent`);
  document.querySelector('#overall-value').textContent = `${overallProgress}%`;
}

function renderPoints(progressData) {
  const points = Math.max(0, Math.min(progressData.points, progressData.maxPoints));
  document.querySelector('#points-value').textContent = points.toLocaleString();
  const pointsBar = document.querySelector('#points-bar');
  pointsBar.value = points;
  pointsBar.max = progressData.maxPoints;
  pointsBar.setAttribute('aria-label', `${points} of ${progressData.maxPoints} points`);
  document.querySelector('#level-value').textContent = progressData.level;
}

function renderTasks(tasks) {
  document.querySelector('#task-list').innerHTML = tasks.map((task) => {
    const isComplete = task.completed >= task.total;
    const isPartial = task.completed > 0 && !isComplete;
    return `
      <li class="task-item${isComplete ? ' is-complete' : ''}${isPartial ? ' is-partial' : ''}">
        <span class="task-status" aria-hidden="true">${isComplete ? '✓' : ''}</span>
        <span class="task-title">${task.title}</span>
        <span class="task-count">${task.completed}/${task.total}</span>
      </li>
    `;
  }).join('');
}

const progressData = loadProgressData();
renderProgressCircle(progressData.overallProgress);
renderPoints(progressData);
renderTasks(progressData.tasks);
