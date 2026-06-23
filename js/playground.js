/**
 * AI Profit Hub - AI Playground Engine v1.0 (2026)
 * Handles client-side interactive widgets.
 */

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initToolFinder();
  initPromptOptimizer();
  initModelRecommender();
  initCostCalculator();
});

/* ==========================================================================
   1. Tab Navigation Logic
   ========================================================================== */
function initTabs() {
  const tabs = document.querySelectorAll(".play-tab-btn");
  const panels = document.querySelectorAll(".playground-panel");

  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      // Deactivate all tabs
      tabs.forEach(t => t.classList.remove("active"));
      // Hide all panels
      panels.forEach(p => p.classList.remove("active"));

      // Activate current
      tab.classList.add("active");
      const targetId = tab.dataset.target;
      const targetPanel = document.getElementById(targetId);
      if (targetPanel) {
        targetPanel.classList.add("active");
      }

      // Re-initialize Lucide icons in case new elements are visible
      if (typeof lucide !== "undefined") {
        lucide.createIcons();
      }
    });
  });
}

/* ==========================================================================
   2. AI Tool Finder Logic
   ========================================================================== */
function initToolFinder() {
  const findBtn = document.getElementById("findToolsBtn");
  if (!findBtn) return;

  findBtn.addEventListener("click", async () => {
    const goal = document.getElementById("finderGoal").value;
    const budget = document.getElementById("finderBudget").value;
    const skill = document.getElementById("finderSkill").value;
    const resultBox = document.getElementById("finderResult");
    const grid = document.getElementById("finderResultsGrid");

    if (!grid || !resultBox) return;

    try {
      findBtn.disabled = true;
      findBtn.innerHTML = '<i data-lucide="loader-2" class="animate-spin"></i> Finding tools...';
      if (typeof lucide !== "undefined") lucide.createIcons();

      const response = await fetch("data/tools.json");
      if (!response.ok) throw new Error("Could not load tools database.");
      const tools = await response.json();

      // Filter tools
      const matches = tools.filter(tool => {
        // Category Goal Match
        const matchGoal = tool.category.toLowerCase() === goal.toLowerCase();

        // Budget Match
        let matchBudget = true;
        if (budget !== "all") {
          matchBudget = tool.pricingType.toLowerCase() === budget.toLowerCase();
        }

        // Skill Match (heuristic rating logic)
        let matchSkill = true;
        if (skill === "beginner") {
          // Beginners prefer highly rated tools with clear interfaces
          matchSkill = tool.rating >= 4.3;
        } else if (skill === "expert") {
          // Experts want developer-friendly or highly advanced tools
          const isDevTool = ["openai", "anthropic", "google", "assemblyai", "elevenlabs", "github"].includes(tool.developer.toLowerCase()) || 
                             tool.desc.toLowerCase().includes("api") || 
                             tool.desc.toLowerCase().includes("developer") || 
                             tool.category === "coding";
          matchSkill = isDevTool || tool.rating >= 4.5;
        }

        return matchGoal && matchBudget && matchSkill;
      });

      // Sort matches by rating descending
      matches.sort((a, b) => b.rating - a.rating);

      // Render results
      if (matches.length === 0) {
        grid.innerHTML = `
          <div style="grid-column: 1/-1; padding: 30px; text-align: center; color: var(--text-secondary);">
            <p>No exact tools found matching all your constraints.</p>
            <p style="font-size: 0.85rem; margin-top: 8px;">Try selecting "Show All Pricing Types" or choosing a broader objective.</p>
          </div>
        `;
      } else {
        grid.innerHTML = matches.slice(0, 6).map(tool => {
          let badgeClass = "badge-paid";
          if (tool.pricingType.toLowerCase() === "free") badgeClass = "badge-free";
          if (tool.pricingType.toLowerCase() === "freemium") badgeClass = "badge-freemium";

          const husseinBadge = tool.husseinPick ? 
            `<span style="position: absolute; top: 12px; right: 12px; font-size: 0.7rem; background: var(--accent); color: #04120f; font-weight: 800; padding: 2px 8px; border-radius: 20px;">Hussein Pick</span>` : '';

          return `
            <div class="finder-tool-card" style="position: relative;">
              ${husseinBadge}
              <div>
                <div class="finder-tool-header">
                  <div class="finder-tool-emoji">${tool.emoji || "🤖"}</div>
                  <div>
                    <h4 class="finder-tool-name">${tool.name}</h4>
                    <span style="font-size: 0.75rem; color: var(--text-muted);">by ${tool.developer}</span>
                  </div>
                </div>
                <p class="finder-tool-tagline">${tool.tagline}</p>
              </div>
              <div class="finder-tool-meta">
                <span class="finder-tool-rating">★ ${tool.rating.toFixed(1)}</span>
                <span class="finder-tool-price ${badgeClass}" style="font-size:0.72rem; border-radius:20px; font-weight:700;">${tool.pricingType}</span>
                <a href="${tool.url}" target="_blank" rel="noopener" style="font-size: 0.8rem; font-weight: 700; color: var(--primary-light);">Visit →</a>
              </div>
            </div>
          `;
        }).join("");
      }

      resultBox.classList.add("active");
    } catch (error) {
      console.error(error);
      grid.innerHTML = '<div style="grid-column: 1/-1; color: #ef4444;">Failed to query tools database. Please try again.</div>';
    } finally {
      findBtn.disabled = false;
      findBtn.innerHTML = '<i data-lucide="sparkles"></i> Find Best Tools';
      if (typeof lucide !== "undefined") lucide.createIcons();
    }
  });
}

