/**
 * AI Profit Hub - Comparison Engine v1.0 (2026)
 * Generates premium interactive comparison views from JSON data.
 */

document.addEventListener("DOMContentLoaded", () => {
  const dataScript = document.getElementById("compare-data");
  if (!dataScript) return;

  try {
    const data = JSON.parse(dataScript.textContent);
    initializeCompare(data);
  } catch (error) {
    console.error("Failed to parse comparison data:", error);
  }
});

function initializeCompare(data) {
  // Render components if their target containers exist in the page
  renderStatusBar(data);
  renderTLDRCard(data);
  renderMatrix(data);
  renderDecision(data);
  renderProsCons(data);
  renderFAQ(data);

  // Initialize interactive accordion events for FAQ
  initFAQAccordions();

  // Re-initialize Lucide Icons if lucide library is loaded
  if (typeof lucide !== "undefined") {
    lucide.createIcons();
  }
}

// 1. Status and Update Alert Bar
function renderStatusBar(data) {
  const container = document.getElementById("cmp-status-container");
  if (!container) return;

  let alertHtml = "";
  if (data.versionAlert) {
    alertHtml = `
      <div class="cmp-status-item">
        <span class="cmp-alert-badge">
          <i data-lucide="alert-circle" style="width: 14px; height: 14px;"></i> Alert: ${data.versionAlert}
        </span>
      </div>
    `;
  }

  container.innerHTML = `
    <div class="cmp-status-bar">
      <div class="cmp-status-item">
        <i data-lucide="calendar" style="width: 15px; height: 15px; color: var(--primary-light);"></i>
        <span>Last Checked: <strong>${data.lastUpdated || "Recent"}</strong></span>
      </div>
      ${alertHtml}
    </div>
  `;
}

// 2. TL;DR Summary Card
function renderTLDRCard(data) {
  const container = document.getElementById("tldr-container");
  if (!container) return;

  const winner = data.overallWinner;
  const toolA = data.toolA;
  const toolB = data.toolB;
  const summary = data.summaryCards || {};

  // Map category winners
  const badgeItems = [
    { label: "🏆 Overall Winner", value: winner === toolA.name ? toolA.name : (winner === toolB.name ? toolB.name : winner) },
    { label: "💰 Best Price", value: summary.bestValue || "Tie" },
    { label: "🚀 Best Performance", value: summary.bestPerformance || winner },
    { label: "💻 Best for Coding", value: summary.bestForCoding || "Tie" },
    { label: "✍️ Best for Writing", value: summary.bestForWriting || "Tie" },
    { label: "🎓 Best for Beginners", value: summary.bestForBeginners || "Tie" }
  ];

  let badgesHtml = "";
  badgeItems.forEach(item => {
    let iconColor = "var(--text-primary)";
    let logo = "✨";
    if (item.value === toolA.name) {
      iconColor = toolA.color;
      logo = toolA.logo;
    } else if (item.value === toolB.name) {
      iconColor = toolB.color;
      logo = toolB.logo;
    }

    badgesHtml += `
      <div class="tldr-badge-item">
        <span class="tldr-badge-label">${item.label}</span>
        <span class="tldr-badge-value" style="color: ${iconColor};">
          <span>${logo}</span> ${item.value}
        </span>
      </div>
    `;
  });

  container.innerHTML = `
    <div class="tldr-summary-card">
      <div class="tldr-header">
        <h3><i data-lucide="zap" style="width: 20px; height: 20px; color: var(--accent);"></i> Fast Decision Summary (TL;DR)</h3>
      </div>
      <div class="tldr-layout">
        <div class="tldr-badges-grid">
          ${badgesHtml}
        </div>
        <div class="tldr-score-widget">
          <div class="tldr-score-tool">
            <div class="tldr-score-circle brand-${toolA.name.toLowerCase().replace(/[^a-z]/g, "")}" style="--score: ${toolA.rating || 9}; --tool-color: ${toolA.color}">
              <div class="tldr-score-inner">${toolA.rating ? toolA.rating.toFixed(1) : "9.0"}</div>
            </div>
            <span class="tldr-score-tool-name" style="color: ${toolA.color};">${toolA.name}</span>
          </div>
          
          <div style="font-weight: 800; font-size: 0.9rem; color: var(--text-muted);">VS</div>
          
          <div class="tldr-score-tool">
            <div class="tldr-score-circle brand-${toolB.name.toLowerCase().replace(/[^a-z]/g, "")}" style="--score: ${toolB.rating || 9}; --tool-color: ${toolB.color}">
              <div class="tldr-score-inner">${toolB.rating ? toolB.rating.toFixed(1) : "9.0"}</div>
            </div>
            <span class="tldr-score-tool-name" style="color: ${toolB.color};">${toolB.name}</span>
          </div>
        </div>
      </div>
    </div>
  `;
}

// 3. Interactive Comparison Table Grid
let currentCategoryFilter = "all";
let showDifferencesOnly = false;
let globalCompareData = null;

