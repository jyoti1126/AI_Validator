import os
import re

base_dir = r'c:\Users\ACER\OneDrive\Desktop\Ai_Validator'

# 1. Update dashboard.js
dashboard_path = os.path.join(base_dir, 'dashboard.js')
with open(dashboard_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add analysisInProgress flag and logic to generateAnalysis
gen_analysis_new = """let analysisInProgress = false;

async function generateAnalysis(startupData) {
  if (analysisInProgress) return;
  analysisInProgress = true;

  startupData.id = getActiveStartupId();
  const loadingOverlay = document.getElementById('loading-overlay');
  if (loadingOverlay) loadingOverlay.style.display = 'flex';
  
  const refreshBtn = document.getElementById('refresh-btn');
  const originalBtnText = refreshBtn ? refreshBtn.textContent : 'Refresh Analysis';
  if (refreshBtn) {
    refreshBtn.disabled = true;
    refreshBtn.textContent = 'Analyzing your startup...';
  }
  
  try {
    const response = await fetch('/api/generate-dashboard', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(startupData)
    });
    
    const data = await response.json();
    
    if (data.success && data.analysis) {
      updateDashboardUI(startupData, data.analysis);
    } else {
      if (response.status === 429) {
        alert("Analysis limit reached. Please wait and try again.");
      } else {
        alert(data.message || "We couldn't analyze your startup right now. Please try again.");
      }
    }
  } catch (error) {
    console.error(error);
    alert("We couldn't analyze your startup right now. Please try again.");
  } finally {
    if (loadingOverlay) loadingOverlay.style.display = 'none';
    if (refreshBtn) {
      refreshBtn.disabled = false;
      refreshBtn.textContent = originalBtnText;
    }
    analysisInProgress = false;
  }
}
"""
content = re.sub(r"async function generateAnalysis\(startupData\) \{[\s\S]*?\}\n\nasync function initDashboard", gen_analysis_new + "\nasync function initDashboard", content)

with open(dashboard_path, 'w', encoding='utf-8') as f:
    f.write(content.strip() + "\n")

# 2. Update report files
report_files = ['overview.js', 'market.js', 'competition.js', 'risks.js', 'business.js', 'mvp.js', 'experiments.js']
for fname in report_files:
    filepath = os.path.join(base_dir, fname)
    if not os.path.exists(filepath): continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        rep_content = f.read()

    # The report files have loadReportAnalysis which does the fetch.
    # Add analysisInProgress there too.
    rep_new = """let analysisInProgress = false;

async function loadReportAnalysis() {
  const startupData = await getStartupDataAsync();
  if (!startupData) {
    const container = document.querySelector('.report-content') || document.querySelector('.experiments-container') || document.body;
    container.innerHTML = '<div style="text-align:center; padding: 4rem;"><h2>Startup not found</h2><p>Please return to <a href="startups.html">My Startups</a> and select a startup.</p></div>';
    return;
  }
  
  let analysis = await getSavedAnalysisAsync();
  
  if (analysis) {
    console.log('[Report] Startup data found');
"""
    if fname == 'experiments.js':
        rep_new += "    renderExperiments(startupData, analysis);\n    return;\n  }"
    else:
        rep_name = fname.replace('.js', '').capitalize()
        rep_new += f"    render{rep_name}(startupData, analysis);\n    return;\n  }}"
        
    rep_new += """
  
  if (analysisInProgress) return;
  analysisInProgress = true;
  
  console.log('[Report] Loading startup');
  const msgTarget = document.querySelector('#' + (document.querySelector('[id$="-copy"]') ? document.querySelector('[id$="-copy"]').id : 'step-list'));
  if (msgTarget) msgTarget.textContent = 'Loading startup report...';
  
  try {
    console.log('[Report] Loading analysis');
    const response = await fetch('/api/generate-dashboard', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({id: getActiveStartupId(), ...startupData})
    });
    
    const result = await response.json();
    
    if (!result.success) {
      if (response.status === 429) {
        throw new Error("Analysis limit reached. Please wait and try again.");
      }
      throw new Error(result.message || 'Unable to load startup analysis');
    }
    
    console.log('[Report] Analysis received');
    analysis = result.analysis;
"""
    if fname == 'experiments.js':
        rep_new += "    renderExperiments(startupData, analysis);\n"
    else:
        rep_new += f"    render{rep_name}(startupData, analysis);\n"
        
    rep_new += """    console.log('[Report] Report rendered successfully');
  } catch (error) {
    console.error(error);
    if (msgTarget) msgTarget.textContent = error.message || 'Unable to load the startup report. Please try again.';
  } finally {
    analysisInProgress = false;
  }
}"""
    rep_content = re.sub(r"async function loadReportAnalysis\(\) \{[\s\S]*?\}\n\nfunction setupNavigation", rep_new + "\n\nfunction setupNavigation", rep_content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(rep_content.strip() + "\n")

