/**
 * Related Articles – "You May Also Like"
 * Automatically injects 3 random article cards before the <footer>.
 * Fully self-contained: styles are injected via JS, no external CSS needed.
 */
(function () {
  'use strict';

  /* ── Article catalogue ─────────────────────────────────────────────── */
  var articles = [
    {
      title: 'Intel Lunar Lake: How Intel Beat ARM',
      url: '/articles/intel-lunar-lake-core-ultra-200v-efficiency-2026.html',
      image: '/images/intel-lunar-lake.png',
      tag: '💻 Hardware',
      date: 'June 19 2026'
    },
    {
      title: 'Huawei Ascend 950DT: Replacing NVIDIA',
      url: '/articles/huawei-ascend-950dt-china-ai-chip-nvidia-alternative-2026.html',
      image: '/images/huawei-ascend-chip.png',
      tag: '🇨🇳 China AI',
      date: 'June 19 2026'
    },
    {
      title: 'The Ultimate 2026 CPU Comparison',
      url: '/articles/ultimate-2026-cpu-comparison-apple-m5-lunar-lake-snapdragon-ryzen.html',
      image: '/images/cpu-comparison-2026.png',
      tag: '⚖️ Compare',
      date: 'June 19 2026'
    },
    {
      title: 'Xcode 27 Dual-Engine AI Coding Agents',
      url: '/articles/xcode-27-dual-engine-ai-coding-agents-2026.html',
      image: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=400&q=80',
      tag: '🍎 Apple',
      date: 'June 18 2026'
    },
    {
      title: 'Apple Reinvents Siri: WWDC 2026',
      url: '/articles/apple-intelligence-siri-wwdc-2026.html',
      image: 'https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=400&q=80',
      tag: '🍎 Apple',
      date: 'June 17 2026'
    },
    {
      title: 'Anthropic Raises $65 Billion',
      url: '/articles/anthropic-65-billion-fable-5-model-2026.html',
      image: 'https://images.unsplash.com/photo-1559526324-593bc073d938?w=400&q=80',
      tag: '💰 Business',
      date: 'June 17 2026'
    },
    {
      title: 'Google Gemma 4 Local AI',
      url: '/articles/google-gemma-4-local-ai-laptop-2026.html',
      image: '/images/google-gemma-local-ai.png',
      tag: '🖥️ Local AI',
      date: 'June 17 2026'
    },
    {
      title: 'Gemini 3.5 Live Translate',
      url: '/articles/google-gemini-3-5-live-translate-20260615.html',
      image: '/images/gemini-live-translate.png',
      tag: '🤖 AI Tools',
      date: 'June 15 2026'
    },
    {
      title: 'OpenAI Investigation',
      url: '/articles/openai-faces-investigation-from-state-attorneys-general-20260613.html',
      image: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&q=80',
      tag: '🤖 AI Tools',
      date: 'June 13 2026'
    },
    {
      title: 'Anthropic Safety Backfired',
      url: '/articles/anthropic8217s-safety-warnings-may-have-just-backfired-20260613.html',
      image: 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&q=80',
      tag: '🤖 AI Tools',
      date: 'June 13 2026'
    },
    {
      title: 'Gemini Omni Video',
      url: '/articles/gemini-omni-video-revolution.html',
      image: 'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=400&q=80',
      tag: '🎬 Video AI',
      date: 'May 29 2026'
    },
    {
      title: 'KPMG Claude',
      url: '/articles/kpmg-claude-276000-employees.html',
      image: 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=400&q=80',
      tag: '🏢 Enterprise',
      date: 'May 29 2026'
    },
    {
      title: 'Samsung HBM4E',
      url: '/articles/samsung-hbm4e-ai-memory-chips.html',
      image: '/images/cpu-comparison-2026.png',
      tag: '🔧 Hardware',
      date: 'May 29 2026'
    },
    {
      title: 'DuckDuckGo vs Google',
      url: '/articles/duckduckgo-vs-google-ai-search.html',
      image: 'https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=400&q=80',
      tag: '🔍 Search',
      date: 'May 27 2026'
    },
    {
      title: 'NVIDIA Record Revenue',
      url: '/articles/nvidia-record-revenue-ai-dominance.html',
      image: 'https://images.unsplash.com/photo-1639322537228-f710d846310a?w=400&q=80',
      tag: '💰 Business',
      date: 'May 27 2026'
    },
    {
      title: 'GPT-5 vs Claude 4',
      url: '/articles/gpt-5-vs-claude-4.html',
      image: 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400&q=80',
      tag: '⚖️ Compare',
      date: 'May 2026'
    },
    {
      title: 'Best Free AI Tools Students',
      url: '/articles/best-free-ai-tools-students.html',
      image: '/images/ai-tools-students.png',
      tag: '🎓 Education',
      date: 'May 2026'
    },
    {
      title: 'ChatGPT Prompts Productivity',
      url: '/articles/chatgpt-prompts-productivity.html',
      image: 'https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b?w=400&q=80',
      tag: '💡 Productivity',
      date: 'May 2026'
    },
    {
      title: 'Anthropic Claude Surpasses OpenAI',
      url: '/articles/anthropic-claude-surpasses-openai.html',
      image: 'https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=400&q=80',
      tag: '🤖 AI Tools',
      date: 'May 2026'
    }
  ];

  /* ── Helpers ────────────────────────────────────────────────────────── */

  /** Fisher-Yates shuffle (returns new array) */
  function shuffle(arr) {
    var a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var tmp = a[i];
      a[i] = a[j];
      a[j] = tmp;
    }
    return a;
  }

  /** Check if a URL matches the current page */
  function isCurrentArticle(articleUrl) {
    var path = window.location.pathname;
    // Normalise: remove trailing slash, compare
    var normPath = path.replace(/\/index\.html$/, '').replace(/\/$/, '');
    var normUrl  = articleUrl.replace(/\/index\.html$/, '').replace(/\/$/, '');
    return normPath === normUrl || path.endsWith(articleUrl);
  }

  /* ── Inject styles ──────────────────────────────────────────────────── */
  function injectStyles() {
    if (document.getElementById('related-articles-styles')) return;

    var css = [
      '/* ── Related Articles Section ── */',
      '.related-articles-section {',
      '  max-width: 1200px;',
      '  margin: 0 auto;',
      '  padding: 60px 20px 40px;',
      '  opacity: 0;',
      '  transform: translateY(30px);',
      '  animation: relatedFadeIn 0.6s ease forwards;',
      '}',
      '',
      '@keyframes relatedFadeIn {',
      '  to { opacity: 1; transform: translateY(0); }',
      '}',
      '',
      '.related-articles-section .related-title {',
      '  font-size: 1.75rem;',
      '  font-weight: 700;',
      '  color: var(--text-primary, #ffffff);',
      '  text-align: center;',
      '  margin-bottom: 8px;',
      '}',
      '',
      '.related-articles-section .related-underline {',
      '  width: 100px;',
      '  height: 4px;',
      '  margin: 0 auto 40px;',
      '  border-radius: 4px;',
      '  background: linear-gradient(90deg, #6C63FF, #a78bfa, #6C63FF);',
      '  background-size: 200% 100%;',
      '  animation: relatedGradientShift 3s ease infinite;',
      '}',
      '',
      '@keyframes relatedGradientShift {',
      '  0%,100% { background-position: 0% 50%; }',
      '  50%     { background-position: 100% 50%; }',
      '}',
      '',
      '.related-articles-grid {',
      '  display: grid;',
      '  grid-template-columns: repeat(3, 1fr);',
      '  gap: 24px;',
      '}',
      '',
      '.related-card {',
      '  background: var(--bg-card, #1a1a2e);',
      '  border: 1px solid var(--border, rgba(255,255,255,0.08));',
      '  border-radius: 16px;',
      '  overflow: hidden;',
      '  transition: transform 0.3s ease, box-shadow 0.3s ease;',
      '  display: flex;',
      '  flex-direction: column;',
      '}',
      '',
      '.related-card:hover {',
      '  transform: translateY(-6px);',
      '  box-shadow: 0 12px 32px rgba(108,99,255,0.18);',
      '}',
      '',
      '.related-card-img-wrapper {',
      '  position: relative;',
      '  width: 100%;',
      '  height: 180px;',
      '  overflow: hidden;',
      '}',
      '',
      '.related-card-img-wrapper img {',
      '  width: 100%;',
      '  height: 100%;',
      '  object-fit: cover;',
      '  transition: transform 0.4s ease;',
      '}',
      '',
      '.related-card:hover .related-card-img-wrapper img {',
      '  transform: scale(1.06);',
      '}',
      '',
      '.related-card-body {',
      '  padding: 16px 18px 20px;',
      '  display: flex;',
      '  flex-direction: column;',
      '  flex: 1;',
      '}',
      '',
      '.related-card-tag {',
      '  display: inline-block;',
      '  background: var(--bg-elevated, rgba(108,99,255,0.12));',
      '  color: var(--primary-light, #a78bfa);',
      '  font-size: 0.75rem;',
      '  font-weight: 600;',
      '  padding: 4px 10px;',
      '  border-radius: 20px;',
      '  margin-bottom: 10px;',
      '  width: fit-content;',
      '}',
      '',
      '.related-card-title {',
      '  font-size: 1.05rem;',
      '  font-weight: 600;',
      '  color: var(--text-primary, #ffffff);',
      '  line-height: 1.4;',
      '  margin: 0 0 auto;',
      '  text-decoration: none;',
      '  transition: color 0.25s ease;',
      '}',
      '',
      '.related-card-title:hover {',
      '  color: var(--primary-light, #a78bfa);',
      '}',
      '',
      '.related-card-date {',
      '  font-size: 0.8rem;',
      '  color: var(--text-secondary, #8888aa);',
      '  margin-top: 12px;',
      '}',
      '',
      '/* ── Responsive ── */',
      '@media (max-width: 900px) {',
      '  .related-articles-grid {',
      '    grid-template-columns: repeat(2, 1fr);',
      '  }',
      '}',
      '',
      '@media (max-width: 600px) {',
      '  .related-articles-grid {',
      '    grid-template-columns: 1fr;',
      '  }',
      '  .related-articles-section .related-title {',
      '    font-size: 1.4rem;',
      '  }',
      '}'
    ].join('\n');

    var style = document.createElement('style');
    style.id = 'related-articles-styles';
    style.textContent = css;
    document.head.appendChild(style);
  }

  /* ── Build the section HTML ─────────────────────────────────────────── */
  function buildSection(picks) {
    var section = document.createElement('section');
    section.className = 'related-articles-section';
    section.setAttribute('aria-label', 'Related articles');

    var heading = '<h2 class="related-title">📚 You May Also Like</h2>' +
                  '<div class="related-underline"></div>';

    var cards = picks.map(function (a) {
      return (
        '<article class="related-card">' +
          '<div class="related-card-img-wrapper">' +
            '<img src="' + a.image + '" alt="' + a.title + '" loading="lazy" />' +
          '</div>' +
          '<div class="related-card-body">' +
            '<span class="related-card-tag">' + a.tag + '</span>' +
            '<a href="' + a.url + '" class="related-card-title">' + a.title + '</a>' +
            '<span class="related-card-date">' + a.date + '</span>' +
          '</div>' +
        '</article>'
      );
    }).join('');

    section.innerHTML = heading +
      '<div class="related-articles-grid">' + cards + '</div>';

    return section;
  }

  /* ── Main ───────────────────────────────────────────────────────────── */
  function init() {
    var footer = document.querySelector('footer');
    if (!footer) return; // Only run on pages with a <footer>

    // Filter out the current article
    var candidates = articles.filter(function (a) {
      return !isCurrentArticle(a.url);
    });

    if (candidates.length === 0) return;

    // Pick up to 3 random articles
    var picks = shuffle(candidates).slice(0, 3);

    injectStyles();
    var section = buildSection(picks);
    footer.parentNode.insertBefore(section, footer);
  }

  // Run when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