/* ==========================================================================
   3. Prompt Optimizer Logic
   ========================================================================== */
function initPromptOptimizer() {
  const optimizeBtn = document.getElementById("optimizePromptBtn");
  if (!optimizeBtn) return;

  optimizeBtn.addEventListener("click", () => {
    const baseIdea = document.getElementById("promptIdea").value.trim();
    const role = document.getElementById("promptRole").value;
    const tone = document.getElementById("promptTone").value;
    const resultBox = document.getElementById("prompterResult");
    const output = document.getElementById("outputOptimizedPrompt");

    if (!baseIdea) {
      alert("Please enter a basic prompt idea first!");
      document.getElementById("promptIdea").focus();
      return;
    }

    // Build constraints list
    const constraints = [];
    if (document.getElementById("constraintMarkdown").checked) {
      constraints.push("- Format all final answers in clean, semantic Markdown layout (using headers, code blocks, bold text, etc.).");
    }
    if (document.getElementById("constraintBullets").checked) {
      constraints.push("- Present summaries, workflows, and list items in structured bullet points instead of dense paragraphs.");
    }
    if (document.getElementById("constraintNoJargon").checked) {
      constraints.push("- Avoid corporate jargon, redundant fluff, and marketing clichés. Be concise, direct, and factual.");
    }
    if (document.getElementById("constraintExamples").checked) {
      constraints.push("- Provide concrete code snippets, text examples, or visual structure templates to illustrate your points.");
    }

    const constraintsStr = constraints.length > 0 ? "\n" + constraints.join("\n") : "- No specific formatting constraints.";

    // Construct optimized prompt
    const engineeredPrompt = `# SYSTEM PERSONA & ROLE
You are acting as an expert ${role}. 
Your communication style must be ${tone}, demonstrating deep subject matter expertise and accuracy.

# CONTEXT & PRIMARY OBJECTIVE
The user's goal is to achieve the following:
"${baseIdea}"

# INPUT VARIABLES & PARAMETERS
To deliver the best results, analyze if the user's input needs default assumptions, or ask the user to provide details for:
1. [Target Audience / End User Profile]
2. [Industry / Domain Context]
3. [Required length or specific scope]

# RULES & CONSTRAINTS${constraintsStr}

# EXECUTION WORKFLOW
Please process this request step-by-step:
1. **Goal Analysis:** Identify what the user wants to achieve and target persona constraints.
2. **First Draft Formulation:** Draft the requested asset aligning strictly with the formatting constraints.
3. **Internal Review:** Verify formatting (e.g. Markdown headers, no buzzwords).
4. **Final Delivery:** Deliver clean output. Introduce your final answer with: "Here is your optimized output:"

# OUTPUT FORMAT
Generate the structured output matching the constraints above.`;

    output.value = engineeredPrompt;
    resultBox.classList.add("active");
    output.scrollIntoView({ behavior: "smooth", block: "nearest" });
  });

  // Copy button listener
  const copyBtn = document.getElementById("copyPlaygroundPromptBtn");
  if (copyBtn) {
    copyBtn.addEventListener("click", () => {
      const text = document.getElementById("outputOptimizedPrompt").value;
      if (!text) return;

      navigator.clipboard.writeText(text).then(() => {
        const origText = copyBtn.innerHTML;
        copyBtn.innerHTML = '<i data-lucide="check" style="width: 14px; height: 14px;"></i> Copied!';
        if (typeof lucide !== "undefined") lucide.createIcons();

        setTimeout(() => {
          copyBtn.innerHTML = origText;
          if (typeof lucide !== "undefined") lucide.createIcons();
        }, 2000);
      });
    });
  }
}

