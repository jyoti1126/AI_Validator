import os
import re

filepath = r'c:\Users\ACER\OneDrive\Desktop\Ai_Validator\dashboard.js'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()
    
# Remove duplicate functions
funcs_to_remove = [
    r"const fallbackStartup = \{[\s\S]*?\};",
    r"function getStartupData\(\) \{[\s\S]*?\} catch \{[\s\S]*?return fallbackStartup;[\s\S]*?\}[\s\S]*?\}",
    r"function getSavedAnalysis\(\) \{[\s\S]*?return null;[\s\S]*?\}[\s\S]*?\}",
    r"function saveAnalysis\(data\) \{[\s\S]*?\}",
    r"function setupMobileNavigation\(\) \{[\s\S]*?\}\s*\n"
]

for pattern in funcs_to_remove:
    content = re.sub(pattern, "", content)
    
# Rewrite syncStartupCardData as we don't need localStorage sync anymore, the backend does it.
content = re.sub(r"function syncStartupCardData\(analysis\) \{[\s\S]*?\}\s*\n", "", content)

# Modify updateDashboardUI to use created_at date maybe? For now just omit date or keep analysisDate from localstorage as fallback.
content = content.replace("localStorage.getItem('analysisDate')", "analysis?.updated_at ? new Date(analysis.updated_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) : ''")

# Modify generateAnalysis
content = content.replace("syncStartupCardData(data.analysis);", "")
content = content.replace("saveAnalysis(data.analysis);", "")
content = content.replace("localStorage.setItem('analysisDate', dateStr);", "")
content = content.replace("async function generateAnalysis(startupData) {", "async function generateAnalysis(startupData) {\n  startupData.id = getActiveStartupId();")

# Modify initDashboard to be async
init_dash = """async function initDashboard() {
  const startupData = await getStartupDataAsync();
  const savedAnalysis = await getSavedAnalysisAsync();
  
  // If we already have analysis, render UI. Else, fetch it.
  if (savedAnalysis) {
    updateDashboardUI(startupData, savedAnalysis);
  } else {
    updateDashboardUI(startupData, null); // Base UI
    generateAnalysis(startupData);
  }
  
  const refreshBtn = document.getElementById('refresh-btn');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', () => {
      generateAnalysis(startupData);
    });
  }
}
"""

content = re.sub(r"function initDashboard\(\) \{[\s\S]*?\}", init_dash, content)
content = content.replace("setupMobileNavigation();\n  ", "")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content.strip() + "\n")
