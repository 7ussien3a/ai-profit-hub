/**
 * AI Profit Hub - Smart Search Engine v1.0 (2026)
 * Supports cross-content search (Articles, Tools, Prompts, Comparisons) & Autocomplete Suggestions.
 */

(function () {
  'use strict';

  // State variables
  let allTools = [];
  let allPrompts = [];
  let generatedContentIndex = [];
  let activeCategory = "all"; // 'all', 'articles', 'tools', 'prompts', 'compare'
  let searchQuery = "";

  // Static Comparisons Database
  const COMPARISONS = [
    {
      title: "ChatGPT vs Claude (2026): Which AI is Better?",
      url: "compare/chatgpt-vs-claude.html",
      desc: "An in-depth side-by-side comparison of ChatGPT and Claude 3.5 Sonnet across writing quality, coding, context size, and pricing.",
      cat: "Compare",
      img: "/images/tech_abstract_design.webp",
      date: "June 23, 2026"
    },
    {
      title: "ChatGPT vs Gemini (2026): Which AI is Better?",
      url: "compare/chatgpt-vs-gemini.html",
      desc: "Head-to-head comparison of OpenAI's ChatGPT and Google's Gemini Advanced. Analysis of voice features, logic, and ecosystem.",
      cat: "Compare",
      img: "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=600&h=300&fit=crop",
      date: "June 23, 2026"
    },
    {
      title: "Claude vs Gemini (2026): Side-by-Side Comparison",
      url: "compare/claude-vs-gemini.html",
      desc: "Anthropic Claude vs Google Gemini Advanced. Deep dive into reasoning, coding, long context window, and writing styles.",
      cat: "Compare",
      img: "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=600&h=300&fit=crop",
      date: "June 23, 2026"
    },
    {
      title: "Midjourney vs DALL-E 3: Best AI Image Generator",
      url: "compare/midjourney-vs-dalle.html",
      desc: "Creative shootout: Midjourney v6 vs OpenAI's DALL-E 3. Which AI generator produces better graphic art and photorealism?",
      cat: "Compare",
      img: "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=600&h=300&fit=crop",
      date: "June 20, 2026"
    },
    {
      title: "Perplexity AI vs ChatGPT (2026): The Search Battle",
      url: "compare/perplexity-vs-chatgpt.html",
      desc: "Real-time search vs conversational intelligence. Compare Perplexity Pro research features against ChatGPT Search engines.",
      cat: "Compare",
      img: "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?w=600&h=300&fit=crop",
      date: "June 20, 2026"
    }
  ];

  document.addEventListener("DOMContentLoaded", () => {
    initSearchEngine();
  });

  async function initSearchEngine() {
    setupSuggestionsUI();
    setupTabPills();
    setupEventListeners();
    const searchInput = document.getElementById("searchInput");
    if (searchInput) {
      searchQuery = searchInput.value;
    }

    try {
      // Fetch static and generated search databases.
      const [toolsRes, promptsRes, contentRes] = await Promise.all([
        fetch("data/tools.json"),
        fetch("data/prompts.json"),
        fetch("data/search-index.json").catch(() => null)
      ]);

      if (toolsRes.ok) allTools = await toolsRes.json();
      if (promptsRes.ok) allPrompts = await promptsRes.json();
      if (contentRes && contentRes.ok) generatedContentIndex = await contentRes.json();

      updateStatsMessage();
      applySearch();
    } catch (error) {
      console.error("Error fetching search database files:", error);
    }
  }

  function updateStatsMessage() {
    const stats = document.getElementById("searchStats");
    if (!stats) return;
    const articleCount = generatedContentIndex.length || (window.ARTICLES ? window.ARTICLES.length : 0);
    const toolCount = allTools.length;
    const promptCount = allPrompts.length;
    const compareCount = COMPARISONS.length;
    const total = articleCount + toolCount + promptCount + compareCount;

    stats.innerHTML = `Searching through <strong>${total}</strong> total items (articles, tools, prompts, & comparisons)`;
  }

  /* ==========================================================================
     1. Autocomplete Suggestions Setup
     ========================================================================== */
  let suggestionsContainer = null;

  function setupSuggestionsUI() {
    const searchWrap = document.querySelector(".search-wrap");
    if (!searchWrap) return;

    // Create container for dropdown suggestions
    suggestionsContainer = document.createElement("div");
    suggestionsContainer.className = "search-suggestions";

    // Inject styling directly to avoid external dependencies
    const style = document.createElement("style");
    style.id = "suggestions-styles";
    style.textContent = `
      .search-wrap { position: relative; }
      .search-suggestions {
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: var(--bg-card, #1A1F35);
        border: 1px solid var(--border, rgba(148,163,184,.1));
        border-radius: 12px;
        margin-top: 8px;
        box-shadow: var(--shadow-lg, 0 10px 30px rgba(0,0,0,0.5));
        z-index: 1000;
        display: none;
        max-height: 380px;
        overflow-y: auto;
        padding: 8px 0;
      }
      .suggestion-item {
        padding: 10px 16px;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 12px;
        transition: var(--transition);
        text-decoration: none;
      }
      .suggestion-item:hover {
        background: var(--bg-elevated, #252B45);
      }
      .suggestion-icon {
        font-size: 1.2rem;
        width: 32px;
        height: 32px;
        background: rgba(255,255,255,0.04);
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
      }
      .suggestion-body {
        display: flex;
        flex-direction: column;
        overflow: hidden;
      }
      .suggestion-title {
        font-size: 0.9rem;
        font-weight: 700;
        color: var(--text-primary);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      .suggestion-meta {
        font-size: 0.72rem;
        color: var(--text-secondary);
        display: flex;
        gap: 8px;
        align-items: center;
      }
      .suggestion-tag {
        font-size: 0.65rem;
        text-transform: uppercase;
        font-weight: 800;
        color: var(--accent);
      }
    `;
    document.head.appendChild(style);
    searchWrap.appendChild(suggestionsContainer);
  }

  function renderSuggestions(query) {
    if (!suggestionsContainer) return;
    const q = query.toLowerCase().trim();

    if (!q) {
      suggestionsContainer.style.display = "none";
      return;
    }

    // Filter potential suggestion hits from all databases
    const items = [];

    // Articles
    const articleSource = generatedContentIndex.length
      ? generatedContentIndex
      : (window.ARTICLES || []);
    articleSource.forEach(a => {
      const haystack = [
        a.title,
        a.description || a.desc,
        a.category || a.cat,
        a.contentType,
        (a.tags || []).join(" "),
        (a.keywords || []).join(" ")
      ].join(" ").toLowerCase();
      if (haystack.includes(q)) {
        items.push({
          title: a.title,
          url: a.url,
          type: a.contentType || "Article",
          emoji: "📰"
        });
      }
    });

    // Tools
    allTools.forEach(t => {
      if (t.name.toLowerCase().includes(q)) {
        items.push({ title: t.name, url: t.url, type: "AI Tool", emoji: t.emoji || "🤖" });
      }
    });

    // Prompts
    allPrompts.forEach(p => {
      if (p.title.toLowerCase().includes(q)) {
        items.push({ title: p.title, url: "prompts-library.html", type: "Prompt", emoji: "⚡" });
      }
    });

    // Comparisons
    COMPARISONS.forEach(c => {
      if (c.title.toLowerCase().includes(q)) {
        items.push({ title: c.title, url: c.url, type: "Compare", emoji: "⚖️" });
      }
    });

    if (items.length === 0) {
      suggestionsContainer.style.display = "none";
      return;
    }

    // Render up to 5 suggestions
    suggestionsContainer.innerHTML = items.slice(0, 5).map(item => `
      <a href="${escapeAttribute(safeUrl(item.url))}" class="suggestion-item">
        <div class="suggestion-icon">${item.emoji}</div>
        <div class="suggestion-body">
          <div class="suggestion-title">${escapeHtml(item.title)}</div>
          <div class="suggestion-meta">
            <span class="suggestion-tag">${escapeHtml(item.type)}</span>
          </div>
        </div>
      </a>
    `).join("");

    suggestionsContainer.style.display = "block";
  }

  /* ==========================================================================
     2. Tab Navigation Setup
     ========================================================================== */
  function setupTabPills() {
    const pillsContainer = document.getElementById("filterPills");
    if (!pillsContainer) return;

    // Redesign pills to show unified types
    pillsContainer.innerHTML = `
      <button class="pill active" data-cat="all">All Results</button>
      <button class="pill" data-cat="articles">Articles</button>
      <button class="pill" data-cat="tools">AI Tools</button>
      <button class="pill" data-cat="prompts">Prompts Library</button>
      <button class="pill" data-cat="compare">Comparisons</button>
    `;
  }

  /* ==========================================================================
     3. Event Listeners
     ========================================================================== */
  function setupEventListeners() {
    const searchInput = document.getElementById("searchInput");
    if (searchInput) {
      searchInput.addEventListener("input", (e) => {
        searchQuery = e.target.value;
        renderSuggestions(searchQuery);
        applySearch();
      });

      // Close suggestions on click outside
      document.addEventListener("click", (e) => {
        if (suggestionsContainer && !e.target.closest(".search-wrap")) {
          suggestionsContainer.style.display = "none";
        }
      });
    }

    // Tab Pill clicks
    const pills = document.querySelectorAll(".pill");
    pills.forEach(pill => {
      pill.addEventListener("click", () => {
        pills.forEach(p => p.classList.remove("active"));
        pill.classList.add("active");
        activeCategory = pill.dataset.cat;
        applySearch();
      });
    });

    // Content Filter overrides
    const typeFilter = document.getElementById("contentTypeFilter");
    if (typeFilter) {
      typeFilter.addEventListener("change", applySearch);
    }
    const companyFilter = document.getElementById("companyFilter");
    if (companyFilter) {
      companyFilter.addEventListener("change", applySearch);
    }
  }

  /* ==========================================================================
     4. Main Search Logic
     ========================================================================== */
  function applySearch() {
    const grid = document.getElementById("resultsGrid");
    const noRes = document.getElementById("noResults");
    const stats = document.getElementById("searchStats");
    if (!grid || !noRes) return;

    const q = searchQuery.toLowerCase().trim();

    // Collect all elements across databases
    let items = [];

    // 1. Articles
    if (activeCategory === "all" || activeCategory === "articles") {
      const articleSource = generatedContentIndex.length
        ? generatedContentIndex
        : (window.ARTICLES || []);
      articleSource.forEach(a => {
        items.push({
          type: "article",
          title: a.title,
          url: a.url,
          desc: a.description || a.desc || "",
          body: a.body,
          date: a.date || "",
          cat: a.category || a.cat || "Articles",
          img: a.image || a.img || "",
          author: a.author,
          tags: a.tags || [],
          keywords: a.keywords || []
        });
      });
    }

    // 2. Tools
    if (activeCategory === "all" || activeCategory === "tools") {
      allTools.forEach(t => {
        items.push({
          type: "tool",
          title: t.name,
          url: t.url,
          desc: t.desc,
          tagline: t.tagline,
          rating: t.rating,
          pricing: t.pricingType,
          detail: t.pricingDetail,
          emoji: t.emoji || "🤖",
          developer: t.developer,
          cat: "AI Tool"
        });
      });
    }

    // 3. Prompts
    if (activeCategory === "all" || activeCategory === "prompts") {
      allPrompts.forEach(p => {
        items.push({
          type: "prompt",
          title: p.title,
          prompt: p.prompt,
          desc: p.desc,
          rating: p.rating,
          cat: p.category.toUpperCase()
        });
      });
    }

    // 4. Comparisons
    if (activeCategory === "all" || activeCategory === "compare") {
      COMPARISONS.forEach(c => {
        items.push({
          type: "compare",
          title: c.title,
          url: c.url,
          desc: c.desc,
          date: c.date,
          cat: "Compare",
          img: c.img
        });
      });
    }

    // Filter elements
    let filtered = items.filter(item => {
      // Search keyword filter
      const matchQ = !q ||
                     item.title.toLowerCase().includes(q) ||
                     (item.desc && item.desc.toLowerCase().includes(q)) ||
                     (item.prompt && item.prompt.toLowerCase().includes(q)) ||
                     (item.tagline && item.tagline.toLowerCase().includes(q)) ||
                     (item.body && item.body.toLowerCase().includes(q)) ||
                     (item.author && item.author.toLowerCase().includes(q)) ||
                     (item.tags && item.tags.join(" ").toLowerCase().includes(q)) ||
                     (item.keywords && item.keywords.join(" ").toLowerCase().includes(q));

      // Extra dropdown filters (keep backwards compatibility with existing reviews/articles filters)
      let matchType = true;
      const selectType = document.getElementById("contentTypeFilter") ? document.getElementById("contentTypeFilter").value : "all";
      if (selectType === "reviews") {
        matchType = item.url && item.url.includes("reviews/");
      } else if (selectType === "articles") {
        matchType = item.type === "article" && !item.url.includes("reviews/");
      }

      let matchCompany = true;
      const selectCompany = document.getElementById("companyFilter") ? document.getElementById("companyFilter").value : "all";
      if (selectCompany !== "all") {
        const compName = selectCompany.toLowerCase();
        matchCompany = item.title.toLowerCase().includes(compName) ||
                       (item.desc && item.desc.toLowerCase().includes(compName)) ||
                       (item.url && item.url.toLowerCase().includes(compName));
      }

      return matchQ && matchType && matchCompany;
    });

    // Render Grid
    if (filtered.length === 0) {
      grid.innerHTML = "";
      noRes.style.display = "block";
      if (stats) stats.innerHTML = "No results found";
      return;
    }

    noRes.style.display = "none";
    if (stats) {
      stats.innerHTML = `Found <strong>${filtered.length}</strong> matching result${filtered.length !== 1 ? 's' : ''}`;
    }

    grid.innerHTML = filtered.map(item => {
      if (item.type === "article" || item.type === "compare") {
        // Standard card with image
        return `
          <article class="result-card">
            <a href="${escapeAttribute(safeUrl(item.url))}">
              <img src="${escapeAttribute(safeUrl(item.img || '/images/robot-technology.jpg'))}" alt="${escapeAttribute(item.title)}" loading="lazy">
            </a>
            <div class="result-card-body">
              <span class="result-tag" style="background:var(--primary-glow);">${escapeHtml(item.cat)}</span>
              <h3><a href="${escapeAttribute(safeUrl(item.url))}">${highlightText(item.title, q)}</a></h3>
              <p class="result-desc">${highlightText(item.desc || "", q)}</p>
              <div class="result-meta">${escapeHtml(item.date || "")}</div>
            </div>
          </article>
        `;
      } else if (item.type === "tool") {
        // Dynamic tool card
        let pricingClass = "badge-paid";
        if (item.pricing.toLowerCase() === "free") pricingClass = "badge-free";
        if (item.pricing.toLowerCase() === "freemium") pricingClass = "badge-freemium";

        return `
          <article class="result-card" style="padding: 24px; justify-content: space-between;">
            <div>
              <div style="display: flex; gap: 12px; align-items: center; margin-bottom: 14px;">
                <span style="font-size: 2rem;">${item.emoji}</span>
                <div>
                  <h3 style="font-size: 1.15rem; font-weight:800; margin:0;"><a href="ai-tools-directory.html">${highlightText(item.title, q)}</a></h3>
                  <span style="font-size: 0.72rem; color: var(--text-secondary);">by ${escapeHtml(item.developer || "")}</span>
                </div>
              </div>
              <span class="result-tag" style="background:var(--primary-glow);">${escapeHtml(item.cat)}</span>
              <p class="result-desc" style="margin-top: 10px;">${highlightText(item.desc, q)}</p>
            </div>

            <div style="border-top:1px solid var(--border); padding-top:14px; margin-top:16px; display:flex; justify-content:space-between; align-items:center;">
              <span style="color:#fbbf24; font-weight:700; font-size:0.85rem;">★ ${item.rating.toFixed(1)}</span>
              <span class="badge ${pricingClass}" style="font-size:0.75rem; border-radius:20px; font-weight:700; padding:2px 8px;">${escapeHtml(item.pricing)}</span>
            </div>
          </article>
        `;
      } else if (item.type === "prompt") {
        // Dynamic prompt card
        return `
          <article class="result-card" style="padding: 24px; justify-content: space-between;">
            <div>
              <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                <span class="result-tag" style="background:rgba(108,99,255,0.1); color: var(--primary-light);">${escapeHtml(item.cat)}</span>
                <span style="color:#fbbf24; font-weight:700; font-size:0.85rem;">★ ${item.rating.toFixed(1)}</span>
              </div>
              <h3 style="font-size: 1.1rem; font-weight:800; margin-bottom:8px;"><a href="prompts-library.html">${highlightText(item.title, q)}</a></h3>
              <p class="result-desc">${highlightText(item.desc, q)}</p>
            </div>

            <div style="border-top:1px solid var(--border); padding-top:14px; margin-top:16px;">
              <button class="play-btn" onclick="copySearchPrompt(this, \`${item.prompt.replace(/`/g, '\\`').replace(/\$/g, '\\$')}\`)" style="width:100%; padding: 8px; font-size: 0.8rem;">
                <i data-lucide="copy" style="width:14px; height:14px; vertical-align:middle; margin-right:4px;"></i> Copy Prompt
              </button>
            </div>
          </article>
        `;
      }
    }).join("");

    if (typeof lucide !== "undefined") {
      lucide.createIcons();
    }
  }

  function highlightText(text, q) {
    const escapedText = escapeHtml(text || "");
    if (!q) return escapedText;
    const re = new RegExp('(' + q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi');
    return escapedText.replace(re, '<mark>$1</mark>');
  }

  function escapeHtml(value) {
    return String(value || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function escapeAttribute(value) {
    return escapeHtml(value);
  }

  function safeUrl(value) {
    const url = String(value || "").trim();
    if (url && !/^(?:javascript|data|vbscript):/i.test(url) && !url.startsWith("//")) {
      return url;
    }
    return "#";
  }

  // Bind global helper for copying prompts in search results
  window.copySearchPrompt = function(btn, text) {
    navigator.clipboard.writeText(text).then(() => {
      const origHtml = btn.innerHTML;
      btn.innerHTML = 'Copied!';
      setTimeout(() => {
        btn.innerHTML = origHtml;
      }, 2000);
    });
  };

})();
