function updateDashboardUI(startupData, analysis) {
  // Update header descriptions
  const description = startupData.idea?.trim() || "";
  // Derive category dynamically from Gemini analysis or stored startup data
  const category = analysis?.industry || startupData.category || '';
  document.querySelector('#startup-description').textContent = description;
  if (category) {
    document.querySelector('#startup-category').textContent = category;
    document.querySelector('#startup-category').style.display = '';
  } else {
    document.querySelector('#startup-category').style.display = 'none';
  }
  
  // Use generated short name if available, otherwise user's provided name
  const generatedName = analysis?.startup_name;
  const startupName = generatedName || startupData.name || "Your Startup";
  document.querySelector('#startup-title').textContent = startupName;
  
  const dateStr = analysis?.updated_at ? new Date(analysis.updated_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) : '';
  if (dateStr) {
    document.querySelector('#analysis-date').textContent = `Generated: ${dateStr}`;
  } else {
    document.querySelector('#analysis-date').textContent = "";
  }
  
  // Score and Validation Overview
  const scoreElem = document.querySelector('.score-ring strong');
  const evidenceElem = document.querySelector('.evidence-badge');
  const overviewNoteElem = document.querySelector('.overview-note');
  
  if (analysis?.validation_overview) {
    if (scoreElem) scoreElem.textContent = `${analysis.validation_overview.score || 0}%`;
    if (evidenceElem) evidenceElem.innerHTML = `<span aria-hidden="true">✦</span> ${analysis.validation_overview.evidence_level || 'Unknown Evidence'}`;
    if (overviewNoteElem) overviewNoteElem.textContent = analysis.validation_overview.summary || 'Not enough information available.';
  } else if (analysis) {
    if (overviewNoteElem) overviewNoteElem.textContent = 'Not enough information available.';
  }

  // Quick Insights
  const insightsList = document.querySelector('.insights-list');
  if (insightsList && analysis) {
    if (analysis.quick_insights && analysis.quick_insights.length > 0) {
      insightsList.innerHTML = '';
      analysis.quick_insights.forEach(insight => {
        let iconClass = 'market';
        let iconChar = '●';
        let statusClass = 'status-good'; 
        
        const cat = (insight.category || '').toLowerCase();
        if (cat.includes('market')) { iconClass = 'market'; iconChar = '●'; }
        else if (cat.includes('compet')) { iconClass = 'competition'; iconChar = '◌'; statusClass = 'status-moderate'; }
        else if (cat.includes('reven') || cat.includes('business')) { iconClass = 'revenue'; iconChar = '⌂'; }
        else if (cat.includes('feasibility') || cat.includes('mvp')) { iconClass = 'feasibility'; iconChar = '●'; }
        else if (cat.includes('risk') || cat.includes('concern')) { iconClass = 'competition'; iconChar = '▲'; statusClass = 'status-moderate'; }
        
        const li = document.createElement('li');
        li.innerHTML = `<span class="insight-label"><span class="insight-icon ${iconClass}" aria-hidden="true">${iconChar}</span>${insight.category || 'Insight'}</span><strong class="${statusClass}">${insight.insight_text || 'Not enough information available.'}</strong>`;
        insightsList.appendChild(li);
      });
    } else {
        insightsList.innerHTML = '<li><span class="insight-label">No insights generated.</span><strong>Not enough information available.</strong></li>';
    }
  }
}



let analysisInProgress = false;

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

async function initDashboard() {
  const startupData = await getStartupDataAsync();
  if (!startupData) {
    document.querySelector('.dashboard-container').innerHTML = '<div style="text-align:center; padding: 4rem;"><h2>Startup not found</h2><p>Please return to <a href="startups.html">My Startups</a> and select a startup.</p></div>';
    return;
  }
  
  const savedAnalysis = await getSavedAnalysisAsync();

  
  // If we already have analysis, render UI. Else, generate it automatically.
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

initDashboard();
