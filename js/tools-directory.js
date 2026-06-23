/**
 * AI Profit Hub - AI Tools Directory Engine v1.0 (2026)
 * Dynamically fetches, searches, filters and paginates AI Tools.
 */

let allTools = [];
let filteredTools = [];
let favoriteTools = []; // Local favorite tools list
let currentPage = 1;
const itemsPerPage = 12;

// Active filter states
let activeCategory = "all";
let activePricing = "all";
let showHusseinPicksOnly = false;
let searchQuery = "";

document.addEventListener("DOMContentLoaded", () => {
  initDirectory();
});

async function initDirectory() {
  const toolsGrid = document.getElementById("toolsGrid");
  if (!toolsGrid) return;

  try {
    const savedFavorites = localStorage.getItem("fav_tools");
    if (savedFavorites) {
      try {
        favoriteTools = JSON.parse(savedFavorites);
      } catch (e) {
        favoriteTools = [];
      }
    }

    const response = await fetch("data/tools.json");
    if (!response.ok) throw new Error("Failed to load tools database");
    allTools = await response.json();
    filteredTools = [...allTools];
    
    setupEventListeners();
    renderDirectory();
    updateStats();
  } catch (error) {
    console.error("Error initializing AI Tools Directory:", error);
    toolsGrid.innerHTML = `
      <div style="grid-column: 1/-1; padding: 40px; text-align: center; color: #ef4444;">
        <i data-lucide="alert-triangle" style="width: 32px; height: 32px; margin: 0 auto 12px; display: block;"></i>
        Failed to load tools directory database. Please try reloading the page.
      </div>
    `;
    if (typeof lucide !== "undefined") lucide.createIcons();
  }
}

function setupEventListeners() {
  // Search Input
  const searchInput = document.getElementById("toolSearch");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      searchQuery = e.target.value.toLowerCase().trim();
      currentPage = 1;
      applyFilters();
    });
  }

  // Category Buttons
  const catBtns = document.querySelectorAll(".cat-btn");
  catBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      catBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      activeCategory = btn.dataset.cat;
      currentPage = 1;
      applyFilters();
    });
  });

  // Pricing Filter Dropdown (Add dynamically or target if exists)
  const pricingSelect = document.getElementById("pricingFilter");
  if (pricingSelect) {
    pricingSelect.addEventListener("change", (e) => {
      activePricing = e.target.value;
      currentPage = 1;
      applyFilters();
    });
  }

  // Hussein's Picks Checkbox/Toggle
  const pickToggle = document.getElementById("husseinPicksToggle");
  if (pickToggle) {
    pickToggle.addEventListener("change", (e) => {
      showHusseinPicksOnly = e.target.checked;
      currentPage = 1;
      applyFilters();
    });
  }
}

function applyFilters() {
  filteredTools = allTools.filter(tool => {
    // 1. Category Filter
    const matchCategory = activeCategory === "all" || tool.category === activeCategory;
    
    // 2. Pricing Filter
    const matchPricing = activePricing === "all" || tool.pricingType.toLowerCase() === activePricing.toLowerCase();
    
    // 3. Hussein Picks Filter
    const matchHussein = !showHusseinPicksOnly || tool.husseinPick === true;

    // 4. Search Query Filter
    const searchString = `${tool.name} ${tool.tagline} ${tool.desc} ${tool.developer}`.toLowerCase();
    const matchSearch = !searchQuery || searchString.includes(searchQuery);

    return matchCategory && matchPricing && matchHussein && matchSearch;
  });

  renderDirectory();
}