function renderMatrix(data) {
  const container = document.getElementById("matrix-container");
  if (!container) return;

  globalCompareData = data;
  
  // Render header control panel
  container.innerHTML = `
    <div class="matrix-section">
      <div class="matrix-controls">
        <div class="matrix-tabs">
          <button class="matrix-tab active" onclick="filterMatrixCategory('all', this)">All Features</button>
          <button class="matrix-tab" onclick="filterMatrixCategory('core', this)">Core Features</button>
          <button class="matrix-tab" onclick="filterMatrixCategory('essential', this)">Essential Specs</button>
          <button class="matrix-tab" onclick="filterMatrixCategory('advanced', this)">Advanced / AI Models</button>
          <button class="matrix-tab" onclick="filterMatrixCategory('pricing', this)">Pricing & Plans</button>
        </div>
        
        <div class="toggle-wrapper" id="diff-toggle" onclick="toggleDifferences()">
          <span>Show Differences Only</span>
          <div class="toggle-switch">
            <div class="toggle-knob"></div>
          </div>
        </div>
      </div>
      
      <div class="matrix-grid" id="matrix-grid-rows">
        <!-- Rows injected dynamically -->
      </div>
    </div>
  `;

  renderMatrixRows();
}

function renderMatrixRows() {
  const grid = document.getElementById("matrix-grid-rows");
  if (!grid || !globalCompareData) return;

  const toolA = globalCompareData.toolA;
  const toolB = globalCompareData.toolB;
  const criteria = globalCompareData.criteria || [];

  let html = `
    <div class="matrix-header">
      <div>Comparison Criteria</div>
      <div>${toolA.name}</div>
      <div>${toolB.name}</div>
      <div>Detailed Assessment</div>
    </div>
  `;

  let visibleRowCount = 0;

  criteria.forEach(item => {
    // 1. Category Filter
    if (currentCategoryFilter !== "all" && item.category !== currentCategoryFilter) {
      return;
    }

    // 2. Differences Filter
    const scoreDiff = Math.abs((item.scoreA || 0) - (item.scoreB || 0));
    const valDiff = String(item.valueA).trim().toLowerCase() !== String(item.valueB).trim().toLowerCase();
    const hasDiff = scoreDiff > 5 || valDiff; // Consider it different if score differs by > 5% or text value differs

    if (showDifferencesOnly && !hasDiff) {
      return;
    }

    visibleRowCount++;

    // Calculate rating bars
    const renderRatingBar = (score, color) => {
      if (score === undefined || score === null || score === 0) return "";
      return `
        <div class="matrix-rating-bar">
          <div class="matrix-rating-fill" style="width: ${score}%; background: ${color};"></div>
        </div>
      `;
    };

    // Check winner
    let winnerIndicatorA = "";
    let winnerIndicatorB = "";
    if (item.scoreA > item.scoreB) {
      winnerIndicatorA = `<span class="matrix-winner-indicator" title="Winner in this criteria">👑</span>`;
    } else if (item.scoreB > item.scoreA) {
      winnerIndicatorB = `<span class="matrix-winner-indicator" title="Winner in this criteria">👑</span>`;
    }

    html += `
      <div class="matrix-row" data-category="${item.category}">
        <div class="matrix-cell-feature">${item.name}</div>
        <div class="matrix-cell-val">
          <span class="matrix-val-text">${item.valueA} ${winnerIndicatorA}</span>
          ${renderRatingBar(item.scoreA, toolA.color)}
        </div>
        <div class="matrix-cell-val">
          <span class="matrix-val-text">${item.valueB} ${winnerIndicatorB}</span>
          ${renderRatingBar(item.scoreB, toolB.color)}
        </div>
        <div class="matrix-cell-notes">${item.notes}</div>
      </div>
    `;
  });

  if (visibleRowCount === 0) {
    html += `
      <div style="padding: 40px; text-align: center; color: var(--text-secondary); font-size: 0.95rem;">
        <i data-lucide="info" style="width: 24px; height: 24px; margin: 0 auto 12px; display: block; color: var(--primary-light);"></i>
        No matching criteria found with current filters. Try turning off "Show Differences Only".
      </div>
    `;
  }

  grid.innerHTML = html;

  if (typeof lucide !== "undefined") {
    lucide.createIcons();
  }
}

window.filterMatrixCategory = function(category, buttonEl) {
  currentCategoryFilter = category;
  
  // Update active tab styling
  const tabs = document.querySelectorAll(".matrix-tab");
  tabs.forEach(tab => tab.classList.remove("active"));
  buttonEl.classList.add("active");

  renderMatrixRows();
};

window.toggleDifferences = function() {
  showDifferencesOnly = !showDifferencesOnly;
  
  // Toggle switch class
  const toggle = document.getElementById("diff-toggle");
  if (showDifferencesOnly) {
    toggle.classList.add("active");
  } else {
    toggle.classList.remove("active");
  }

  renderMatrixRows();
};

