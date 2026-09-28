function renderRisks(startupData, analysis) {
  const generatedName = analysis?.startup_name;
  const startupName = generatedName || startupData.name || "Your Startup";
  document.querySelector('#startup-name').textContent = startupName;
  
  const grid = document.querySelector('#risk-grid');
  
  if (analysis?.risks && Array.isArray(analysis.risks) && analysis.risks.length > 0) {
    grid.innerHTML = '';
    analysis.risks.forEach((risk, i) => {
      const article = document.createElement('article');
      article.className = 'risk-card';
      article.innerHTML = `
        <div class="risk-header">
          <span class="risk-icon" aria-hidden="true">!</span>
          <h3>${risk.title || 'N/A'}</h3>
        </div>
        <p class="risk-desc"><strong>Why it matters:</strong> ${risk.description || 'N/A'}</p>
        <p class="risk-mitigation"><strong>Solution:</strong> ${risk.mitigation || 'N/A'}</p>
      `;
      grid.appendChild(article);
    });
  } else {
    grid.innerHTML = `<p>No risks data available. Please generate the dashboard analysis first.</p>`;
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
    renderRisks(startupData, analysis);
    return;
  }
  
  if (analysis) {
    console.log('[Report] Startup data found');
    renderRisks(startupData, analysis);
  } else {
    document.querySelector('#risk-grid').innerHTML = `<p>No risks data available. Please generate the dashboard analysis first.</p>`;
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