function renderDirectory() {
  const grid = document.getElementById("toolsGrid");
  const noResults = document.getElementById("noResults");
  if (!grid) return;

  // Pagination bounds
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedItems = filteredTools.slice(startIndex, endIndex);

  if (filteredTools.length === 0) {
    grid.innerHTML = "";
    if (noResults) noResults.style.display = "block";
    renderPagination(0);
    return;
  }

  if (noResults) noResults.style.display = "none";

  let html = "";
  paginatedItems.forEach(tool => {
    const isPick = tool.husseinPick ? "hussein-pick" : "";
    const ratingStars = renderStars(tool.rating);
    const isFavorited = favoriteTools.includes(tool.id);
    const favIcon = isFavorited ? "★" : "☆";
    const favClass = isFavorited ? "active" : "";
    
    // Pricing Badge class
    let badgeClass = "badge-paid";
    if (tool.pricingType.toLowerCase() === "free") badgeClass = "badge-free";
    if (tool.pricingType.toLowerCase() === "freemium") badgeClass = "badge-freemium";

    // Pros and Cons lists
    let prosHtml = "";
    (tool.pros || []).slice(0, 3).forEach(p => prosHtml += `<li>✓ ${p}</li>`);
    let consHtml = "";
    (tool.cons || []).slice(0, 2).forEach(c => consHtml += `<li>✗ ${c}</li>`);

    // Alternatives badges
    let altsHtml = "";
    if (tool.alternatives && tool.alternatives.length > 0) {
      altsHtml = `
        <div class="dir-card-alts">
          <span>Alternatives:</span>
          <div class="dir-alts-badges">
            ${tool.alternatives.map(alt => `<span class="alt-badge">${alt}</span>`).join("")}
          </div>
        </div>
      `;
    }

    // Review Button HTML
    let reviewBtnHtml = "";
    if (tool.reviewLink) {
      reviewBtnHtml = `
        <a href="${tool.reviewLink}" class="tool-link dir-review-btn">Review</a>
      `;
    }

    html += `
      <div class="tool-card ${isPick}" data-id="${tool.id}">
        <div class="tool-card-header" style="position: relative; width: 100%;">
          <div class="tool-emoji">${tool.emoji || "🤖"}</div>
          <div class="tool-title-wrapper">
            <h3 class="tool-name">${tool.name}</h3>
            <span class="tool-tagline">by ${tool.developer || "Creator"}</span>
          </div>
          <button class="tool-fav-btn ${favClass}" onclick="toggleFavoriteTool('${tool.id}', this)" aria-label="Favorite tool" style="margin-left: auto; background: transparent; border: none; font-size: 1.25rem; cursor: pointer; color: ${isFavorited ? '#fbbf24' : 'var(--text-muted)'}; transition: var(--transition);">
            ${favIcon}
          </button>
        </div>
        
        <p class="tool-desc">${tool.desc}</p>
        
        <div class="dir-rating-row">
          <span class="dir-rating-val">${tool.rating.toFixed(1)}</span>
          <span class="dir-rating-stars">${ratingStars}</span>
        </div>

        <!-- Dynamic Slide-out Quick Details Drawer -->
        <div class="tool-card-drawer" id="drawer-${tool.id}" style="display: none;">
          <div class="drawer-grid">
            <div class="drawer-col">
              <span class="drawer-heading">Pros / Advantages</span>
              <ul class="drawer-list pros-list">${prosHtml || "<li>Tested and reliable</li>"}</ul>
            </div>
            <div class="drawer-col">
              <span class="drawer-heading">Cons / Drawbacks</span>
              <ul class="drawer-list cons-list">${consHtml || "<li>None major reported</li>"}</ul>
            </div>
          </div>
          ${altsHtml}
        </div>

        <div class="tool-footer">
          <div class="tool-badges">
            <span class="badge ${badgeClass}">${tool.pricingType}</span>
            <span class="badge badge-cat">${tool.pricingDetail || ""}</span>
          </div>
          <div class="tool-actions">
            <button class="dir-drawer-btn" onclick="toggleToolDrawer('${tool.id}', this)" aria-label="Toggle details">
              <i data-lucide="chevron-down" style="width: 16px; height: 16px;"></i> Details
            </button>
            ${reviewBtnHtml}
            <a href="${tool.url}" class="tool-link" target="_blank" rel="noopener">Visit →</a>
          </div>
        </div>
      </div>
    `;
  });

  grid.innerHTML = html;
  renderPagination(filteredTools.length);

  if (typeof lucide !== "undefined") {
    lucide.createIcons();
  }
}