// 4. Quick Decision Card
function renderDecision(data) {
  const container = document.getElementById("decision-container");
  if (!container) return;

  const toolA = data.toolA;
  const toolB = data.toolB;
  const decision = data.quickDecision || {};

  let listHtmlA = "";
  (decision.toolA || []).forEach(item => {
    listHtmlA += `<li>${item}</li>`;
  });

  let listHtmlB = "";
  (decision.toolB || []).forEach(item => {
    listHtmlB += `<li>${item}</li>`;
  });

  container.innerHTML = `
    <div class="decision-card">
      <h3 style="text-align: center;"><i data-lucide="compass" style="width: 22px; height: 22px; color: var(--accent); vertical-align: middle; margin-right: 8px;"></i> Which AI Should You Choose?</h3>
      <div class="decision-grid">
        <div class="decision-column">
          <div class="decision-column-title" style="color: ${toolA.color};">
            <span>${toolA.logo}</span> Choose ${toolA.name} If...
          </div>
          <ul class="decision-list">
            ${listHtmlA}
          </ul>
        </div>
        <div class="decision-column">
          <div class="decision-column-title" style="color: ${toolB.color};">
            <span>${toolB.logo}</span> Choose ${toolB.name} If...
          </div>
          <ul class="decision-list">
            ${listHtmlB}
          </ul>
        </div>
      </div>
    </div>
  `;
}

// 5. Pros & Cons Sections
function renderProsCons(data) {
  const container = document.getElementById("pros-cons-container");
  if (!container) return;

  const toolA = data.toolA;
  const toolB = data.toolB;
  const pc = data.prosCons || {};

  const makeList = (items, type) => {
    let html = "";
    (items || []).forEach(item => {
      html += `<li class="${type === "pro" ? "pro-item" : "con-item"}">${item}</li>`;
    });
    return html;
  };

  container.innerHTML = `
    <div class="pros-cons-section">
      <div class="pros-cons-card">
        <h3 style="color: ${toolA.color};"><span>${toolA.logo}</span> ${toolA.name} Pros & Cons</h3>
        <h4 style="font-size: 0.85rem; font-weight: 800; color: var(--accent); margin: 12px 0 8px;">✓ Pros / Advantages</h4>
        <ul class="pros-cons-list" style="margin-bottom: 20px;">
          ${makeList((pc.toolA || {}).pros, "pro")}
        </ul>
        <h4 style="font-size: 0.85rem; font-weight: 800; color: #ef4444; margin: 12px 0 8px;">✗ Cons / Disadvantages</h4>
        <ul class="pros-cons-list">
          ${makeList((pc.toolA || {}).cons, "con")}
        </ul>
      </div>
      
      <div class="pros-cons-card">
        <h3 style="color: ${toolB.color};"><span>${toolB.logo}</span> ${toolB.name} Pros & Cons</h3>
        <h4 style="font-size: 0.85rem; font-weight: 800; color: var(--accent); margin: 12px 0 8px;">✓ Pros / Advantages</h4>
        <ul class="pros-cons-list" style="margin-bottom: 20px;">
          ${makeList((pc.toolB || {}).pros, "pro")}
        </ul>
        <h4 style="font-size: 0.85rem; font-weight: 800; color: #ef4444; margin: 12px 0 8px;">✗ Cons / Disadvantages</h4>
        <ul class="pros-cons-list">
          ${makeList((pc.toolB || {}).cons, "con")}
        </ul>
      </div>
    </div>
  `;
}

// 6. FAQ accordions
function renderFAQ(data) {
  const container = document.getElementById("faq-container");
  if (!container) return;

  const faqItems = data.faq || [];
  if (faqItems.length === 0) return;

  let html = `<h3>❓ Frequently Asked Questions</h3>`;
  
  faqItems.forEach((item, index) => {
    html += `
      <div class="faq-item">
        <button class="faq-trigger" type="button" aria-expanded="false">
          ${item.question}
          <span class="faq-chevron"><i data-lucide="chevron-down" style="width: 18px; height: 18px;"></i></span>
        </button>
        <div class="faq-content">
          <p>${item.answer}</p>
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
}

function initFAQAccordions() {
  const triggers = document.querySelectorAll(".faq-trigger");
  triggers.forEach(trigger => {
    trigger.addEventListener("click", () => {
      const expanded = trigger.getAttribute("aria-expanded") === "true";
      const content = trigger.nextElementSibling;
      
      // Toggle current accordion
      if (expanded) {
        trigger.setAttribute("aria-expanded", "false");
        content.style.display = "none";
        const chevron = trigger.querySelector(".faq-chevron");
        if (chevron) chevron.style.transform = "rotate(0deg)";
      } else {
        trigger.setAttribute("aria-expanded", "true");
        content.style.display = "block";
        const chevron = trigger.querySelector(".faq-chevron");
        if (chevron) chevron.style.transform = "rotate(180deg)";
      }
    });
  });
}
