/**
 * AI Profit Hub - AI Resources Hub Engine v1.0 (2026)
 * Dynamically fetches and renders resources, cheat sheets and blueprints.
 */

let allResources = [];
let filteredResources = [];
let activeTag = "all";

document.addEventListener("DOMContentLoaded", () => {
  initResources();
});

async function initResources() {
  const grid = document.getElementById("resourcesGrid");
  if (!grid) return;

  try {
    const response = await fetch("data/resources.json");
    if (!response.ok) throw new Error("Failed to load resources data");
    allResources = await response.json();
    filteredResources = [...allResources];

    setupEventListeners();
    renderResources();
    renderTagFilters();
  } catch (error) {
    console.error("Error loading resources:", error);
    grid.innerHTML = `
      <div style="grid-column: 1/-1; padding: 40px; text-align: center; color: #ef4444;">
        <i data-lucide="alert-triangle" style="width: 32px; height: 32px; margin: 0 auto 12px; display: block;"></i>
        Failed to load resources hub. Please try reloading the page.
      </div>
    `;
    if (typeof lucide !== "undefined") lucide.createIcons();
  }
}

function setupEventListeners() {
  // Search filter
  const searchInput = document.getElementById("resourceSearch");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      const query = e.target.value.toLowerCase().trim();
      filterResources(query);
    });
  }
}

function renderTagFilters() {
  const container = document.getElementById("tagFilters");
  if (!container) return;

  // Extract unique tags
  const tags = new Set();
  allResources.forEach(res => {
    (res.tags || []).forEach(t => tags.add(t));
  });

  let html = `<button class="res-tag-btn active" onclick="filterByTag('all', this)">All Mapped</button>`;
  tags.forEach(tag => {
    html += `<button class="res-tag-btn" onclick="filterByTag('${tag}', this)">#${tag}</button>`;
  });

  container.innerHTML = html;
}

window.filterByTag = function(tag, buttonEl) {
  activeTag = tag;
  
  // Toggle active class
  const buttons = document.querySelectorAll(".res-tag-btn");
  buttons.forEach(btn => btn.classList.remove("active"));
  buttonEl.classList.add("active");

  applyFilters();
};

function filterResources(query = "") {
  applyFilters(query);
}

function applyFilters(query = "") {
  const searchVal = query.toLowerCase();

  filteredResources = allResources.filter(res => {
    const matchTag = activeTag === "all" || (res.tags || []).includes(activeTag);
    const searchString = `${res.title} ${res.desc} ${res.type}`.toLowerCase();
    const matchSearch = !searchVal || searchString.includes(searchVal);

    return matchTag && matchSearch;
  });

  renderResources();
}

function renderResources() {
  const grid = document.getElementById("resourcesGrid");
  if (!grid) return;

  grid.innerHTML = "";

  if (filteredResources.length === 0) {
    grid.innerHTML = `
      <div style="grid-column: 1/-1; padding: 40px; text-align: center; color: var(--text-secondary);">
        <i data-lucide="info" style="width: 24px; height: 24px; margin: 0 auto 12px; display: block; color: var(--primary-light);"></i>
        No resources found matching the criteria.
      </div>
    `;
    if (typeof lucide !== "undefined") lucide.createIcons();
    return;
  }

  filteredResources.forEach(res => {
    let icon = "file-text";
    if (res.type.toLowerCase().includes("cheat")) icon = "layout";
    if (res.type.toLowerCase().includes("workflow")) icon = "git-branch";

    const card = document.createElement("div");
    card.className = "resource-card";
    card.innerHTML = `
      <div class="res-card-icon">
        <i data-lucide="${icon}" style="width: 24px; height: 24px; color: var(--primary-light);"></i>
      </div>
      <div class="res-card-body">
        <span class="res-type-badge">${res.type} (${res.format})</span>
        <h3 class="res-title">${res.title}</h3>
        <p class="res-desc">${res.desc}</p>
        <div class="res-tags">
          ${(res.tags || []).map(t => `<span class="res-tag">#${t}</span>`).join("")}
        </div>
      </div>
      <div class="res-card-footer">
        <a href="${res.downloadUrl}" class="res-download-btn" ${res.downloadUrl.startsWith("http") ? 'target="_blank" rel="noopener"' : 'download'}>
          <i data-lucide="download" style="width: 15px; height: 15px;"></i> ${res.actionText || "Get Resource"}
        </a>
      </div>
    `;
    grid.appendChild(card);
  });

  if (typeof lucide !== "undefined") {
    lucide.createIcons();
  }
}