function renderStars(rating) {
  const fullStars = Math.floor(rating);
  const halfStar = rating % 1 >= 0.5 ? 1 : 0;
  const emptyStars = 5 - fullStars - halfStar;
  
  return "★".repeat(fullStars) + (halfStar ? "½" : "") + "☆".repeat(emptyStars);
}

window.toggleToolDrawer = function(id, btn) {
  const drawer = document.getElementById(`drawer-${id}`);
  if (!drawer) return;

  const isOpen = drawer.style.display === "block";
  drawer.style.display = isOpen ? "none" : "block";

  // Toggle button state & icon rotation
  const icon = btn.querySelector("i");
  if (isOpen) {
    btn.classList.remove("active");
    if (icon) icon.style.transform = "rotate(0deg)";
  } else {
    btn.classList.add("active");
    if (icon) icon.style.transform = "rotate(180deg)";
  }
};

function renderPagination(totalItems) {
  let paginationContainer = document.getElementById("dir-pagination");
  
  if (!paginationContainer) {
    // Inject pagination wrapper dynamically if it doesn't exist
    const grid = document.getElementById("toolsGrid");
    if (!grid) return;
    
    paginationContainer = document.createElement("div");
    paginationContainer.id = "dir-pagination";
    paginationContainer.className = "dir-pagination-container";
    grid.parentNode.insertBefore(paginationContainer, grid.nextSibling);
  }

  const totalPages = Math.ceil(totalItems / itemsPerPage);
  
  if (totalPages <= 1) {
    paginationContainer.innerHTML = "";
    return;
  }

  let html = "";
  
  // Previous Button
  const prevDisabled = currentPage === 1 ? "disabled" : "";
  html += `
    <button class="page-btn prev-btn" ${prevDisabled} onclick="changeDirPage(${currentPage - 1})">
      &larr; Prev
    </button>
  `;

  // Page Numbers
  for (let i = 1; i <= totalPages; i++) {
    const activeClass = currentPage === i ? "active" : "";
    html += `
      <button class="page-btn num-btn ${activeClass}" onclick="changeDirPage(${i})">
        ${i}
      </button>
    `;
  }

  // Next Button
  const nextDisabled = currentPage === totalPages ? "disabled" : "";
  html += `
    <button class="page-btn next-btn" ${nextDisabled} onclick="changeDirPage(${currentPage + 1})">
      Next &rarr;
    </button>
  `;

  paginationContainer.innerHTML = html;
}

window.changeDirPage = function(page) {
  currentPage = page;
  renderDirectory();
  // Smooth scroll back to top of the grid
  const searchBar = document.querySelector(".search-bar");
  if (searchBar) {
    searchBar.scrollIntoView({ behavior: "smooth", block: "start" });
  }
};

function updateStats() {
  const statsContainer = document.querySelector(".directory-stats");
  if (!statsContainer) return;

  const count = allTools.length;
  const categoriesCount = new Set(allTools.map(t => t.category)).size;

  statsContainer.innerHTML = `
    <div class="directory-stat"><strong>${count}+</strong><span>Tools Listed</span></div>
    <div class="directory-stat"><strong>${categoriesCount}</strong><span>Categories</span></div>
    <div class="directory-stat"><strong>100%</strong><span>Hands-On Tested</span></div>
  `;
}

window.toggleFavoriteTool = function(id, btn) {
  const index = favoriteTools.indexOf(id);
  if (index === -1) {
    favoriteTools.push(id);
    btn.textContent = "★";
    btn.style.color = "#fbbf24";
    btn.classList.add("active");
  } else {
    favoriteTools.splice(index, 1);
    btn.textContent = "☆";
    btn.style.color = "var(--text-muted)";
    btn.classList.remove("active");
  }
  localStorage.setItem("fav_tools", JSON.stringify(favoriteTools));
};