/* ==========================================================================
   4. LLM Model Recommender Logic
   ========================================================================== */
const MODELS_DATA = {
  "claude-sonnet": {
    name: "Claude 3.5 Sonnet",
    developer: "Anthropic",
    rating: "4.9/5",
    pricing: "$3.00 / M input, $15.00 / M output",
    emoji: "🧠",
    features: [
      "200K Context Window (superb for big files)",
      "Unmatched coding logic and bug explanations",
      "Nuanced, creative writing tone",
      "Live file workspace (Artifacts)"
    ],
    reason: "Best-in-class reasoning, coding, and long-document processing. If quality and accuracy are paramount, Claude 3.5 Sonnet is the absolute developer standard."
  },
  "gpt-4o": {
    name: "GPT-4o",
    developer: "OpenAI",
    rating: "4.8/5",
    pricing: "$2.50 / M input, $10.00 / M output",
    emoji: "⚡",
    features: [
      "128K Context Window",
      "Native Python sandbox code interpreter",
      "High token speeds & real-time advanced voice",
      "Excellent multi-modal reasoning"
    ],
    reason: "Best for all-around agentic workflows, Python code execution, and fast conversational interfaces. Slightly cheaper than Sonnet with better math sandbox tools."
  },
  "gemini-pro": {
    name: "Gemini 1.5 Pro",
    developer: "Google",
    rating: "4.7/5",
    pricing: "$1.25 / M input (<128K), $5.00 / M output",
    emoji: "🪐",
    features: [
      "Massive 2-Million Token Context window",
      "Exceptional multi-modal input (videos, full codebases)",
      "Native integration with Google Cloud & Docs",
      "Extremely affordable high-tier pricing"
    ],
    reason: "If you need to analyze entire repositories, long video files, or books, Gemini 1.5 Pro has an unmatched context window at half the price of GPT-4o."
  },
  "gpt-4o-mini": {
    name: "GPT-4o mini",
    developer: "OpenAI",
    rating: "4.6/5",
    pricing: "$0.15 / M input, $0.60 / M output",
    emoji: "🐜",
    features: [
      "128K Context Window",
      "Incredibly fast latency times",
      "Extremely cost-effective for large scale runs",
      "Highly capable function calling"
    ],
    reason: "Perfect for high-volume, low-cost tasks like simple chats, classifications, routing, and summary tasks where speed is key and quality is balanced."
  },
  "gemini-flash": {
    name: "Gemini 1.5 Flash",
    developer: "Google",
    rating: "4.5/5",
    pricing: "$0.075 / M input (<128K), $0.30 / M output",
    emoji: "⚡",
    features: [
      "1-Million Token Context window",
      "Blazing fast speeds",
      "Cheapest sub-dollar model on the market",
      "Multi-modal video analysis support"
    ],
    reason: "The ultimate budget king. Offers a massive 1M context window and fast response times at a fraction of a cent. Ideal for summarization at scale."
  },
  "claude-haiku": {
    name: "Claude 3.5 Haiku",
    developer: "Anthropic",
    rating: "4.5/5",
    pricing: "$0.80 / M input, $4.00 / M output",
    emoji: "🕊️",
    features: [
      "200K Context Window",
      "Fast response times",
      "Strong coding syntax capability",
      "Consistent JSON output structuring"
    ],
    reason: "Offers Claude's logical reasoning and large context in a lightweight package. Good for data structuring and code automation pipelines."
  }
};

