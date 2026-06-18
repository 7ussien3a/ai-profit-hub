/**
 * article-sidebar.js — AI Profit Hub  v2.0
 * ─────────────────────────────────────────
 * Automatically injects a sticky two-column layout on every article page:
 *
 *   ┌──────────────────────────────────────────────┐
 *   │  Article Header (FULL WIDTH — above grid)    │
 *   │  Hero Image     (FULL WIDTH — above grid)    │
 *   ├────────────────────────────┬─────────────────┤
 *   │  Article Body  (left col)  │  Sidebar (right)│
 *   │  • paragraphs              │  • TOC + scroll │
 *   │  • tables, tips            │  • related links│
 *   │  • share bar               │  • ad slot      │
 *   └────────────────────────────┴─────────────────┘
 *
 * Also upgrades all Unsplash images to high-res srcset automatically.
 */
(function () {
  'use strict';

  var main = document.querySelector('main');
  if (!main) return;
  if (document.querySelector('.aph-injected')) return; // no double-inject

  // ─── 1. STYLES ────────────────────────────────────────────────────────────
  var css = document.createElement('style');
  css.id = 'aph-sidebar-styles';
  css.textContent = [

    /* Full-width header zone (above the two-column grid) */
    '.aph-header-zone {',
    '  max-width: 1240px;',
    '  margin: 0 auto;',
    '  padding: 0 24px;',
    '}',

    /* Two-column wrapper */
    '.aph-grid {',
    '  max-width: 1240px;',
    '  margin: 0 auto;',
    '  padding: 0 24px 80px;',
    '  display: grid;',
    '  grid-template-columns: minmax(0, 1fr) 300px;',
    '  gap: 48px;',
    '  align-items: start;',
    '}',

    /* Body column */
    '.aph-body { min-width: 0; }',

    /* Sidebar column */
    '.aph-sidebar {',
    '  position: sticky;',
    '  top: 88px;',
    '  display: flex;',
    '  flex-direction: column;',
    '  gap: 16px;',
    '  max-height: calc(100vh - 108px);',
    '  overflow-y: auto;',
    '  scrollbar-width: none;',
    '}',
    '.aph-sidebar::-webkit-scrollbar { display: none; }',

    /* Sidebar cards */
    '.aph-card {',
    '  background: var(--bg-card, #1A1F35);',
    '  border: 1px solid var(--border, rgba(148,163,184,.1));',
    '  border-radius: 12px;',
    '  padding: 18px;',
    '}',
    '.aph-card-title {',
    '  font-size: .7rem;',
    '  font-weight: 700;',
    '  text-transform: uppercase;',
    '  letter-spacing: .09em;',
    '  color: var(--text-secondary, #94A3B8);',
    '  margin: 0 0 12px;',
    '}',

    /* Read progress bar inside TOC card */
    '.aph-prog-track {',
    '  height: 3px;',
    '  background: var(--border, rgba(148,163,184,.1));',
    '  border-radius: 3px;',
    '  margin-bottom: 14px;',
    '  overflow: hidden;',
    '}',
    '.aph-prog-fill {',
    '  height: 100%;',
    '  width: 0%;',
    '  background: linear-gradient(90deg,#6C63FF,#00D4AA);',
    '  border-radius: 3px;',
    '  transition: width .12s linear;',
    '}',

    /* TOC list */
    '.aph-toc { list-style: none; margin: 0; padding: 0; }',
    '.aph-toc li { margin-bottom: 3px; }',
    '.aph-toc a {',
    '  display: block;',
    '  font-size: .78rem;',
    '  color: var(--text-secondary, #94A3B8);',
    '  text-decoration: none;',
    '  padding: 5px 8px 5px 10px;',
    '  border-left: 2px solid var(--border, rgba(148,163,184,.1));',
    '  border-radius: 0 4px 4px 0;',
    '  line-height: 1.4;',
    '  transition: color .18s, border-color .18s, background .18s;',
    '}',
    '.aph-toc a:hover { color: var(--primary-light,#8B83FF); border-color: var(--primary,#6C63FF); background: rgba(108,99,255,.06); }',
    '.aph-toc a.aph-active { color: var(--primary-light,#8B83FF); border-color: var(--primary,#6C63FF); background: rgba(108,99,255,.08); font-weight:600; }',

    /* Related links */
    '.aph-link {',
    '  display: block;',
    '  font-size: .78rem;',
    '  color: var(--primary-light, #8B83FF);',
    '  text-decoration: none;',
    '  padding: 8px 10px;',
    '  background: var(--bg-elevated, #252B45);',
    '  border-radius: 7px;',
    '  line-height: 1.4;',
    '  margin-bottom: 7px;',
    '  transition: background .18s;',
    '}',
    '.aph-link:last-child { margin-bottom: 0; }',
    '.aph-link:hover { background: rgba(108,99,255,.18); }',

    /* Ad slot */
    '.aph-ad {',
    '  background: var(--bg-card, #1A1F35);',
    '  border: 1px dashed var(--border, rgba(148,163,184,.15));',
    '  border-radius: 12px;',
    '  min-height: 250px;',
    '  display: flex;',
    '  align-items: center;',
    '  justify-content: center;',
    '  font-size: .68rem;',
    '  color: var(--text-secondary, #94A3B8);',
    '}',

    /* ── RESPONSIVE ── */
    '@media (max-width: 1060px) {',
    '  .aph-grid { grid-template-columns: 1fr; max-width: 800px; gap: 32px; padding-bottom: 60px; }',
    '  .aph-sidebar { position: static; max-height: none; display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }',
    '  .aph-header-zone { max-width: 800px; }',
    '}',
    '@media (max-width: 640px) {',
    '  .aph-grid { padding: 0 16px 48px; gap: 20px; }',
    '  .aph-header-zone { padding: 0 16px; }',
    '  .aph-sidebar { grid-template-columns: 1fr; }',
    '}',
    '',
    '    /* Dynamic Lead Magnet Newsletter Box */',
    '    .aph-newsletter-box {',
    '      background: linear-gradient(135deg, #161b2c 0%, #0d111e 100%);',
    '      border: 2px solid var(--primary, #6C63FF);',
    '      border-radius: 14px;',
    '      padding: 28px;',
    '      margin: 36px 0;',
    '      box-shadow: 0 8px 30px rgba(108,99,255,0.15);',
    '      position: relative;',
    '      overflow: hidden;',
    '    }',
    '    .aph-newsletter-box::before {',
    '      content: "";',
    '      position: absolute;',
    '      top: -50px;',
    '      right: -50px;',
    '      width: 150px;',
    '      height: 150px;',
    '      background: radial-gradient(circle, rgba(108,99,255,0.2) 0%, transparent 70%);',
    '      pointer-events: none;',
    '    }',
    '    .aph-newsletter-title {',
    '      font-size: 1.15rem;',
    '      font-weight: 800;',
    '      color: var(--text-primary, #ffffff);',
    '      margin: 0 0 8px;',
    '      display: flex;',
    '      align-items: center;',
    '      gap: 8px;',
    '    }',
    '    .aph-newsletter-desc {',
    '      font-size: 0.88rem;',
    '      color: var(--text-secondary, #94A3B8);',
    '      line-height: 1.5;',
    '      margin-bottom: 18px;',
    '    }',
    '    .aph-newsletter-form {',
    '      display: flex;',
    '      gap: 10px;',
    '    }',
    '    .aph-newsletter-input {',
    '      flex: 1;',
    '      padding: 12px 16px;',
    '      border-radius: 8px;',
    '      border: 1px solid var(--border, rgba(148,163,184,.1));',
    '      background: var(--bg-card, #1A1F35);',
    '      color: var(--text-primary, #ffffff);',
    '      font-size: 0.875rem;',
    '      outline: none;',
    '    }',
    '    .aph-newsletter-input:focus {',
    '      border-color: var(--primary, #6C63FF);',
    '    }',
    '    .aph-newsletter-btn {',
    '      padding: 12px 24px;',
    '      background: var(--primary, #6C63FF);',
    '      color: #fff;',
    '      border: none;',
    '      border-radius: 8px;',
    '      font-size: 0.875rem;',
    '      font-weight: 600;',
    '      cursor: pointer;',
    '      transition: background 0.2s;',
    '    }',
    '    .aph-newsletter-btn:hover {',
    '      background: var(--primary-light, #a78bfa);',
    '    }',
    '    @media(max-width: 580px) {',
    '      .aph-newsletter-form {',
    '        flex-direction: column;',
    '      }',
    '    }',

  ].join('\n');
  document.head.appendChild(css);

  // ─── 2. UPGRADE IMAGES → high-res srcset ─────────────────────────────────
  main.querySelectorAll('img').forEach(function (img, i) {
    var src = img.getAttribute('src') || '';
    if (src.indexOf('unsplash.com') > -1 && !img.getAttribute('srcset')) {
      var base = src.split('?')[0];
      img.setAttribute('srcset',
        base + '?w=800&q=80&auto=format&fit=crop 800w,' +
        base + '?w=1200&q=85&auto=format&fit=crop 1200w,' +
        base + '?w=1600&q=90&auto=format&fit=crop 1600w'
      );
      img.setAttribute('sizes', '(max-width:768px) 100vw, (max-width:1200px) 90vw, 1100px');
      img.setAttribute('src', base + '?w=1600&q=85&auto=format&fit=crop');
      if (i === 0) { img.setAttribute('loading', 'eager'); img.setAttribute('fetchpriority', 'high'); }
    }
  });

  // ─── 3. SEPARATE: full-width header zone vs article body ─────────────────
  var allChildren = Array.from(main.children);
  var headerZoneEls = [];
  var bodyEls       = [];
  var inHeader      = true;

  allChildren.forEach(function (el) {
    if (!inHeader) { bodyEls.push(el); return; }

    var tag = el.tagName.toUpperCase();
    var cls = el.className || '';

    // Stop treating as header when we hit actual article content
    var isContent = (
      tag === 'P' ||
      tag === 'H2' ||
      tag === 'UL' ||
      tag === 'OL' ||
      tag === 'BLOCKQUOTE' ||
      cls.indexOf('stat-grid')    > -1 ||
      cls.indexOf('source-badge') > -1 ||
      cls.indexOf('highlight-box')> -1 ||
      cls.indexOf('personal-take')> -1 ||
      cls.indexOf('share-row')    > -1 ||
      cls.indexOf('article-body') > -1 ||
      cls.indexOf('article-two-col') > -1  // already has manual layout
    );

    // These always stay full-width
    var isHeaderZone = (
      cls.indexOf('article-header') > -1 ||
      cls.indexOf('article-cover')  > -1 ||
      cls.indexOf('bc')             > -1 ||
      (tag === 'DIV' && el.querySelector('img') && !isContent)
    );

    if (isHeaderZone) {
      headerZoneEls.push(el);
    } else if (isContent) {
      inHeader = false;
      bodyEls.push(el);
    } else {
      headerZoneEls.push(el);
    }
  });

  // If everything ended up in header (unusual layout), put it all in body
  if (bodyEls.length === 0) {
    bodyEls = headerZoneEls.splice(0);
  }

  // ─── 4. BUILD TOC from h2 headings in body elements ──────────────────────
  var tempDiv = document.createElement('div');
  bodyEls.forEach(function (el) { tempDiv.appendChild(el.cloneNode(true)); });
  var h2s = tempDiv.querySelectorAll('h2');
  var tocItems = [];
  h2s.forEach(function (h, i) { tocItems.push({ text: h.textContent.trim().slice(0, 52), idx: i }); });

  // Add IDs to real h2s in bodyEls
  var realH2s = [];
  bodyEls.forEach(function (el) {
    if (el.tagName === 'H2') realH2s.push(el);
    else if (el.querySelectorAll) el.querySelectorAll('h2').forEach(function (h) { realH2s.push(h); });
  });
  realH2s.forEach(function (h, i) { if (!h.id) h.id = 'aph-sec-' + i; });
  tocItems.forEach(function (item, i) { if (realH2s[i]) item.id = realH2s[i].id; });

  // ─── 4.5. DYNAMIC TRUST & CONVERSION ENHANCEMENTS ─────────────────────────
  // A. Check and inject Author Bio Box if missing
  var hasAuthorBio = false;
  bodyEls.forEach(function (el) {
    var cls = el.className || '';
    if (cls.indexOf('author-bio') > -1) hasAuthorBio = true;
  });

  if (!hasAuthorBio) {
    var bioBox = document.createElement('div');
    bioBox.className = 'author-bio';
    bioBox.style.cssText = 'display:flex;gap:20px;align-items:center;margin:40px 0 0;padding:24px;background:var(--bg-elevated,#1a1f2e);border:1px solid var(--border,#2a2f3e);border-radius:12px;';
    bioBox.innerHTML = '<img src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=80&h=80&fit=crop&crop=face" alt="Hussein" style="width:72px;height:72px;border-radius:50%;object-fit:cover;flex-shrink:0;">' +
                       '<div>' +
                       '<p style="margin:0 0 4px;font-weight:700;font-size:.95rem">Hussein — AI Profit Hub</p>' +
                       '<p style="margin:0;font-size:.85rem;line-height:1.6;color:var(--text-secondary)">Daily AI news, tool reviews, and practical guides. Follow AI Profit Hub for everything happening in artificial intelligence.</p>' +
                       '</div>';
    bodyEls.push(bioBox);
  }

  // B. Check and inject Lead Magnet Newsletter Subscription Box if missing
  var hasNewsletter = false;
  bodyEls.forEach(function (el) {
    var cls = el.className || '';
    if (cls.indexOf('lead-magnet-box') > -1 || cls.indexOf('aph-newsletter-box') > -1) {
      hasNewsletter = true;
    }
  });

  if (!hasNewsletter) {
    var nlBox = document.createElement('div');
    nlBox.className = 'aph-newsletter-box';
    var iframeId = 'ml_iframe_' + Math.round(Math.random() * 100000);
    nlBox.innerHTML = '<div class="aph-newsletter-title">📥 Join Our Free AI Newsletter</div>' +
                      '<div class="aph-newsletter-desc">Get the latest AI tool reviews, ChatGPT prompts, and productivity hacks sent straight to your inbox weekly. Join 10,000+ professionals working smarter.</div>' +
                      '<iframe name="' + iframeId + '" style="display:none;"></iframe>' +
                      '<form class="aph-newsletter-form" action="https://dashboard.mailerlite.com/jsonp/2455913/forms/190642525337290158/subscribe" method="POST" target="' + iframeId + '">' +
                      '<input type="email" name="fields[email]" class="aph-newsletter-input" placeholder="Enter your email address..." required>' +
                      '<input type="hidden" name="ml-submit" value="1">' +
                      '<input type="hidden" name="anticsrf" value="true">' +
                      '<button type="submit" class="aph-newsletter-btn">Subscribe</button>' +
                      '</form>' +
                      '<div class="aph-newsletter-success" style="display:none; color:#00D4AA; font-weight:600; font-size:0.9rem; text-align:center; padding:10px 0;">🎉 Thank you for subscribing! Please check your inbox.</div>';

    var form = nlBox.querySelector('form');
    var successDiv = nlBox.querySelector('.aph-newsletter-success');
    form.addEventListener('submit', function() {
      form.style.display = 'none';
      successDiv.style.display = 'block';
    });

    // Find the right place to insert it: before share-row or personal-take
    var insertIdx = -1;
    for (var j = 0; j < bodyEls.length; j++) {
      var cName = bodyEls[j].className || '';
      if (cName.indexOf('share-row') > -1 || cName.indexOf('personal-take') > -1 || cName.indexOf('author-bio') > -1) {
        insertIdx = j;
        break;
      }
    }
    if (insertIdx > -1) {
      bodyEls.splice(insertIdx, 0, nlBox);
    } else {
      bodyEls.push(nlBox);
    }
  }

  // ─── 5. RELATED ARTICLES ─────────────────────────────────────────────────
  var ARTICLES = [
    { t: 'China AI Price War: Qwen3.7 vs OpenAI',      u: '/articles/china-ai-qwen3-deepseek-v4-price-war-2026.html' },
    { t: 'Microsoft Launches 7 In-House AI Models',     u: '/articles/microsoft-mai-7-models-copilot-2026.html' },
    { t: 'Apple Reinvents Siri at WWDC 2026',           u: '/articles/apple-intelligence-siri-wwdc-2026.html' },
    { t: 'Anthropic Raises $65 Billion',                u: '/articles/anthropic-65-billion-fable-5-model-2026.html' },
    { t: 'Google Gemma 4: Run AI Locally Free',         u: '/articles/google-gemma-4-local-ai-laptop-2026.html' },
    { t: 'Google Gemini 3.5 Live Translation',          u: '/articles/google-gemini-3-5-live-translate-20260615.html' },
    { t: 'Gemini Omni: Edit Video With Words',          u: '/articles/gemini-omni-video-revolution.html' },
    { t: 'KPMG Deploys Claude for 276,000 Staff',       u: '/articles/kpmg-claude-276000-employees.html' },
    { t: 'NVIDIA Hits $81.6B Record Revenue',           u: '/articles/nvidia-record-revenue-ai-dominance.html' },
    { t: 'GPT-5 vs Claude 4: Full Comparison',          u: '/articles/gpt-5-vs-claude-4.html' },
    { t: 'Best Free AI Tools for Students 2026',        u: '/articles/best-free-ai-tools-students.html' },
    { t: 'ChatGPT Prompts for Productivity',            u: '/articles/chatgpt-prompts-productivity.html' },
    { t: 'Samsung HBM4E AI Memory Revolution',          u: '/articles/samsung-hbm4e-ai-memory-chips.html' },
    { t: 'DuckDuckGo vs Google AI Search',              u: '/articles/duckduckgo-vs-google-ai-search.html' },
    { t: 'DeepSeek vs Qwen vs Claude: Compared',        u: '/articles/deepseek-qwen-claude-comparison.html' },
    { t: 'Microsoft Build 2026: Everything New',        u: '/articles/microsoft-build-2026.html' },
    { t: 'Meta Llama 4 Muse & Spark Released',          u: '/articles/meta-llama-4-muse-spark.html' },
    { t: 'AI for Faceless YouTube Channels',            u: '/articles/ai-tools-faceless-youtube.html' },
    { t: 'How to Make Money with AI Art',               u: '/articles/make-money-ai-art.html' },
    { t: 'Agentic Coding: The Future of Programming',   u: '/articles/agentic-coding-future.html' },
  ];

  var path = window.location.pathname;
  var related = ARTICLES.filter(function (a) {
    return path.indexOf(a.u.replace('/articles/', '').replace('.html', '')) === -1;
  }).slice(0, 3);

  // ─── 6. BUILD SIDEBAR ─────────────────────────────────────────────────────
  var sidebar = document.createElement('aside');
  sidebar.className = 'aph-sidebar aph-injected';

  var sHTML = '';

  // TOC card
  if (tocItems.length > 0) {
    sHTML += '<div class="aph-card">';
    sHTML += '<div class="aph-prog-track"><div class="aph-prog-fill" id="aphFill"></div></div>';
    sHTML += '<p class="aph-card-title">&#128221; In This Article</p>';
    sHTML += '<ul class="aph-toc" id="aphToc">';
    tocItems.forEach(function (item) {
      sHTML += '<li><a href="#' + (item.id || '') + '" class="aph-tl">' + item.text + '</a></li>';
    });
    sHTML += '</ul></div>';
  }

  // Related
  if (related.length > 0) {
    sHTML += '<div class="aph-card">';
    sHTML += '<p class="aph-card-title">&#128214; Related Reading</p>';
    related.forEach(function (a) {
      sHTML += '<a href="' + a.u + '" class="aph-link">' + a.t + ' &#8594;</a>';
    });
    sHTML += '</div>';
  }

  // Ad slot
  sHTML += '<div class="aph-ad">Advertisement</div>';

  sidebar.innerHTML = sHTML;

  // ─── 7. INJECT INTO PAGE ─────────────────────────────────────────────────
  // Clear main
  while (main.firstChild) main.removeChild(main.firstChild);

  // Full-width header zone
  var headerZone = document.createElement('div');
  headerZone.className = 'aph-header-zone';
  headerZoneEls.forEach(function (el) { headerZone.appendChild(el); });
  main.appendChild(headerZone);

  // Two-column grid
  var grid = document.createElement('div');
  grid.className = 'aph-grid';

  var body = document.createElement('div');
  body.className = 'aph-body';
  bodyEls.forEach(function (el) { body.appendChild(el); });

  grid.appendChild(body);
  grid.appendChild(sidebar);
  main.appendChild(grid);

  // ─── 8. SCROLL BEHAVIOUR ─────────────────────────────────────────────────
  var fill  = document.getElementById('aphFill');
  var links = document.querySelectorAll('.aph-tl');

  window.addEventListener('scroll', function () {
    var st = window.scrollY || document.documentElement.scrollTop;
    var dh = document.documentElement.scrollHeight - window.innerHeight;

    if (fill && dh > 0) fill.style.width = Math.min(100, (st / dh) * 100).toFixed(1) + '%';

    if (links.length) {
      var active = '';
      realH2s.forEach(function (h) { if (h.getBoundingClientRect().top < 130) active = h.id; });
      links.forEach(function (a) { a.classList.toggle('aph-active', a.getAttribute('href') === '#' + active); });
    }
  }, { passive: true });

  // Smooth scroll
  links.forEach(function (a) {
    a.addEventListener('click', function (e) {
      var t = document.getElementById(this.getAttribute('href').slice(1));
      if (t) { e.preventDefault(); t.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
    });
  });

  // ─── 9. MARK AS INJECTED ─────────────────────────────────────────────────
  main.classList.add('aph-injected');

})();
