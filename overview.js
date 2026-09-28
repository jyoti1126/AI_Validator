function renderOverview(startupData, analysis) {
  const generatedName = analysis?.startup_name;
  const startupName = generatedName || startupData.name || "Your Startup";
  document.querySelector('#startup-name').textContent = startupName;
  
  if (analysis?.overview) {
    let html = `<strong>Summary:</strong> ${analysis.overview.summary || 'N/A'}<br><br>`;
    html += `<strong>Problem:</strong> ${analysis.overview.problem || 'N/A'}<br><br>`;
    html += `<strong>Target Customers:</strong> ${analysis.overview.target_customers || 'N/A'}<br><br>`;
    html += `<strong>Value Proposition:</strong> ${analysis.overview.value_proposition || 'N/A'}`;
    document.querySelector('#overview-copy').innerHTML = html;
  } else {
    document.querySelector('#overview-copy').textContent = "No overview data available. Please generate the dashboard analysis first.";
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
    renderOverview(startupData, analysis);
    return;
  }
  
  if (analysis) {
    console.log('[Report] Startup data found');
    renderOverview(startupData, analysis);
  } else {
    document.querySelector('#overview-copy').textContent = "No overview data available. Please generate the dashboard analysis first.";
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