function initModelRecommender() {
  const recBtn = document.getElementById("recommendBtn");
  if (!recBtn) return;

  recBtn.addEventListener("click", () => {
    const task = document.getElementById("recTaskType").value;
    const priority = document.getElementById("recPriority").value;
    const context = document.getElementById("recContext").value;
    const resultBox = document.getElementById("recommenderResult");
    const outputGrid = document.getElementById("recommenderOutputGrid");

    if (!outputGrid || !resultBox) return;

    let targetModelKey = "gpt-4o"; // Default fallbacks

    // Decision Logic
    if (context === "large") {
      targetModelKey = priority === "accuracy" ? "gemini-pro" : "gemini-flash";
    } else if (priority === "cost") {
      targetModelKey = task === "reasoning" || task === "coding" ? "claude-haiku" : "gemini-flash";
    } else if (priority === "speed") {
      targetModelKey = "gpt-4o-mini";
    } else if (priority === "accuracy") {
      targetModelKey = task === "coding" || task === "reasoning" ? "claude-sonnet" : "gpt-4o";
    } else { // Balanced
      targetModelKey = task === "coding" ? "claude-sonnet" : "gpt-4o-mini";
    }

    const model = MODELS_DATA[targetModelKey];

    outputGrid.innerHTML = `
      <div class="rec-icon">${model.emoji}</div>
      <div class="rec-body">
        <h3>${model.name} (${model.developer})</h3>
        <p style="font-size:0.8rem; color:var(--text-secondary); margin-bottom:12px;">
          <strong>Pricing:</strong> ${model.pricing} | <strong>Rating:</strong> ${model.rating}
        </p>
        <p class="rec-reason">${model.reason}</p>
        <strong style="font-size:0.85rem; color:var(--text-primary); display:block; margin-bottom:8px;">Key Features:</strong>
        <ul class="rec-bullet-list">
          ${model.features.map(f => `<li>${f}</li>`).join("")}
        </ul>
      </div>
    `;

    resultBox.classList.add("active");
    if (typeof lucide !== "undefined") lucide.createIcons();
    resultBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
  });
}

/* ==========================================================================
   5. Token & Cost Calculator Logic
   ========================================================================== */
const RATE_CARDS = {
  "gpt-4o": { name: "GPT-4o", input: 2.50, output: 10.00 },
  "gpt-4o-mini": { name: "GPT-4o mini", input: 0.15, output: 0.60 },
  "claude-sonnet": { name: "Claude 3.5 Sonnet", input: 3.00, output: 15.00 },
  "claude-haiku": { name: "Claude 3.5 Haiku", input: 0.80, output: 4.00 },
  "gemini-pro": { name: "Gemini 1.5 Pro", input: 1.25, output: 5.00 },
  "gemini-flash": { name: "Gemini 1.5 Flash", input: 0.075, output: 0.30 }
};

function initCostCalculator() {
  const calcBtn = document.getElementById("calculateCostBtn");
  if (!calcBtn) return;

  calcBtn.addEventListener("click", () => {
    const selectedModel = document.getElementById("calcModel").value;
    const unitType = document.getElementById("calcUnit").value;
    let inputVal = parseFloat(document.getElementById("calcInputVolume").value) || 0;
    let outputVal = parseFloat(document.getElementById("calcOutputVolume").value) || 0;

    const resultBox = document.getElementById("calculatorResult");
    const chartWrapper = document.getElementById("calculatorChartWrapper");

    if (!resultBox || !chartWrapper) return;

    // Convert words to tokens if required (1 word = 1.33 tokens)
    if (unitType === "words") {
      inputVal = Math.round(inputVal * 1.33);
      outputVal = Math.round(outputVal * 1.33);
    }

    // Rates of active model
    const rates = RATE_CARDS[selectedModel];
    const inputCost = (inputVal / 1000000) * rates.input;
    const outputCost = (outputVal / 1000000) * rates.output;
    const totalCost = inputCost + outputCost;

    // Render stats
    document.getElementById("calcValInput").textContent = `$${inputCost.toFixed(4)}`;
    document.getElementById("calcValOutput").textContent = `$${outputCost.toFixed(4)}`;
    document.getElementById("calcValTotal").textContent = `$${totalCost.toFixed(4)}`;

    // Build comparison chart data
    const chartData = Object.keys(RATE_CARDS).map(key => {
      const card = RATE_CARDS[key];
      const modelInputCost = (inputVal / 1000000) * card.input;
      const modelOutputCost = (outputVal / 1000000) * card.output;
      const modelTotalCost = modelInputCost + modelOutputCost;
      return {
        key: key,
        name: card.name,
        total: modelTotalCost
      };
    });

    // Find maximum cost to establish chart scale
    const maxCost = Math.max(...chartData.map(c => c.total));

    chartWrapper.innerHTML = chartData.map(item => {
      const percentage = maxCost > 0 ? (item.total / maxCost) * 100 : 0;
      const isSelected = item.key === selectedModel ? "accent-fill" : "";
      
      return `
        <div class="calc-chart-row">
          <div class="calc-chart-label" title="${item.name}">${item.name}</div>
          <div class="calc-chart-bar-wrapper">
            <div class="calc-chart-bar-fill ${isSelected}" style="width: ${percentage}%;"></div>
          </div>
          <div class="calc-chart-val">$${item.total.toFixed(4)}</div>
        </div>
      `;
    }).join("");

    resultBox.classList.add("active");
    resultBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
  });
}
