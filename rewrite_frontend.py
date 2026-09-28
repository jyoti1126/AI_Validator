import os
import re

base_dir = r'c:\Users\ACER\OneDrive\Desktop\Ai_Validator'

# Rewrite shared.js
shared_js_content = """const fallbackStartup = {
  idea: 'A platform connecting local home chefs with nearby customers.',
  targetCustomers: 'General Consumers',
  businessModel: 'Commission',
  budget: '10,000',
  timeAvailable: 'Full-time',
  skills: ['Marketing', 'Coding', 'Design'],
  validationStatus: 'Validated'
};

function getActiveStartupId() {
  let id = localStorage.getItem('selectedStartupId');
  if (id && id.startsWith('startup-')) id = id.replace('startup-', '');
  return id;
}

async function getStartupDataAsync() {
  const id = getActiveStartupId();
  if (!id) return fallbackStartup;
  try {
    const res = await fetch(`/api/startups/${id}`);
    const data = await res.json();
    if (data.success && data.startup) {
      return { ...fallbackStartup, ...data.startup };
    }
    return fallbackStartup;
  } catch (err) {
    console.error(err);
    return fallbackStartup;
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
"""

with open(os.path.join(base_dir, 'shared.js'), 'w', encoding='utf-8') as f:
    f.write(shared_js_content)

# Regex to strip out duplicate functions from report files
funcs_to_remove = [
    r"const fallbackStartup = \{[\s\S]*?\};",
    r"function getStartupData\(\) \{[\s\S]*?\} catch \{[\s\S]*?return fallbackStartup;[\s\S]*?\}[\s\S]*?\}",
    r"function getSavedAnalysis\(\) \{[\s\S]*?return null;[\s\S]*?\}[\s\S]*?\}",
    r"function saveAnalysis\(data\) \{[\s\S]*?\}",
    r"function setupMobileNavigation\(\) \{[\s\S]*?\}\s*\n"
]

files_to_clean = ['overview.js', 'market.js', 'competition.js', 'risks.js', 'business.js', 'mvp.js', 'experiments.js']

for fname in files_to_clean:
    filepath = os.path.join(base_dir, fname)
    if not os.path.exists(filepath): continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    for pattern in funcs_to_remove:
        content = re.sub(pattern, "", content)
        
    # Replace synchronous calls with async
    content = content.replace("const startupData = getStartupData();", "const startupData = await getStartupDataAsync();")
    content = content.replace("let analysis = getSavedAnalysis();", "let analysis = await getSavedAnalysisAsync();")
    content = content.replace("const analysis = getSavedAnalysis();", "const analysis = await getSavedAnalysisAsync();")
    content = content.replace("saveAnalysis(analysis);", "") # Not needed anymore, API handles it
    
    # In experiments.js, there is progress logic that needs to be updated.
    # We will just write a specific replace for experiments.js later if needed, but let's just do the general ones first.
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip() + "\n")
