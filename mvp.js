function renderMVP(startupData, analysis) {
  const generatedName = analysis?.startup_name;
  const startupName = generatedName || startupData.name || "Your Startup";
  document.querySelector('#startup-name').textContent = startupName;
  
  const featureList = document.querySelector('#feature-list');
  
  if (analysis?.mvp) {
    let html = `<div style="margin-bottom: 20px;"><strong>MVP Description:</strong> ${analysis.mvp.description || 'N/A'}</div>`;
    
    if (analysis.mvp.features && analysis.mvp.features.length > 0) {
      html += `<h3>Essential Features</h3><ul class="feature-items">`;
      analysis.mvp.features.forEach(f => {
        html += `<li><span aria-hidden="true">✓</span> ${f}</li>`;
      });
      html += `</ul>`;
    }
    
    if (analysis.mvp.avoid_initially && analysis.mvp.avoid_initially.length > 0) {
      html += `<h3 style="margin-top: 20px;">Do NOT Build Yet</h3><ul class="feature-items out-of-scope">`;
      analysis.mvp.avoid_initially.forEach(f => {
        html += `<li><span aria-hidden="true">✗</span> ${f}</li>`;
      });
      html += `</ul>`;
    }

    html += `<div style="margin-top: 20px;"><strong>First Users:</strong> ${analysis.mvp.first_users || 'N/A'}</div>`;
    html += `<div style="margin-top: 10px;"><strong>Launch Approach:</strong> ${analysis.mvp.launch_approach || 'N/A'}</div>`;
    
    featureList.innerHTML = html;
  } else {
    featureList.innerHTML = `<p>No MVP data available. Please generate the dashboard analysis first.</p>`;
  }
}

let analysisInProgress = false;

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
    renderMvp(startupData, analysis);
    return;
  }
  
  if (analysis) {
    console.log('[Report] Startup data found');
    renderMvp(startupData, analysis);
  } else {
    document.querySelector('#feature-list').innerHTML = `<p>No MVP data available. Please generate the dashboard analysis first.</p>`;
  }
}

function setupNavigation() {
  const menuButton = document.querySelector('.menu-button');
  const sidebar = document.querySelector('.sidebar');

  if (!menuButton) return;
  menuButton.addEventListener('click', () => {
    const isOpen = sidebar.classList.toggle('is-open');
    menuButton.setAttribute('aria-expanded', String(isOpen));
  });
}

loadReportAnalysis();
setupNavigation();
