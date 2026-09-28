import os
import re

filepath = r'c:\Users\ACER\OneDrive\Desktop\Ai_Validator\startups.js'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace demoStartups, loadStartups, getSavedStartupData, saveStartups
funcs_to_remove = [
    r"const demoStartups = \[[\s\S]*?\];\s*\n",
    r"function loadStartups\(\) \{[\s\S]*?return startups;\s*\n\}\s*\n",
    r"function getSavedStartupData\(\) \{[\s\S]*?\} catch \{[\s\S]*?return \{\};\s*\n\}\s*\n\}\s*\n",
    r"function saveStartups\(startups\) \{[\s\S]*?\}\s*\n",
    r"function setupMobileNavigation\(\) \{[\s\S]*?\}\s*\n",
    r"// One-time cleanup[\s\S]*?function cleanupHardcodedCategories\(\) \{[\s\S]*?\}\s*\n\s*\ncleanupHardcodedCategories\(\);\s*\n"
]

for pattern in funcs_to_remove:
    content = re.sub(pattern, "", content)

# Rewrite openStartup
# It should just set selectedStartupId to the id and redirect to dashboard.html
open_startup_new = """function openStartup(id) {
  localStorage.setItem('selectedStartupId', id);
  window.location.href = 'dashboard.html';
}
"""
content = re.sub(r"function openStartup\(id\) \{[\s\S]*?\}\s*\n", open_startup_new, content)

# Modify initialization at the bottom
init_new = """async function initStartups() {
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
"""

content = re.sub(r"const startups = loadStartups\(\);\s*\nrenderStartups\(startups\);\s*\nsetupCardActions\(startups\);\s*\nsetupMobileNavigation\(\);\s*\n", init_new, content)

# Update confirm delete logic
delete_logic = """document.getElementById('confirm-delete').addEventListener('click', async () => {
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
"""

content = re.sub(r"document\.getElementById\('confirm-delete'\)\.addEventListener\('click', \(\) => \{[\s\S]*?\}\);\s*\n", delete_logic, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content.strip() + "\n")
