/**
 * AI Profit Hub - User Dashboard Engine v1.0 (2026)
 * Handles favorites lists, reading list bookmarks, and Tech Stack management.
 */

document.addEventListener("DOMContentLoaded", () => {
  initDashboard();
});

let allTools = [];
let allPrompts = [];
let favTools = [];
let favPrompts = [];
let favArticles = [];
let techStack = [];

async function initDashboard() {
  initTabs();
  loadLocalStorage();

  try {
    // Fetch central databases
    const [toolsRes, promptsRes] = await Promise.all([
      fetch("data/tools.json"),
      fetch("data/prompts.json")
    ]);

    if (toolsRes.ok) allTools = await toolsRes.json();
    if (promptsRes.ok) allPrompts = await promptsRes.json();

    renderAll();
  } catch (error) {
    console.error("Error loading dashboard data databases:", error);
  }
}

/* ==========================================================================
   1. UI Tab Control
   ========================================================================== */
function initTabs() {
  const tabs = document.querySelectorAll(".dash-tab-btn");
  const panels = document.querySelectorAll(".dash-panel");

  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      panels.forEach(p => p.classList.remove("active"));

      tab.classList.add("active");
      const targetPanel = document.getElementById(tab.dataset.target);
      if (targetPanel) {
        targetPanel.classList.add("active");
      }

      if (typeof lucide !== "undefined") {
        lucide.createIcons();
      }
    });
  });
}

/* ==========================================================================
   2. LocalStorage Loader
   ========================================================================== */
function loadLocalStorage() {
  // 1. Saved Tools
  const savedTools = localStorage.getItem("fav_tools");
  try {
    favTools = savedTools ? JSON.parse(savedTools) : [];
  } catch (e) {
    favTools = [];
  }

  // 2. Saved Prompts
  const savedPrompts = localStorage.getItem("fav_prompts");
  try {
    favPrompts = savedPrompts ? JSON.parse(savedPrompts) : [];
  } catch (e) {
    favPrompts = [];
  }

  // 3. Reading List
  const savedArticles = localStorage.getItem("fav_articles");
  try {
    favArticles = savedArticles ? JSON.parse(savedArticles) : [];
  } catch (e) {
    favArticles = [];
  }

  // 4. Tech Stack
  const savedStack = localStorage.getItem("tech_stack");
  try {
    techStack = savedStack ? JSON.parse(savedStack) : [];
  } catch (e) {
    techStack = [];
  }
}

/* ==========================================================================
   3. Rendering Hub
   ========================================================================== */
function renderAll() {
  renderSavedTools();
  renderSavedPrompts();
  renderReadingList();
  renderTechStack();
  renderStackOptions();
}

// 1. Saved Tools Panel
function renderSavedTools() {
  const grid = document.getElementById("favToolsGrid");
  if (!grid) return;

  if (favTools.length === 0) {
    grid.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">☆</div>
        <h3>No saved tools yet</h3>
        <p>Go to the AI Tools Directory and click the star icon on any tool card to save it here.</p>
        <a href="best-ai-tools/index.html" class="play-btn" style="padding: 8px 16px; font-size:0.85rem;">Browse Directory</a>
      </div>
    `;
    return;
  }

  // Find tools details
  const matchingTools = allTools.filter(t => favTools.includes(t.id));

  grid.innerHTML = matchingTools.map(tool => {
    let badgeClass = "badge-paid";
    if (tool.pricingType.toLowerCase() === "free") badgeClass = "badge-free";
    if (tool.pricingType.toLowerCase() === "freemium") badgeClass = "badge-freemium";

    return `
      <div class="reading-list-card">
        <div>
          <div class="read-card-header">
            <span class="read-tag" style="background:var(--primary-glow);">${tool.pricingType}</span>
            <span style="font-size: 1.6rem;">${tool.emoji || "🤖"}</span>
          </div>
          <h3 class="read-title"><a href="${tool.url}" target="_blank" rel="noopener">${tool.name}</a></h3>
          <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 14px;">${tool.tagline}</p>
        </div>
        <div class="read-actions">
          <button class="remove-fav-btn" onclick="removeFavoriteTool('${tool.id}')">
            <i data-lucide="trash-2" style="width: 14px; height: 14px;"></i> Remove
          </button>
          <a href="${tool.url}" target="_blank" rel="noopener" style="color: var(--primary-light); font-weight:700;">Visit →</a>
        </div>
      </div>
    `;
  }).join("");

  if (typeof lucide !== "undefined") lucide.createIcons();
}

window.removeFavoriteTool = function(id) {
  favTools = favTools.filter(item => item !== id);
  localStorage.setItem("fav_tools", JSON.stringify(favTools));
  renderSavedTools();
};

// 2. Saved Prompts Panel
function renderSavedPrompts() {
  const grid = document.getElementById("favPromptsGrid");
  if (!grid) return;

  if (favPrompts.length === 0) {
    grid.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">⚡</div>
        <h3>No saved prompts yet</h3>
        <p>Visit the Prompts Library and click the star icon to save prompts here.</p>
        <a href="prompts-library.html" class="play-btn" style="padding: 8px 16px; font-size:0.85rem;">Browse Prompts</a>
      </div>
    `;
    return;
  }

  const matchingPrompts = allPrompts.filter(p => favPrompts.includes(p.id));

  grid.innerHTML = matchingPrompts.map(prompt => {
    return `
      <div class="reading-list-card">
        <div>
          <div class="read-card-header">
            <span class="read-tag">${prompt.category}</span>
            <span style="color:#fbbf24; font-weight:700;">★ ${prompt.rating.toFixed(1)}</span>
          </div>
          <h3 class="read-title" style="margin-bottom:6px;">${prompt.title}</h3>
          <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 14px;">${prompt.desc}</p>
          <div style="display:none;" class="hidden-prompt-text">${prompt.prompt}</div>
        </div>
        <div class="read-actions">
          <button class="remove-fav-btn" onclick="removeFavoritePrompt('${prompt.id}')">
            <i data-lucide="trash-2" style="width: 14px; height: 14px;"></i> Remove
          </button>
          <button class="play-btn" onclick="copyDashboardPrompt(this)" style="padding: 6px 12px; font-size: 0.75rem;">
            Copy Prompt
          </button>
        </div>
      </div>
    `;
  }).join("");

  if (typeof lucide !== "undefined") lucide.createIcons();
}

