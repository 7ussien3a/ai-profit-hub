/**
 * AI Profit Hub - Floating AI Site Assistant v1.0 (2026)
 * Self-contained floating chat widget with serverless rule-based intelligence.
 */

(function () {
  'use strict';

  let allTools = [];
  let allPrompts = [];
  let prefix = "";

  // Static articles list for quick matching
  const ARTICLES_SHORT = [
    { title: "Google's New AI SEO Patent", url: "articles/google-ai-seo-patent-brand-optimization-2026.html" },
    { title: "Kling 3.0 Turbo vs LTX-2.3 Video", url: "articles/kling-3-turbo-ltx-2-video-ai-2026.html" },
    { title: "Google NotebookLM podcast Guide", url: "articles/google-notebooklm-ultimate-guide-2026.html" },
    { title: "Grok 2 & Grok 3 Ultimate Guide", url: "articles/grok-2-3-xai-llm-guide-2026.html" },
    { title: "Suno v4 vs Udio AI Music", url: "articles/suno-v4-vs-udio-ai-music-2026.html" },
    { title: "Apple intelligence Siri WWDC 2026", url: "articles/apple-intelligence-siri-wwdc-2026.html" },
    { title: "Intel Lunar Lake vs ARM CPUs", url: "articles/intel-lunar-lake-core-ultra-200v-efficiency-2026.html" }
  ];

  document.addEventListener("DOMContentLoaded", () => {
    determinePrefix();
    initAssistant();
    loadDatabases();
  });

  function determinePrefix() {
    const path = window.location.pathname;
    if (path.includes('/articles/') || path.includes('/reviews/') || path.includes('/compare/') || path.includes('/best-ai-tools/') || path.includes('/categories/') || path.includes('/companies/')) {
      prefix = "../";
    }
  }

  async function loadDatabases() {
    try {
      const [tRes, pRes] = await Promise.all([
        fetch(prefix + "data/tools.json"),
        fetch(prefix + "data/prompts.json")
      ]);
      if (tRes.ok) allTools = await tRes.json();
      if (pRes.ok) allPrompts = await pRes.json();
    } catch (e) {
      console.error("Assistant failed to pre-fetch databases:", e);
    }
  }

  function initAssistant() {
    if (document.getElementById("ai-site-assistant-wrapper")) return;

    // 1. Inject Styles
    const style = document.createElement("style");
    style.id = "assistant-widget-styles";
    style.textContent = `
      .assistant-widget-btn {
        position: fixed;
        bottom: 24px;
        right: 24px;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: var(--gradient-primary, linear-gradient(135deg, #6C63FF 0%, #00D4AA 100%));
        color: white;
        border: none;
        cursor: pointer;
        box-shadow: 0 8px 30px rgba(108, 99, 255, 0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      }
      .assistant-widget-btn:hover {
        transform: scale(1.08) translateY(-3px);
        box-shadow: 0 12px 40px rgba(108, 99, 255, 0.5);
      }
      .assistant-chat-window {
        position: fixed;
        bottom: 96px;
        right: 24px;
        width: 380px;
        height: 520px;
        background: var(--bg-card, #1A1F35);
        border: 1px solid var(--border, rgba(148, 163, 184, 0.1));
        border-radius: 16px;
        box-shadow: var(--shadow-lg, 0 10px 40px rgba(0,0,0,0.5));
        display: flex;
        flex-direction: column;
        z-index: 9999;
        overflow: hidden;
        transform: translateY(20px);
        opacity: 0;
        pointer-events: none;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      }
      .assistant-chat-window.open {
        transform: translateY(0);
        opacity: 1;
        pointer-events: auto;
      }
      .assistant-chat-header {
        padding: 16px 20px;
        background: var(--bg-secondary, #111827);
        border-bottom: 1px solid var(--border);
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      .assistant-chat-header h3 {
        margin: 0;
        font-size: 1.05rem;
        font-weight: 800;
        display: flex;
        align-items: center;
        gap: 8px;
        color: var(--text-primary);
      }
      .assistant-close-btn {
        background: transparent;
        border: none;
        color: var(--text-secondary);
        cursor: pointer;
        font-size: 1.2rem;
        transition: var(--transition);
      }
      .assistant-close-btn:hover {
        color: var(--text-primary);
      }
      .assistant-msg-log {
        flex-grow: 1;
        padding: 20px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 14px;
        background: rgba(10, 14, 26, 0.2);
      }
      .assistant-msg {
        max-width: 80%;
        padding: 10px 14px;
        border-radius: 12px;
        font-size: 0.88rem;
        line-height: 1.5;
      }
      .assistant-msg.agent {
        background: var(--bg-elevated, #252B45);
        color: var(--text-primary);
        align-self: flex-start;
        border-bottom-left-radius: 2px;
      }
      .assistant-msg.user {
        background: var(--primary);
        color: white;
        align-self: flex-end;
        border-bottom-right-radius: 2px;
      }
      .assistant-quick-replies {
        display: flex;
        gap: 8px;
        padding: 12px 20px;
        overflow-x: auto;
        background: var(--bg-card);
        border-top: 1px solid var(--border);
        white-space: nowrap;
      }
      .quick-reply-btn {
        background: var(--bg-elevated);
        border: 1px solid var(--border);
        color: var(--text-secondary);
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        cursor: pointer;
        transition: var(--transition);
      }
      .quick-reply-btn:hover {
        background: var(--primary);
        border-color: var(--primary-light);
        color: white;
      }
      .assistant-input-bar {
        padding: 14px 20px;
        background: var(--bg-secondary);
        border-top: 1px solid var(--border);
        display: flex;
        gap: 10px;
      }
      .assistant-input-bar input {
        flex-grow: 1;
        background: var(--bg-elevated);
        border: 1px solid var(--border);
        color: var(--text-primary);
        padding: 8px 14px;
        border-radius: 20px;
        font-size: 0.88rem;
        outline: none;
        transition: var(--transition);
      }
      .assistant-input-bar input:focus {
        border-color: var(--primary-light);
      }
      .assistant-send-btn {
        background: var(--primary);
        border: none;
        color: white;
        width: 34px;
        height: 34px;
        border-radius: 50%;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: var(--transition);
      }
      .assistant-send-btn:hover {
        background: var(--primary-light);
        transform: scale(1.05);
      }

      /* Pulse animation */
      .assistant-widget-btn::before {
        content: '';
        position: absolute;
        width: 100%;
        height: 100%;
        border-radius: 50%;
        background: inherit;
        opacity: 0.6;
        z-index: -1;
        animation: assistantPulse 2s infinite;
      }
      @keyframes assistantPulse {
        0% { transform: scale(1); opacity: 0.6; }
        100% { transform: scale(1.4); opacity: 0; }
      }

      @media(max-width: 480px) {
        .assistant-chat-window {
          width: calc(100% - 32px);
          height: calc(100% - 100px);
          bottom: 80px;
          right: 16px;
        }
        .assistant-widget-btn {
          bottom: 16px;
          right: 16px;
        }
      }
    `;
    document.head.appendChild(style);

    // 2. Build DOM elements
    const wrapper = document.createElement("div");
    wrapper.id = "ai-site-assistant-wrapper";
    wrapper.innerHTML = `
      <button class="assistant-widget-btn" id="assistantWidgetBtn" aria-label="Open AI Assistant">
        <i data-lucide="message-square" style="width:26px; height:26px;"></i>
      </button>
      
      <div class="assistant-chat-window" id="assistantChatWindow">
        <div class="assistant-chat-header">
          <h3><span style="font-size:1.15rem;">⚡</span> AI Hub Assistant</h3>
          <button class="assistant-close-btn" id="assistantCloseBtn">&times;</button>
        </div>
        
        <div class="assistant-msg-log" id="assistantMsgLog">
          <div class="assistant-msg agent">
            Hello! I am your AI Profit Hub assistant. Ask me anything about:
            <ul style="margin: 8px 0 0 16px; padding:0;">
              <li>Finding best AI tools</li>
              <li>Prompts & instructions</li>
              <li>Comparing ChatGPT, Claude or Gemini</li>
              <li>Bookmarking and Dashboard</li>
            </ul>
          </div>
        </div>

        <div class="assistant-quick-replies">
          <button class="quick-reply-btn" data-query="recommend writing tools">✍️ Writing Tools</button>
          <button class="quick-reply-btn" data-query="recommend coding tools">💻 Coding Tools</button>
          <button class="quick-reply-btn" data-query="compare chatgpt vs claude">⚖️ ChatGPT vs Claude</button>
          <button class="quick-reply-btn" data-query="how do I save favorites">⭐ Bookmarks Info</button>
        </div>

        <div class="assistant-input-bar">
          <input type="text" id="assistantInput" placeholder="Type your question..." autocomplete="off">
          <button class="assistant-send-btn" id="assistantSendBtn">
            <i data-lucide="send" style="width:16px; height:16px;"></i>
          </button>
        </div>
      </div>
    `;

    document.body.appendChild(wrapper);
    if (typeof lucide !== "undefined") {
      lucide.createIcons();
    }

    // 3. Register Event Listeners
    const widgetBtn = document.getElementById("assistantWidgetBtn");
    const chatWindow = document.getElementById("assistantChatWindow");
    const closeBtn = document.getElementById("assistantCloseBtn");
    const sendBtn = document.getElementById("assistantSendBtn");
    const inputField = document.getElementById("assistantInput");

    widgetBtn.addEventListener("click", () => {
      chatWindow.classList.toggle("open");
      if (chatWindow.classList.contains("open")) {
        inputField.focus();
        // Change icon to chevron down
        widgetBtn.innerHTML = '<i data-lucide="chevron-down" style="width:26px; height:26px;"></i>';
      } else {
        widgetBtn.innerHTML = '<i data-lucide="message-square" style="width:26px; height:26px;"></i>';
      }
      if (typeof lucide !== "undefined") lucide.createIcons();
    });

    closeBtn.addEventListener("click", () => {
      chatWindow.classList.remove("open");
      widgetBtn.innerHTML = '<i data-lucide="message-square" style="width:26px; height:26px;"></i>';
      if (typeof lucide !== "undefined") lucide.createIcons();
    });

    sendBtn.addEventListener("click", handleUserSubmit);
    inputField.addEventListener("keydown", (e) => {
      if (e.key === "Enter") handleUserSubmit();
    });

    // Quick replies
    document.querySelectorAll(".quick-reply-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const query = btn.dataset.query;
        appendMessage(query, "user");
        processQuery(query);
      });
    });
  }

  function appendMessage(text, sender) {
    const log = document.getElementById("assistantMsgLog");
    if (!log) return;

    const msg = document.createElement("div");
    msg.className = `assistant-msg ${sender}`;
    msg.innerHTML = text;
    log.appendChild(msg);

    // Scroll to bottom
    log.scrollTop = log.scrollHeight;
  }

  function handleUserSubmit() {
    const input = document.getElementById("assistantInput");
    if (!input) return;
    const val = input.value.trim();
    if (!val) return;

    appendMessage(val, "user");
    input.value = "";

    // Show typing state
    setTimeout(() => {
      processQuery(val);
    }, 400);
  }

  /* ==========================================================================
     Smart NLP/Keyword Matching Engine
     ========================================================================== */
  function processQuery(query) {
    const q = query.toLowerCase().trim();

    // 1. Check for Comparison questions
    if (q.includes("compare") || q.includes("vs") || q.includes("versus")) {
      let match = null;
      if (q.includes("claude") && q.includes("chatgpt")) {
        match = { title: "ChatGPT vs Claude", url: "compare/chatgpt-vs-claude.html", summary: "ChatGPT Plus has DALL-E 3 and Python sandbox, while Claude 3.5 Sonnet is better for writing nuance and logic debugging." };
      } else if (q.includes("gemini") && q.includes("chatgpt")) {
        match = { title: "ChatGPT vs Gemini", url: "compare/chatgpt-vs-gemini.html", summary: "Gemini Advanced has continuous live speech and integration with Docs, while ChatGPT Plus excels at Python and plugins." };
      } else if (q.includes("claude") && q.includes("gemini")) {
        match = { title: "Claude vs Gemini", url: "compare/claude-vs-gemini.html", summary: "Claude excels at precise coding and professional text. Gemini has a massive 2M context window." };
      }

      if (match) {
        appendMessage(`
          <strong>⚖️ ${match.title} Side-by-Side:</strong><br>
          ${match.summary}<br><br>
          Read my full analysis here:<br>
          👉 <a href="${prefix}${match.url}" style="color:var(--accent); font-weight:700;">Full VS comparison</a>
        `, "agent");
        return;
      }
    }

    // 2. Check for tool recommendations by category
    const categories = ["writing", "coding", "design", "search", "video"];
    let matchedCat = null;
    categories.forEach(cat => {
      if (q.includes(cat) || (cat === "design" && q.includes("image")) || (cat === "writing" && q.includes("text"))) {
        matchedCat = cat;
      }
    });

    if (matchedCat) {
      const matchTools = allTools.filter(t => t.category.toLowerCase() === matchedCat.toLowerCase());
      if (matchTools.length > 0) {
        const listStr = matchTools.slice(0, 3).map(t => `<li>${t.emoji || "🤖"} <strong>${t.name}</strong> (${t.pricingType}) - ${t.tagline}</li>`).join("");
        appendMessage(`
          <strong>💻 Recommended ${matchedCat.toUpperCase()} tools:</strong><br>
          Based on my tests, here are the top tools:<br>
          <ul style="margin: 8px 0 8px 16px; padding:0;">${listStr}</ul>
          View the full list in the:<br>
          👉 <a href="${prefix}best-ai-tools/index.html" style="color:var(--accent); font-weight:700;">AI Tools Directory</a>
        `, "agent");
        return;
      }
    }

    // 3. Search for specific tool name
    let matchedTool = null;
    for (const tool of allTools) {
      if (q.includes(tool.name.toLowerCase())) {
        matchedTool = tool;
        break;
      }
    }

    if (matchedTool) {
      appendMessage(`
        <strong>${matchedTool.emoji || "🤖"} ${matchedTool.name} Detail:</strong><br>
        Developed by <strong>${matchedTool.developer}</strong>. Pricing is <strong>${matchedTool.pricingDetail}</strong>.<br><br>
        <em>"${matchedTool.desc.substring(0, 120)}..."</em><br><br>
        👉 <a href="${matchedTool.url}" target="_blank" rel="noopener" style="color:var(--accent); font-weight:700;">Visit ${matchedTool.name}</a>
      `, "agent");
      return;
    }

    // 4. Save bookmarks info
    if (q.includes("save") || q.includes("bookmark") || q.includes("favorite") || q.includes("dashboard")) {
      appendMessage(`
        <strong>⭐ Bookmarks & Dashboard Info:</strong><br>
        You can save any tool in the Directory or Prompt in the Library by clicking the star icon.<br><br>
        Also, you can bookmark any article by clicking the bookmark button next to the title. All bookmarks are saved locally and accessible on:<br>
        👉 <a href="${prefix}dashboard.html" style="color:var(--accent); font-weight:700;">My AI Dashboard</a>
      `, "agent");
      return;
    }

    // 5. Check for Prompt questions
    if (q.includes("prompt") || q.includes("instructions") || q.includes("template")) {
      const matchPrompts = allPrompts.slice(0, 2);
      const listStr = matchPrompts.map(p => `<li>⚡ <strong>${p.title}</strong> - ${p.desc}</li>`).join("");
      appendMessage(`
        <strong>⚡ Prompt Templates:</strong><br>
        We have a library of production-ready prompts:<br>
        <ul style="margin: 8px 0 8px 16px; padding:0;">${listStr}</ul>
        Copy and run them from the library page:<br>
        👉 <a href="${prefix}prompts-library.html" style="color:var(--accent); font-weight:700;">Prompts Library</a>
      `, "agent");
      return;
    }

    // 6. Article search match
    let matchedArticle = null;
    for (const art of ARTICLES_SHORT) {
      if (q.includes(art.title.toLowerCase()) || q.includes("guide") || q.includes("seo") || q.includes("notebooklm")) {
        matchedArticle = art;
        break;
      }
    }

    if (matchedArticle) {
      appendMessage(`
        <strong>📰 Related Guide:</strong><br>
        Here is a relevant resource on that topic:<br>
        👉 <a href="${prefix}${matchedArticle.url}" style="color:var(--accent); font-weight:700;">${matchedArticle.title}</a>
      `, "agent");
      return;
    }

    // 7. General fallback response
    appendMessage(`
      I'm not sure how to answer that exactly. Try asking me to:<br>
      - <em>"Recommend coding tools"</em><br>
      - <em>"Compare Claude and ChatGPT"</em><br>
      - <em>"How do I bookmark items?"</em><br>
      - <em>"Find prompt templates"</em><br><br>
      Or search through all tutorials using our <a href="${prefix}search.html" style="color:var(--accent); font-weight:700;">Smart Search</a>!
    `, "agent");
  }

})();
