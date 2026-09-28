import os
import re

filepath = r'c:\Users\ACER\OneDrive\Desktop\Ai_Validator\experiments.js'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace getProgressKey, loadProgress, saveProgress
funcs_to_remove = [
    r"let currentStartupName = '';\s*\nlet currentProgress = \{\};\s*\n\s*\n",
    r"function getProgressKey\(\) \{[\s\S]*?\}\s*\n\s*\n",
    r"function loadProgress\(\) \{[\s\S]*?\}\s*\n\s*\n",
    r"function saveProgress\(\) \{[\s\S]*?\}\s*\n\s*\n",
    r"function setupNavigation\(\) \{[\s\S]*?\}\s*\n\s*\n"
]

for pattern in funcs_to_remove:
    content = re.sub(pattern, "", content)

# Rewrite renderExperiments
render_exp = """async function renderExperiments(startupData, analysis) {
  const currentStartupName = analysis?.startup_name || startupData.startupName || "Your Startup";
  document.querySelector('#startup-name').textContent = currentStartupName;
  
  const descElem = document.querySelector('#experiments-desc');
  descElem.textContent = `For your ${currentStartupName}, complete these experiments to understand whether customers will actually use the platform.`;

  const stepList = document.querySelector('#step-list');
  
  const id = getActiveStartupId();
  let tasks = [];
  try {
    const res = await fetch(`/api/startups/${id}/tasks`);
    const data = await res.json();
    if (data.success) tasks = data.tasks;
  } catch (err) {
    console.error(err);
  }
  
  if (tasks && tasks.length > 0) {
    stepList.innerHTML = '';
    
    tasks.forEach(step => {
      const isCompleted = step.completed;
      const li = document.createElement('li');
      li.className = `step-item ${isCompleted ? 'is-completed' : ''}`;
      
      li.innerHTML = `
        <input type="checkbox" class="step-checkbox" id="${step.id}" ${isCompleted ? 'checked' : ''} aria-label="Mark ${step.title} as completed">
        <div class="step-content">
          <h4 class="step-title"><label for="${step.id}" style="cursor: pointer; display: block;">${step.title}</label></h4>
          <p class="step-desc">${step.description}</p>
        </div>
      `;
      
      const checkbox = li.querySelector('.step-checkbox');
      checkbox.addEventListener('change', async (e) => {
        const checked = e.target.checked;
        
        try {
          const updateRes = await fetch(`/api/tasks/${step.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ completed: checked })
          });
          const result = await updateRes.json();
          if (result.success) {
             if (checked) {
               li.classList.add('is-completed');
             } else {
               li.classList.remove('is-completed');
             }
             // Get updated tasks to recalculate
             const res = await fetch(`/api/startups/${id}/tasks`);
             const data = await res.json();
             updateProgressUI(data.tasks || []);
          }
        } catch (err) {
          console.error(err);
          e.target.checked = !checked; // revert
        }
      });
      
      li.addEventListener('click', (e) => {
        if (e.target !== checkbox && e.target.tagName !== 'LABEL') {
           checkbox.click();
        }
      });
      
      stepList.appendChild(li);
    });
    
    updateProgressUI(tasks);
  } else {
    stepList.innerHTML = '<li><p>No validation steps available. Please generate the dashboard analysis first.</p></li>';
    document.querySelector('.progress-card').style.display = 'none';
  }
}
"""

content = re.sub(r"function renderExperiments\(startupData, analysis\) \{[\s\S]*?\}\s*\n", render_exp, content)

# Rewrite updateProgressUI
update_progress = """function updateProgressUI(tasks) {
  const totalSteps = tasks.length;
  const completedSteps = tasks.filter(t => t.completed).length;
  const percentage = totalSteps > 0 ? Math.round((completedSteps / totalSteps) * 100) : 0;
  
  document.querySelector('#progress-count').textContent = `${completedSteps} of ${totalSteps} steps completed`;
  document.querySelector('#progress-percentage').textContent = `${percentage}%`;
  document.querySelector('#progress-bar').style.width = `${percentage}%`;
  
  const completionMessage = document.querySelector('#completion-message');
  if (totalSteps > 0 && completedSteps === totalSteps) {
    completionMessage.classList.add('is-visible');
  } else {
    completionMessage.classList.remove('is-visible');
  }
}
"""

content = re.sub(r"function updateProgressUI\(totalSteps\) \{[\s\S]*?\}\s*\n", update_progress, content)
content = content.replace("setupNavigation();", "")
content = content.replace("body: JSON.stringify(startupData)", "body: JSON.stringify({id: getActiveStartupId(), ...startupData})")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content.strip() + "\n")