window.removeFavoritePrompt = function(id) {
  favPrompts = favPrompts.filter(item => item !== id);
  localStorage.setItem("fav_prompts", JSON.stringify(favPrompts));
  renderSavedPrompts();
};

window.copyDashboardPrompt = function(btn) {
  const card = btn.closest(".reading-list-card");
  if (!card) return;
  const text = card.querySelector(".hidden-prompt-text").textContent;
  
  navigator.clipboard.writeText(text).then(() => {
    const orig = btn.textContent;
    btn.textContent = "Copied!";
    setTimeout(() => {
      btn.textContent = orig;
    }, 2000);
  });
};

// 3. Reading List Panel
function renderReadingList() {
  const grid = document.getElementById("readingListGrid");
  if (!grid) return;

  if (favArticles.length === 0) {
    grid.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">📰</div>
        <h3>Reading list is empty</h3>
        <p>Add articles, guides or comparisons to your list by clicking the bookmark button on any post.</p>
        <a href="search.html" class="play-btn" style="padding: 8px 16px; font-size:0.85rem;">Find Articles</a>
      </div>
    `;
    return;
  }

  grid.innerHTML = favArticles.map((article, idx) => {
    return `
      <div class="reading-list-card">
        <div>
          <div class="read-card-header">
            <span class="read-tag" style="background:var(--primary-glow);">${article.type || "Article"}</span>
          </div>
          <h3 class="read-title"><a href="${article.url}">${article.title}</a></h3>
        </div>
        <div class="read-actions">
          <button class="remove-fav-btn" onclick="removeReadingListItem(${idx})">
            <i data-lucide="trash-2" style="width: 14px; height: 14px;"></i> Remove
          </button>
          <a href="${article.url}" style="color: var(--primary-light); font-weight:700;">Read →</a>
        </div>
      </div>
    `;
  }).join("");

  if (typeof lucide !== "undefined") lucide.createIcons();
}

window.removeReadingListItem = function(idx) {
  favArticles.splice(idx, 1);
  localStorage.setItem("fav_articles", JSON.stringify(favArticles));
  renderReadingList();
};

// 4. Tech Stack Panel
function renderTechStack() {
  const grid = document.getElementById("techStackGrid");
  const countLabel = document.getElementById("stackCount");
  if (!grid || !countLabel) return;

  countLabel.textContent = techStack.length;

  if (techStack.length === 0) {
    grid.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">🔧</div>
        <h3>No stack tools added</h3>
        <p>Select which AI tools you actively use daily in your workflow below to build your toolkit.</p>
      </div>
    `;
    return;
  }

  const matchingTools = allTools.filter(t => techStack.includes(t.id));

  grid.innerHTML = matchingTools.map(tool => {
    return `
      <div class="reading-list-card" style="border-color: var(--accent);">
        <div style="display:flex; gap: 12px; align-items:center; margin-bottom:12px;">
          <span style="font-size: 2.2rem;">${tool.emoji || "🤖"}</span>
          <div>
            <h3 style="font-size: 1.1rem; margin:0;">${tool.name}</h3>
            <span style="font-size: 0.72rem; color:var(--text-muted);">${tool.category.toUpperCase()}</span>
          </div>
        </div>
        <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 12px; line-height:1.5;">${tool.tagline}</p>
        <div class="read-actions" style="border-top: none; padding-top:0;">
          <button class="remove-fav-btn" onclick="toggleTechStackId('${tool.id}', false)">
            <i data-lucide="x" style="width: 14px; height: 14px;"></i> Remove from Stack
          </button>
          <a href="${tool.url}" target="_blank" rel="noopener" style="color:var(--accent); font-weight:700;">Visit →</a>
        </div>
      </div>
    `;
  }).join("");

  if (typeof lucide !== "undefined") lucide.createIcons();
}

function renderStackOptions() {
  const container = document.getElementById("stackOptionsGrid");
  if (!container) return;

  container.innerHTML = allTools.map(tool => {
    const isActive = techStack.includes(tool.id);
    const activeClass = isActive ? "active" : "";
    const isChecked = isActive ? "checked" : "";

    return `
      <label class="stack-option-label ${activeClass}" id="label-stack-${tool.id}">
        <input type="checkbox" ${isChecked} onchange="handleStackToggle(this, '${tool.id}')">
        <span>${tool.emoji || "🤖"} ${tool.name}</span>
      </label>
    `;
  }).join("");
}

window.handleStackToggle = function(checkbox, id) {
  toggleTechStackId(id, checkbox.checked);
};

function toggleTechStackId(id, shouldAdd) {
  const index = techStack.indexOf(id);
  if (shouldAdd && index === -1) {
    techStack.push(id);
  } else if (!shouldAdd && index !== -1) {
    techStack.splice(index, 1);
  }

  localStorage.setItem("tech_stack", JSON.stringify(techStack));
  
  // Re-sync UI state
  renderTechStack();
  renderStackOptions();
}
