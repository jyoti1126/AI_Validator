function renderCompetition(startupData, analysis) {
  const generatedName = analysis?.startup_name;
  const startupName = generatedName || startupData.name || "Your Startup";
  document.querySelector('#startup-name').textContent = startupName;
  
  const tbody = document.querySelector('#competitor-table-body');
  
  if (analysis?.competition && Array.isArray(analysis.competition) && analysis.competition.length > 0) {
    tbody.innerHTML = '';
    analysis.competition.forEach(comp => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><strong>${comp.name || 'N/A'}</strong></td>
        <td>${comp.similarity || 'N/A'}</td>
        <td>${comp.description || 'N/A'}</td>
        <td>${comp.differentiation_opportunity || 'N/A'}</td>
      `;
      tbody.appendChild(tr);
    });
  } else {
    tbody.innerHTML = `<tr><td colspan="4">No competition data available. Please generate the dashboard analysis first.</td></tr>`;
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
    renderCompetition(startupData, analysis);
    return;
  }
  
  if (analysis) {
    console.log('[Report] Startup data found');
    renderCompetition(startupData, analysis);
  } else {
    document.querySelector('#competitor-table-body').innerHTML = `<tr><td colspan="4">No competition data available. Please generate the dashboard analysis first.</td></tr>`;
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
