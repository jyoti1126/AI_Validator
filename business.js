function renderBusiness(startupData, analysis) {
  const generatedName = analysis?.startup_name;
  const startupName = generatedName || startupData.name || "Your Startup";
  document.querySelector('#startup-name').textContent = startupName;
  
  if (analysis?.business) {
    document.querySelector('#target-customers-copy').textContent = analysis.business.business_model || "N/A";
    document.querySelector('#value-prop-copy').textContent = (analysis.business.revenue_streams || []).join(", ") || "N/A";
    document.querySelector('#revenue-model-copy').textContent = (analysis.business.resources_needed || []).join(", ") || "N/A";
    document.querySelector('#acquisition-copy').textContent = analysis.business.customer_acquisition || "N/A";
    document.querySelector('#key-metric-copy').textContent = (analysis.business.business_assumptions || []).join(", ") || "N/A";
  } else {
    const msg = "No business data available. Please generate the dashboard analysis first.";
    document.querySelector('#target-customers-copy').textContent = msg;
    document.querySelector('#value-prop-copy').textContent = msg;
    document.querySelector('#revenue-model-copy').textContent = msg;
    document.querySelector('#acquisition-copy').textContent = msg;
    document.querySelector('#key-metric-copy').textContent = msg;
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
    renderBusiness(startupData, analysis);
    return;
  }
  
  if (analysis) {
    console.log('[Report] Startup data found');
    renderBusiness(startupData, analysis);
  } else {
    const msg = "No business data available. Please generate the dashboard analysis first.";
    document.querySelector('#target-customers-copy').textContent = msg;
    document.querySelector('#value-prop-copy').textContent = msg;
    document.querySelector('#revenue-model-copy').textContent = msg;
    document.querySelector('#acquisition-copy').textContent = msg;
    document.querySelector('#key-metric-copy').textContent = msg;
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
