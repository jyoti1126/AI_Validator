import os
import re

base_dir = r'c:\Users\ACER\OneDrive\Desktop\Ai_Validator'

# 1. Fix dashboard.js
dashboard_path = os.path.join(base_dir, 'dashboard.js')
with open(dashboard_path, 'r', encoding='utf-8') as f:
    dash = f.read()

# Fix syntax error at bottom of dashboard.js
dash = re.sub(r" else \{\s*updateDashboardUI\(startupData, null\); // Base UI\s*generateAnalysis\(startupData\);\s*\}\s*const refreshBtn = document\.getElementById\('refresh-btn'\);\s*if \(refreshBtn\) \{\s*refreshBtn\.addEventListener\('click', \(\) => \{\s*generateAnalysis\(startupData\);\s*\}\);\s*\}\s*\}\s*", "", dash)

# Add startupData check to initDashboard
init_dash = """async function initDashboard() {
  const startupData = await getStartupDataAsync();
  if (!startupData) {
    document.querySelector('.dashboard-container').innerHTML = '<div style="text-align:center; padding: 4rem;"><h2>Startup not found</h2><p>Please return to <a href="startups.html">My Startups</a> and select a startup.</p></div>';
    return;
  }
  
  const savedAnalysis = await getSavedAnalysisAsync();
"""
dash = dash.replace("async function initDashboard() {\n  const startupData = await getStartupDataAsync();\n  const savedAnalysis = await getSavedAnalysisAsync();", init_dash)

# Also fix syncStartupCardData leftover in dashboard.js
dash = re.sub(r"// Sync Gemini's generated name and validation score back to the My Startups card[\s\S]*?\}\s*\}", "", dash)


with open(dashboard_path, 'w', encoding='utf-8') as f:
    f.write(dash.strip() + "\n")

# 2. Fix report files
report_files = ['overview.js', 'market.js', 'competition.js', 'risks.js', 'business.js', 'mvp.js', 'experiments.js']

for fname in report_files:
    filepath = os.path.join(base_dir, fname)
    if not os.path.exists(filepath): continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    check = """async function loadReportAnalysis() {
  const startupData = await getStartupDataAsync();
  if (!startupData) {
    const container = document.querySelector('.report-content') || document.querySelector('.experiments-container') || document.body;
    container.innerHTML = '<div style="text-align:center; padding: 4rem;"><h2>Startup not found</h2><p>Please return to <a href="startups.html">My Startups</a> and select a startup.</p></div>';
    return;
  }
  
  let analysis = await getSavedAnalysisAsync();"""
    
    content = content.replace("async function loadReportAnalysis() {\n  const startupData = await getStartupDataAsync();\n  let analysis = await getSavedAnalysisAsync();", check)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip() + "\n")
