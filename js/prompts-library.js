/**
 * AI Profit Hub - AI Prompts Library Engine v1.0 (2026)
 * Dynamically fetches, searches, filters, copies and bookmarks Prompts.
 */

let allPrompts = [];
let filteredPrompts = [];
let favoritePrompts = []; // Array of prompt IDs saved in localStorage

// Active filters
let activeCategory = "all";
let searchQuery = "";
let showFavoritesOnly = false;

document.addEventListener("DOMContentLoaded", () => {
  initPrompts();
});

async function initPrompts() {
  const promptsGrid = document.querySelector(".prompts-grid");
  if (!promptsGrid) return;

  // Load favorites from localStorage
  const savedFavorites = localStorage.getItem("fav_prompts");
  if (savedFavorites) {
    try {
      favoritePrompts = JSON.parse(savedFavorites);
    } catch (e) {
      favoritePrompts = [];
    }
  }

  try {
    const response = await fetch("data/prompts.json");
    if (!response.ok) throw new Error("Failed to load prompts database");
    allPrompts = await response.json();
    filteredPrompts = [...allPrompts];

    setupEventListeners();
    renderPrompts();
  } catch (error) {
    console.error("Error loading prompts library:", error);
    promptsGrid.innerHTML = `
      <div style="grid-column: 1/-1; padding: 40px; text-align: center; color: #ef4444;">
        <i data-lucide="alert-triangle" style="width: 32px; height: 32px; margin: 0 auto 12px; display: block;"></i>
        Failed to load prompts library. Please try reloading the page.
      </div>
    `;
    if (typeof lucide !== "undefined") lucide.createIcons();
  }
}

function setupEventListeners() {
  // Search Bar
  const searchInput = document.getElementById("promptSearch");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      searchQuery = e.target.value.toLowerCase().trim();
      applyFilters();
    });
  }

  // Category Pills
  const pills = document.querySelectorAll(".filter-pill");
  pills.forEach(pill => {
    pill.addEventListener("click", () => {
      pills.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      activeCategory = pill.dataset.filter;
      showFavoritesOnly = false; // Turn off favorites filter when choosing category
      
      const favBtn = document.getElementById("favFilterBtn");
      if (favBtn) favBtn.classList.remove("active");

      applyFilters();
    });
  });

  // Favorites Filter Button
  const favBtn = document.getElementById("favFilterBtn");
  if (favBtn) {
    favBtn.addEventListener("click", () => {
      pills.forEach(p => p.classList.remove("active"));
      favBtn.classList.toggle("active");
      showFavoritesOnly = favBtn.classList.contains("active");
      activeCategory = "all";
      applyFilters();
    });
  }
}

function applyFilters() {
  filteredPrompts = allPrompts.filter(item => {
    // 1. Category Filter
    const matchCategory = activeCategory === "all" || item.category === activeCategory;

    // 2. Favorites Filter
    const matchFavorites = !showFavoritesOnly || favoritePrompts.includes(item.id);

    // 3. Search Filter
    const searchString = `${item.title} ${item.desc} ${item.prompt} ${item.category}`.toLowerCase();
    const matchSearch = !searchQuery || searchString.includes(searchQuery);

    return matchCategory && matchFavorites && matchSearch;
  });

  renderPrompts();
}

function renderPrompts() {
  const grid = document.querySelector(".prompts-grid");
  if (!grid) return;

  // Clear grid
  grid.innerHTML = "";

  if (filteredPrompts.length === 0) {
    grid.innerHTML = `
      <div style="grid-column: 1/-1; padding: 40px; text-align: center; color: var(--text-secondary);">
        <i data-lucide="info" style="width: 24px; height: 24px; margin: 0 auto 12px; display: block; color: var(--primary-light);"></i>
        No prompts found matching your search.
      </div>
    `;
    if (typeof lucide !== "undefined") lucide.createIcons();
    return;
  }

  filteredPrompts.forEach(item => {
    const isFavorited = favoritePrompts.includes(item.id);
    const favIcon = isFavorited ? "★" : "☆";
    const favClass = isFavorited ? "active" : "";
    const featuredBadge = item.featured ? `<span class="prompt-tag featured-badge">🔥 Featured</span>` : "";

    const card = document.createElement("div");
    card.className = "prompt-card";
    card.dataset.id = item.id;
    card.innerHTML = `
      <div class="prompt-card-header">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; width: 100%;">
          <span class="prompt-tag">${item.category}</span>
          ${featuredBadge}
          <button class="prompt-fav-btn ${favClass}" onclick="toggleFavoritePrompt('${item.id}', this)" aria-label="Favorite prompt">
            ${favIcon}
          </button>
        </div>
        <h3>${item.title}</h3>
        <p>${item.desc}</p>
      </div>
      <div class="prompt-text-wrapper">
        <div class="prompt-text">${item.prompt}</div>
      </div>
      <button class="copy-btn" onclick="copyPromptText(this)">
        <span>📋 Copy Prompt</span>
      </button>
    `;

    grid.appendChild(card);
  });

  // Re-initialize Lucide Icons if lucide library is loaded
  if (typeof lucide !== "undefined") {
    lucide.createIcons();
  }
}

window.copyPromptText = function(button) {
  const card = button.closest(".prompt-card");
  if (!card) return;

  const text = card.querySelector(".prompt-text").textContent;
  
  navigator.clipboard.writeText(text).then(() => {
    const originalText = button.innerHTML;
    button.innerHTML = "<span>✅ Copied!</span>";
    button.style.background = "var(--accent)";
    button.style.color = "#04120f";
    
    setTimeout(() => {
      button.innerHTML = originalText;
      button.style.background = "";
      button.style.color = "";
    }, 2000);
  }).catch(err => {
    console.error("Failed to copy text: ", err);
  });
};

window.toggleFavoritePrompt = function(id, button) {
  const index = favoritePrompts.indexOf(id);
  if (index === -1) {
    favoritePrompts.push(id);
    button.textContent = "★";
    button.classList.add("active");
  } else {
    favoritePrompts.splice(index, 1);
    button.textContent = "☆";
    button.classList.remove("active");
    
    // If showFavoritesOnly filter is active, immediately remove from DOM
    if (showFavoritesOnly) {
      applyFilters();
    }
  }

  // Save to localStorage
  localStorage.setItem("fav_prompts", JSON.stringify(favoritePrompts));
};
