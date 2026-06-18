/**
 * article-sidebar.js — AI Profit Hub
 * Auto-injects a sticky two-column layout with sidebar into every article page.
 * Works on ALL articles without modifying their HTML.
 * Features:
 *  - Auto-generated TOC from h2 headings
 *  - Active section highlighting on scroll
 *  - Key stats card (if data-stats attribute present)
 *  - Related articles
 *  - Ad placeholder
 *  - Fully responsive (collapses on tablet/mobile)
 */
(function () {
  'use strict';

  // Only run on article pages
  var main = document.querySelector('main');
  if (!main) return;

  // Don't double-inject
  if (document.querySelector('.aph-sidebar-injected')) return;

  // ── 1. INJECT STYLES ─────────────────────────────────────────────────────
  var style = document.createElement('style');
  style.textContent = [
    /* Upgrade hero images to high-res on large screens */
    'img[loading="eager"]{ image-rendering: -webkit-optimize-contrast; }',

    /* Wrap the main element in a two-column grid */
    '.aph-article-wrap {',
    '  display: grid;',
    '  grid-template-columns: 1fr 290px;',
    '  gap: 48px;',
    '  max-width: 1240px;',
    '  margin: 0 auto;',
    '  padding: 0 24px 80px;',
    '  align-items: start;',
    '}',
    '.aph-article-body { min-width: 0; }',

    /* Sticky sidebar */
    '.aph-sidebar {',
    '  position: sticky;',
    '  top: 88px;',
    '  display: flex;',
    '  flex-direction: column;',
    '  gap: 18px;',
    '  max-height: calc(100vh - 110px);',
    '  overflow-y: auto;',
    '  scrollbar-width: none;',
    '}',
    '.aph-sidebar::-webkit-scrollbar { display: none; }',

    /* Sidebar cards */
    '.aph-card {',
    '  background: var(--bg-card, #1A1F35);',
    '  border: 1px solid var(--border, rgba(148,163,184,0.1));',
    '  border-radius: 12px;',
    '  padding: 18px;',
    '}',
    '.aph-card h4 {',
    '  font-size: 0.72rem;',
    '  font-weight: 700;',
    '  text-transform: uppercase;',
    '  letter-spacing: 0.09em;',
    '  color: var(--text-secondary, #94A3B8);',
    '  margin: 0 0 12px;',
    '}',

    /* TOC list */
    '.aph-toc { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 4px; }',
    '.aph-toc a {',
    '  display: block;',
    '  font-size: 0.8rem;',
    '  color: var(--text-secondary, #94A3B8);',
    '  text-decoration: none;',
    '  padding: 5px 0 5px 10px;',
    '  border-left: 2px solid var(--border, rgba(148,163,184,0.1));',
    '  line-height: 1.4;',
    '  transition: color 0.2s, border-color 0.2s;',
    '}',
    '.aph-toc a:hover, .aph-toc a.aph-active {',
    '  color: var(--primary-light, #8B83FF);',
    '  border-color: var(--primary, #6C63FF);',
    '}',

    /* Related links */
    '.aph-related-link {',
    '  display: block;',
    '  font-size: 0.8rem;',
    '  color: var(--primary-light, #8B83FF);',
    '  text-decoration: none;',
    '  padding: 8px 10px;',
    '  background: var(--bg-elevated, #252B45);',
    '  border-radius: 7px;',
    '  line-height: 1.4;',
    '  margin-bottom: 8px;',
    '  transition: background 0.2s;',
    '}',
    '.aph-related-link:hover { background: rgba(108,99,255,0.15); }',
    '.aph-related-link:last-child { margin-bottom: 0; }',

    /* Ad box */
    '.aph-ad {',
    '  background: var(--bg-card, #1A1F35);',
    '  border: 1px dashed var(--border, rgba(148,163,184,0.15));',
    '  border-radius: 12px;',
    '  min-height: 250px;',
    '  display: flex;',
    '  align-items: center;',
    '  justify-content: center;',
    '  font-size: 0.7rem;',
    '  color: var(--text-secondary, #94A3B8);',
    '}',

    /* Progress bar inside TOC */
    '.aph-read-bar {',
    '  height: 3px;',
    '  background: var(--border, rgba(148,163,184,0.1));',
    '  border-radius: 3px;',
    '  margin-bottom: 12px;',
    '  overflow: hidden;',
    '}',
    '.aph-read-fill {',
    '  height: 100%;',
    '  width: 0%;',
    '  background: linear-gradient(90deg, #6C63FF, #00D4AA);',
    '  border-radius: 3px;',
    '  transition: width 0.15s linear;',
    '}',

    /* Responsive: collapse on tablet */
    '@media (max-width: 1060px) {',
    '  .aph-article-wrap {',
    '    grid-template-columns: 1fr;',
    '    max-width: 800px;',
    '    gap: 32px;',
    '    padding-bottom: 60px;',
    '  }',
    '  .aph-sidebar {',
    '    position: static;',
    '    max-height: none;',
    '    display: grid;',
    '    grid-template-columns: 1fr 1fr;',
    '    gap: 14px;',
    '  }',
    '}',
    '@media (max-width: 600px) {',
    '  .aph-article-wrap { padding: 0 16px 48px; gap: 20px; }',
    '  .aph-sidebar { grid-template-columns: 1fr; }',
    '}',

    /* Fix image quality: upgrade srcset on all article hero images */
    '.aph-hero-img { width: 100%; height: auto; max-height: 520px; object-fit: cover; display: block; border-radius: 14px; }',
  ].join('\n');
  document.head.appendChild(style);

  // ── 2. UPGRADE HERO IMAGES ────────────────────────────────────────────────
  // Find the first large image in the article (hero / cover)
  var heroImgs = main.querySelectorAll('img');
  heroImgs.forEach(function (img, i) {
    var src = img.getAttribute('src') || '';
    // Only upgrade Unsplash images that don't already have srcset
    if (src.indexOf('unsplash.com') > -1 && !img.getAttribute('srcset')) {
      // Extract base URL (without width/quality params)
      var base = src.split('?')[0];
      img.setAttribute('srcset',
        base + '?w=800&q=80&auto=format&fit=crop 800w, ' +
        base + '?w=1200&q=85&auto=format&fit=crop 1200w, ' +
        base + '?w=1600&q=90&auto=format&fit=crop 1600w'
      );
      img.setAttribute('sizes', '(max-width:768px) 100vw, (max-width:1200px) 90vw, 1100px');
      // Upgrade src itself to high-res
      img.setAttribute('src', base + '?w=1600&q=85&auto=format&fit=crop');
      if (i === 0) {
        img.setAttribute('loading', 'eager');
        img.setAttribute('fetchpriority', 'high');
      }
    }
  });

  // ── 3. BUILD TOC FROM H2 HEADINGS ────────────────────────────────────────
  var headings = main.querySelectorAll('h2');
  var tocItems = [];
  headings.forEach(function (h, i) {
    if (!h.id) {
      h.id = 'section-' + i;
    }
    tocItems.push({ id: h.id, text: h.textContent.trim().slice(0, 55) });
  });

  // ── 4. RELATED ARTICLES DATA ──────────────────────────────────────────────
  var ALL_ARTICLES = [
    { title: 'China AI Price War: Qwen3.7 vs OpenAI', url: '/articles/china-ai-qwen3-deepseek-v4-price-war-2026.html' },
    { title: 'Microsoft Launches 7 In-House AI Models', url: '/articles/microsoft-mai-7-models-copilot-2026.html' },
    { title: 'Apple Reinvents Siri at WWDC 2026', url: '/articles/apple-intelligence-siri-wwdc-2026.html' },
    { title: 'Anthropic Raises $65 Billion', url: '/articles/anthropic-65-billion-fable-5-model-2026.html' },
    { title: 'Google Gemma 4: Local AI for Everyone', url: '/articles/google-gemma-4-local-ai-laptop-2026.html' },
    { title: 'Google Gemini 3.5 Live Translate', url: '/articles/google-gemini-3-5-live-translate-20260615.html' },
    { title: 'Gemini Omni: Edit Video With Words', url: '/articles/gemini-omni-video-revolution.html' },
    { title: 'KPMG Deploys Claude for 276,000 Staff', url: '/articles/kpmg-claude-276000-employees.html' },
    { title: 'NVIDIA Hits $81.6B Record Revenue', url: '/articles/nvidia-record-revenue-ai-dominance.html' },
    { title: 'GPT-5 vs Claude 4: Full Comparison', url: '/articles/gpt-5-vs-claude-4.html' },
    { title: 'Best Free AI Tools for Students 2026', url: '/articles/best-free-ai-tools-students.html' },
    { title: 'ChatGPT Prompts for Productivity', url: '/articles/chatgpt-prompts-productivity.html' },
    { title: 'Samsung HBM4E AI Memory Chips', url: '/articles/samsung-hbm4e-ai-memory-chips.html' },
    { title: 'DuckDuckGo vs Google AI Search', url: '/articles/duckduckgo-vs-google-ai-search.html' },
    { title: 'DeepSeek vs Qwen vs Claude', url: '/articles/deepseek-qwen-claude-comparison.html' },
    { title: 'Microsoft Build 2026: Everything New', url: '/articles/microsoft-build-2026.html' },
    { title: 'Cloudflare AI & Layoffs 2026', url: '/articles/cloudflare-ai-layoffs-2026.html' },
    { title: 'Meta Llama 4 Muse & Spark', url: '/articles/meta-llama-4-muse-spark.html' },
    { title: 'AI for Faceless YouTube Channels', url: '/articles/ai-tools-faceless-youtube.html' },
    { title: 'How to Make Money with AI Art', url: '/articles/make-money-ai-art.html' },
  ];

  // Pick 3 articles that are NOT the current page
  var currentPath = window.location.pathname;
  var related = ALL_ARTICLES.filter(function (a) {
    return currentPath.indexOf(a.url.replace('/articles/', '')) === -1;
  }).slice(0, 3);

  // ── 5. BUILD SIDEBAR HTML ─────────────────────────────────────────────────
  var sidebar = document.createElement('aside');
  sidebar.className = 'aph-sidebar aph-sidebar-injected';
  sidebar.setAttribute('aria-label', 'Article sidebar');

  var sidebarHTML = '';

  // TOC card (only if we found headings)
  if (tocItems.length > 0) {
    sidebarHTML += '<div class="aph-card">';
    sidebarHTML += '<div class="aph-read-bar"><div class="aph-read-fill" id="aphReadFill"></div></div>';
    sidebarHTML += '<h4>&#128221; In This Article</h4>';
    sidebarHTML += '<ul class="aph-toc" id="aphToc">';
    tocItems.forEach(function (item) {
      sidebarHTML += '<li><a href="#' + item.id + '" class="aph-toc-link">' + item.text + '</a></li>';
    });
    sidebarHTML += '</ul></div>';
  }

  // Related articles card
  if (related.length > 0) {
    sidebarHTML += '<div class="aph-card">';
    sidebarHTML += '<h4>&#128214; Related Reading</h4>';
    related.forEach(function (a) {
      sidebarHTML += '<a href="' + a.url + '" class="aph-related-link">' + a.title + ' &#8594;</a>';
    });
    sidebarHTML += '</div>';
  }

  // Ad placeholder
  sidebarHTML += '<div class="aph-ad">Advertisement</div>';

  sidebar.innerHTML = sidebarHTML;

  // ── 6. WRAP MAIN CONTENT IN TWO-COLUMN GRID ───────────────────────────────
  // Move all of main's children into article-body div, then add sidebar
  var wrap = document.createElement('div');
  wrap.className = 'aph-article-wrap';

  var body = document.createElement('div');
  body.className = 'aph-article-body';

  // Move children
  while (main.firstChild) {
    body.appendChild(main.firstChild);
  }

  wrap.appendChild(body);
  wrap.appendChild(sidebar);
  main.appendChild(wrap);

  // ── 7. SCROLL: TOC ACTIVE + READ PROGRESS ────────────────────────────────
  var tocLinks = document.querySelectorAll('.aph-toc-link');
  var readFill = document.getElementById('aphReadFill');

  if (tocLinks.length > 0 || readFill) {
    window.addEventListener('scroll', function () {
      var scrollTop = window.scrollY || document.documentElement.scrollTop;
      var docHeight = document.documentElement.scrollHeight - window.innerHeight;

      // Read progress
      if (readFill && docHeight > 0) {
        readFill.style.width = Math.min(100, (scrollTop / docHeight) * 100).toFixed(1) + '%';
      }

      // Active TOC item
      if (tocLinks.length > 0) {
        var current = '';
        headings.forEach(function (h) {
          if (h.getBoundingClientRect().top < 140) {
            current = h.id;
          }
        });
        tocLinks.forEach(function (link) {
          link.classList.toggle('aph-active', link.getAttribute('href') === '#' + current);
        });
      }
    }, { passive: true });
  }

  // ── 8. SMOOTH SCROLL for TOC links ───────────────────────────────────────
  tocLinks.forEach(function (link) {
    link.addEventListener('click', function (e) {
      var targetId = this.getAttribute('href').slice(1);
      var target = document.getElementById(targetId);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

})();
