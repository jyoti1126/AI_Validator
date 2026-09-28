function renderMarket(startupData, analysis) {
  const generatedName = analysis?.startup_name;
  const startupName = generatedName || startupData.name || "Your Startup";
  document.querySelector('#startup-name').textContent = startupName;
  
  if (analysis?.market) {
    document.querySelector('#market-overview-copy').textContent = analysis.market.market_overview || "N/A";
    document.querySelector('#target-market-copy').textContent = analysis.market.target_market || "N/A";
    document.querySelector('#customer-demand-copy').textContent = analysis.market.customer_demand || "N/A";
    document.querySelector('#market-opportunity-copy').textContent = analysis.market.market_opportunity || "N/A";
  } else {
    const msg = "No market data available. Please generate the dashboard analysis first.";
    document.querySelector('#market-overview-copy').textContent = msg;
    document.querySelector('#target-market-copy').textContent = msg;
    document.querySelector('#customer-demand-copy').textContent = msg;
    document.querySelector('#market-opportunity-copy').textContent = msg;
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
    renderMarket(startupData, analysis);
    return;
  }
  
  if (analysis) {
    console.log('[Report] Startup data found');
    renderMarket(startupData, analysis);
  } else {
    const msg = "No market data available. Please generate the dashboard analysis first.";
    document.querySelector('#market-overview-copy').textContent = msg;
    document.querySelector('#target-market-copy').textContent = msg;
    document.querySelector('#customer-demand-copy').textContent = msg;
    document.querySelector('#market-opportunity-copy').textContent = msg;
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
