#!/usr/bin/env python3
"""Rewrite priority editorial pages from verified primary-source notes."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
REVIEWED = "July 29, 2026"

PRIORITY_MAINS = {
    "reviews/claude-sonnet-5-review.html": """
<main class="article-container" id="main-content">
  <header class="article-header">
    <span class="article-card-tag">Documentation-based review</span>
    <h1>Claude Sonnet 5 Review: Features, Pricing and Limits</h1>
    <p class="article-subtitle">A source-backed assessment of Anthropic's current Sonnet model for coding, agents, and professional knowledge work.</p>
    <p class="editorial-byline">Editorial review by <a href="../author/hussein-harby.html">Hussein Harby</a>. Reviewed July 29, 2026. No hands-on benchmark is claimed.</p>
  </header>

  <section>
    <h2>Verdict in brief</h2>
    <p>Claude Sonnet 5 is a strong default for developers and knowledge workers who need an agentic model with published tool-use, coding, and long-horizon workflow improvements. Anthropic released it on June 30, 2026 and made it available across Claude plans, Claude Code, and the Claude API under the model ID <code>claude-sonnet-5</code>.</p>
    <p>The strongest reason to shortlist Sonnet 5 is not a single provider benchmark. It is the combination of broad product access, adjustable effort, agent-oriented design, and a lower published price than Anthropic's Opus tier. The main caution is that Anthropic's evaluations are provider-run. Teams should validate reliability, latency, and token consumption on their own tasks.</p>
  </section>

  <section>
    <h2>Official availability and pricing</h2>
    <div style="overflow-x:auto">
      <table>
        <thead><tr><th>Item</th><th>Published detail</th></tr></thead>
        <tbody>
          <tr><td>Release date</td><td>June 30, 2026</td></tr>
          <tr><td>API model ID</td><td><code>claude-sonnet-5</code></td></tr>
          <tr><td>Access</td><td>Claude plans, Claude Code, and the Claude Platform</td></tr>
          <tr><td>Introductory API price</td><td>$2 per million input tokens and $10 per million output tokens through August 31, 2026</td></tr>
          <tr><td>Published standard price</td><td>$3 per million input tokens and $15 per million output tokens after the introductory period</td></tr>
        </tbody>
      </table>
    </div>
    <p>Prices are date-sensitive. Check Anthropic's current pricing before making a budget decision.</p>
  </section>

  <section>
    <h2>What changed in Sonnet 5</h2>
    <p>Anthropic positions Sonnet 5 as its most agentic Sonnet model to date. The official announcement emphasizes planning, browser and terminal tool use, coding, and long-running professional workflows. It also introduces effort controls that let developers trade cost and latency for additional reasoning.</p>
    <p>Anthropic reports improvements over Sonnet 4.6 on agentic search, computer use, coding, and knowledge-work evaluations. Those results are useful for understanding the provider's design goals, but they should be treated as Anthropic's measurements rather than independent AI Profit Hub test results.</p>
  </section>

  <section>
    <h2>Strengths</h2>
    <ul>
      <li><strong>Agent-oriented design:</strong> The model is explicitly designed for multi-step work that uses tools and maintains a plan.</li>
      <li><strong>Broad access:</strong> The same model family is available in the Claude product, Claude Code, and the API.</li>
      <li><strong>Clear published pricing:</strong> Anthropic provides a dated introductory rate and a stated standard rate.</li>
      <li><strong>Safety documentation:</strong> Anthropic publishes a system card and describes the safeguards used for higher-risk cyber requests.</li>
    </ul>
  </section>

  <section>
    <h2>Limitations and decision risks</h2>
    <ul>
      <li>Provider benchmarks may not reflect your repository, prompts, tools, or production constraints.</li>
      <li>Higher effort can increase token usage, latency, and total cost.</li>
      <li>Agentic workflows still need permission boundaries, logging, retries, and human review for consequential actions.</li>
      <li>The updated tokenizer can change token counts compared with earlier Sonnet models, so migration budgets should use measured usage rather than a simple price comparison.</li>
    </ul>
  </section>

  <section>
    <h2>Who should choose it?</h2>
    <p>Sonnet 5 is best suited to teams that want one model for coding, tool use, document analysis, and agent workflows without moving to Anthropic's highest-cost tier. Cost-sensitive batch workloads may benefit from a smaller model. Teams already standardized on OpenAI or Google should compare total workflow reliability, not just model-list pricing.</p>
  </section>

  <section>
    <h2>Hussein's Take</h2>
    <p>Sonnet 5 deserves a place on a serious agent-model shortlist because Anthropic publishes a clear product position, API identity, pricing schedule, and safety record. I would not select it from launch benchmarks alone. Run a fixed set of repository tasks, measure completion quality and retries, and compare the total cost of a successful workflow.</p>
  </section>

  <section class="review-methodology">
    <h2>Review methodology</h2>
    <p>This documentation-based review used Anthropic's launch announcement, system card, and published pricing as checked on July 29, 2026. AI Profit Hub did not run an independent benchmark or claim hands-on product testing for this page.</p>
  </section>

  <section class="editorial-sources">
    <h2>Primary sources</h2>
    <ul>
      <li><a href="https://www.anthropic.com/news/claude-sonnet-5" target="_blank" rel="noopener noreferrer">Anthropic: Introducing Claude Sonnet 5</a></li>
      <li><a href="https://www-cdn.anthropic.com/73ad94ca3c0502e75e46637cc62c8bd9532a7f2c/Claude%20Sonnet%205%20System%20Card.pdf" target="_blank" rel="noopener noreferrer">Anthropic: Claude Sonnet 5 System Card</a></li>
      <li><a href="https://www.anthropic.com/pricing" target="_blank" rel="noopener noreferrer">Anthropic pricing</a></li>
    </ul>
  </section>
</main>
""",
    "articles/gpt-5-6-sol-review-2026.html": """
<main class="article-container" id="main-content">
  <header class="article-header">
    <span class="article-card-tag">Documentation-based review</span>
    <h1>GPT-5.6 Sol Review: Features, Pricing and Limitations</h1>
    <p class="article-subtitle">A practical assessment of OpenAI's flagship GPT-5.6 model using the official model catalog and guidance.</p>
    <p class="editorial-byline">Editorial review by <a href="../author/hussein-harby.html">Hussein Harby</a>. Reviewed July 29, 2026. No independent benchmark is claimed.</p>
  </header>

  <section>
    <h2>Verdict in brief</h2>
    <p>GPT-5.6 Sol is OpenAI's flagship model for complex professional work, including coding, reasoning, tool use, and long-context workflows. The <code>gpt-5.6</code> alias routes to <code>gpt-5.6-sol</code>, while Terra and Luna provide lower-cost options in the same family.</p>
    <p>Sol is the right baseline when task failure is more expensive than model usage. It is a poor default for every request: classification, extraction, and high-volume simple tasks should be tested on Terra, Luna, or another efficient model.</p>
  </section>

  <section>
    <h2>Official specifications</h2>
    <div style="overflow-x:auto">
      <table>
        <thead><tr><th>Specification</th><th>Published value</th></tr></thead>
        <tbody>
          <tr><td>Model ID</td><td><code>gpt-5.6-sol</code></td></tr>
          <tr><td>Alias</td><td><code>gpt-5.6</code></td></tr>
          <tr><td>Input price</td><td>$5 per million tokens</td></tr>
          <tr><td>Cached input price</td><td>$0.50 per million tokens</td></tr>
          <tr><td>Output price</td><td>$30 per million tokens</td></tr>
          <tr><td>Context window</td><td>1.05 million tokens</td></tr>
          <tr><td>Maximum output</td><td>128,000 tokens</td></tr>
          <tr><td>Knowledge cutoff</td><td>February 16, 2026</td></tr>
        </tbody>
      </table>
    </div>
    <p>These values were checked in OpenAI's model catalog on July 29, 2026. Pricing and limits can change.</p>
  </section>

  <section>
    <h2>Where Sol fits</h2>
    <p>OpenAI recommends Sol for complex reasoning and coding. It supports image input, function calling, structured outputs, streaming, and tools through the Responses API. Adjustable reasoning effort ranges from none through max, which lets an application tune latency and depth by task.</p>
    <p>The million-token context window is useful only when retrieval, prompt structure, and output evaluation are designed carefully. Sending an entire repository or document collection can increase cost and distract the model. Retrieval and scoped context remain useful engineering controls.</p>
  </section>

  <section>
    <h2>Strengths</h2>
    <ul>
      <li>A single flagship model for text, image input, tools, structured output, and long-context work.</li>
      <li>Clear model IDs and lower-cost family alternatives for routing.</li>
      <li>Large published context and output limits for complex production workflows.</li>
      <li>Reasoning-effort controls that support deliberate quality and latency testing.</li>
    </ul>
  </section>

  <section>
    <h2>Limitations</h2>
    <ul>
      <li>Output tokens are substantially more expensive than input tokens, so verbose or retry-heavy workflows can dominate cost.</li>
      <li>A large context window does not remove the need for source selection, permissions, evaluation, and human review.</li>
      <li>Provider documentation describes capabilities, not guaranteed performance on a specific business process.</li>
      <li>Applications should pin model IDs and test migration behaviour rather than assuming an alias will never change.</li>
    </ul>
  </section>

  <section>
    <h2>Practical selection framework</h2>
    <ol>
      <li>Define a representative task set and an objective success rubric.</li>
      <li>Use Sol as the quality baseline.</li>
      <li>Run the same tasks on Terra and Luna.</li>
      <li>Measure successful-task cost, latency, retries, and human corrections.</li>
      <li>Route only the tasks that need Sol's additional capability to the flagship model.</li>
    </ol>
  </section>

  <section>
    <h2>Hussein's Take</h2>
    <p>GPT-5.6 Sol is a sensible quality baseline, not a universal default. The most useful production decision is usually a routing decision: reserve Sol for tasks where better reasoning changes the outcome, and use lower-cost models where it does not.</p>
  </section>

  <section class="review-methodology">
    <h2>Review methodology</h2>
    <p>This documentation-based review uses OpenAI's official model catalog, comparison page, and model guidance. AI Profit Hub did not run an independent benchmark for this article.</p>
  </section>

  <section class="editorial-sources">
    <h2>Primary sources</h2>
    <ul>
      <li><a href="https://developers.openai.com/api/docs/models/gpt-5.6-sol" target="_blank" rel="noopener noreferrer">OpenAI: GPT-5.6 Sol model page</a></li>
      <li><a href="https://developers.openai.com/api/docs/models/compare" target="_blank" rel="noopener noreferrer">OpenAI: Compare models</a></li>
      <li><a href="https://developers.openai.com/api/docs/guides/latest-model" target="_blank" rel="noopener noreferrer">OpenAI: Model guidance</a></li>
    </ul>
  </section>
</main>
""",
    "articles/deepseek-v4-china-ai-model-2026.html": """
<main class="article-container" id="main-content">
  <header class="article-header">
    <span class="article-card-tag">Model guide</span>
    <h1>DeepSeek V4 Guide: Models, Access, Pricing and Limits</h1>
    <p class="article-subtitle">A source-backed guide to DeepSeek V4-Pro and V4-Flash using DeepSeek's release notes, pricing page, and transparency center.</p>
    <p class="editorial-byline">Editorial review by <a href="../author/hussein-harby.html">Hussein Harby</a>. Reviewed July 29, 2026.</p>
  </header>

  <section>
    <h2>What DeepSeek released</h2>
    <p>DeepSeek announced the V4 preview on April 24, 2026. The API exposes two model IDs: <code>deepseek-v4-pro</code> and <code>deepseek-v4-flash</code>. Both support thinking and non-thinking modes through OpenAI-compatible and Anthropic-compatible interfaces.</p>
    <p>DeepSeek publishes model cards and technical material through its transparency center. Its launch post describes V4-Pro as a 1.6 trillion parameter mixture-of-experts model with 49 billion active parameters, and V4-Flash as a 284 billion parameter model with 13 billion active parameters. Those figures are provider-published specifications.</p>
  </section>

  <section>
    <h2>Model choice</h2>
    <div style="overflow-x:auto">
      <table>
        <thead><tr><th>Decision</th><th>V4-Pro</th><th>V4-Flash</th></tr></thead>
        <tbody>
          <tr><td>Primary role</td><td>Higher-capability reasoning and agent work</td><td>Faster, lower-cost general and agent work</td></tr>
          <tr><td>API ID</td><td><code>deepseek-v4-pro</code></td><td><code>deepseek-v4-flash</code></td></tr>
          <tr><td>Published context</td><td>1 million tokens</td><td>1 million tokens</td></tr>
          <tr><td>Thinking mode</td><td>Supported</td><td>Supported</td></tr>
          <tr><td>Best first test</td><td>Complex coding and multi-step reasoning</td><td>High-volume workflows and routing baseline</td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <section>
    <h2>Access and pricing</h2>
    <p>The API base URL remains <code>https://api.deepseek.com</code>. DeepSeek also publishes an Anthropic-compatible base URL. Current prices are listed in Chinese yuan per million tokens and differ for cache hits, uncached input, and output. Because those rates can change, this guide links to the live pricing page rather than freezing a price claim into the recommendation.</p>
    <p>The older <code>deepseek-chat</code> and <code>deepseek-reasoner</code> names were scheduled for retirement on July 24, 2026. New integrations should use the V4 model IDs and confirm the current migration notes.</p>
  </section>

  <section>
    <h2>Capabilities and evidence limits</h2>
    <p>DeepSeek presents V4 as an agentic, coding, reasoning, and long-context model family. It also publishes open weights and a technical report. Benchmark statements in the release post remain provider measurements; they should not be treated as an independent result or as proof that V4 will outperform a closed model on every workload.</p>
  </section>

  <section>
    <h2>Practical implementation checklist</h2>
    <ol>
      <li>Use the current V4 model IDs instead of retired aliases.</li>
      <li>Set thinking mode and effort deliberately rather than accepting defaults without testing.</li>
      <li>Measure cache-hit behaviour because it can materially change cost.</li>
      <li>Apply user isolation, rate limits, logging, and permission boundaries to agent workflows.</li>
      <li>Evaluate both Pro and Flash on the same task set before choosing a default.</li>
    </ol>
  </section>

  <section>
    <h2>Hussein's Take</h2>
    <p>V4-Flash should be the first cost and latency baseline for most teams; V4-Pro should earn its place on tasks where additional reasoning changes the result. DeepSeek's open technical material is useful, but production selection still requires your own task-level evaluation.</p>
  </section>

  <section class="editorial-sources">
    <h2>Primary sources</h2>
    <ul>
      <li><a href="https://api-docs.deepseek.com/news/news260424/" target="_blank" rel="noopener noreferrer">DeepSeek V4 official release</a></li>
      <li><a href="https://api-docs.deepseek.com/quick_start/pricing" target="_blank" rel="noopener noreferrer">DeepSeek models and pricing</a></li>
      <li><a href="https://api-docs.deepseek.com/updates/" target="_blank" rel="noopener noreferrer">DeepSeek API change log</a></li>
      <li><a href="https://www.deepseek.com/en/transparency/" target="_blank" rel="noopener noreferrer">DeepSeek transparency center</a></li>
    </ul>
  </section>
</main>
""",
    "compare/deepseek-v4-vs-gpt-5-6-sol.html": """
<main class="article-container" id="main-content">
  <header class="article-header">
    <span class="article-card-tag">Model comparison</span>
    <h1>DeepSeek V4 vs GPT-5.6 Sol: Practical Comparison</h1>
    <p class="article-subtitle">A documentation-based comparison of access, pricing structure, context, deployment choices, and best-fit workloads.</p>
    <p class="editorial-byline">Editorial review by <a href="../author/hussein-harby.html">Hussein Harby</a>. Reviewed July 29, 2026. No independent benchmark is claimed.</p>
  </header>

  <section>
    <h2>Verdict summary</h2>
    <p>Choose GPT-5.6 Sol when you want OpenAI's flagship model, integrated platform tools, and a clearly documented dollar-denominated API price. Start with DeepSeek V4-Flash when low-cost, high-volume work or open-model evaluation matters, and test V4-Pro for harder reasoning and coding tasks.</p>
    <p>There is no responsible universal winner. The providers publish different benchmarks, pricing currencies, infrastructure options, and product integrations. A useful comparison must measure successful-task cost on the same workload.</p>
  </section>

  <section>
    <h2>Official specifications at a glance</h2>
    <div style="overflow-x:auto">
      <table>
        <thead><tr><th>Factor</th><th>DeepSeek V4</th><th>GPT-5.6 Sol</th></tr></thead>
        <tbody>
          <tr><td>Provider</td><td>DeepSeek</td><td>OpenAI</td></tr>
          <tr><td>Model IDs</td><td><code>deepseek-v4-flash</code>, <code>deepseek-v4-pro</code></td><td><code>gpt-5.6-sol</code></td></tr>
          <tr><td>Published context</td><td>1 million tokens</td><td>1.05 million tokens</td></tr>
          <tr><td>Published max output</td><td>Check current DeepSeek pricing documentation</td><td>128,000 tokens</td></tr>
          <tr><td>Pricing structure</td><td>CNY rates for cache hits, uncached input, and output</td><td>USD rates for input, cached input, and output</td></tr>
          <tr><td>Open weights</td><td>Published for V4 preview models</td><td>No</td></tr>
          <tr><td>Review basis</td><td>Official release, pricing, and transparency pages</td><td>Official model catalog and guidance</td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <section>
    <h2>Coding and agent workflows</h2>
    <p>Both providers position these models for complex coding and tool-using agents. OpenAI integrates Sol with the Responses API and its platform tools. DeepSeek offers OpenAI-compatible and Anthropic-compatible API formats and publishes thinking-mode controls. Architecture and API compatibility do not guarantee equal tool reliability; test your actual tool schemas, permission model, retries, and long-running state.</p>
  </section>

  <section>
    <h2>Cost comparison</h2>
    <p>Do not compare a single token price in isolation. Currency, cache-hit assumptions, output length, reasoning tokens, failed attempts, and human correction time can change the result. Build a small evaluation set and calculate cost per accepted output.</p>
  </section>

  <section>
    <h2>Privacy and deployment</h2>
    <p>Review the provider terms, data controls, account region, and retention settings that apply to your plan. Open weights can support additional deployment choices, but operating an open model creates infrastructure, security, and maintenance responsibilities. API use creates a different risk profile and should be evaluated under the applicable contract.</p>
  </section>

  <section>
    <h2>Best choice by user type</h2>
    <ul>
      <li><strong>OpenAI platform teams:</strong> Sol is the simpler integration baseline.</li>
      <li><strong>Cost-sensitive API teams:</strong> Test V4-Flash first, then escalate difficult tasks.</li>
      <li><strong>Open-model researchers:</strong> DeepSeek provides the relevant weights and technical material.</li>
      <li><strong>Regulated organisations:</strong> Decide from contracts, hosting, audit controls, and data policy before model quality.</li>
    </ul>
  </section>

  <section>
    <h2>Hussein's Take</h2>
    <p>Use Sol as a quality baseline and V4-Flash as a cost baseline. Then let measured successful-task cost decide. Claims that one model categorically defeats the other are less useful than a reproducible routing policy.</p>
  </section>

  <section class="review-methodology">
    <h2>Comparison methodology</h2>
    <p>This comparison uses current official model, pricing, release, and transparency documentation checked on July 29, 2026. Provider benchmark tables were not combined because their methods are not directly interchangeable.</p>
  </section>

  <section class="editorial-sources">
    <h2>Primary sources</h2>
    <ul>
      <li><a href="https://api-docs.deepseek.com/news/news260424/" target="_blank" rel="noopener noreferrer">DeepSeek V4 official release</a></li>
      <li><a href="https://api-docs.deepseek.com/quick_start/pricing" target="_blank" rel="noopener noreferrer">DeepSeek official pricing</a></li>
      <li><a href="https://developers.openai.com/api/docs/models/gpt-5.6-sol" target="_blank" rel="noopener noreferrer">OpenAI GPT-5.6 Sol model page</a></li>
      <li><a href="https://developers.openai.com/api/docs/models/compare" target="_blank" rel="noopener noreferrer">OpenAI model comparison</a></li>
    </ul>
  </section>
</main>
""",
    "compare/claude-sonnet-5-vs-gemini-3-5-flash.html": """
<main class="article-container" id="main-content">
  <header class="article-header">
    <span class="article-card-tag">Model comparison</span>
    <h1>Claude Sonnet 5 vs Gemini 3.5 Flash</h1>
    <p class="article-subtitle">A source-backed comparison for coding, agents, multimodal input, pricing decisions, and production evaluation.</p>
    <p class="editorial-byline">Editorial review by <a href="../author/hussein-harby.html">Hussein Harby</a>. Reviewed July 29, 2026. No independent benchmark is claimed.</p>
  </header>

  <section>
    <h2>Verdict summary</h2>
    <p>Claude Sonnet 5 is the clearer shortlist choice for teams centered on Claude Code, Anthropic's agent workflow, and a published post-introductory token price. Gemini 3.5 Flash is the stronger first test for high-speed multimodal and agentic workflows that benefit from Google's built-in search, Maps grounding, code execution, file search, and computer-use support.</p>
    <p>Neither model wins every workload. Run the same tasks with the same acceptance rubric and measure completion quality, retries, latency, and total cost.</p>
  </section>

  <section>
    <h2>Official comparison</h2>
    <div style="overflow-x:auto">
      <table>
        <thead><tr><th>Factor</th><th>Claude Sonnet 5</th><th>Gemini 3.5 Flash</th></tr></thead>
        <tbody>
          <tr><td>Provider</td><td>Anthropic</td><td>Google</td></tr>
          <tr><td>Model ID</td><td><code>claude-sonnet-5</code></td><td><code>gemini-3.5-flash</code></td></tr>
          <tr><td>Published input limit</td><td>Check current Anthropic model documentation</td><td>1,048,576 tokens</td></tr>
          <tr><td>Published output limit</td><td>Check current Anthropic model documentation</td><td>65,536 tokens</td></tr>
          <tr><td>Input modalities</td><td>Check current Anthropic documentation</td><td>Text, image, video, audio, and PDF</td></tr>
          <tr><td>Tool focus</td><td>Agentic coding and tool use</td><td>Function calling, search and Maps grounding, code execution, file search, and computer use</td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <section>
    <h2>Coding and agents</h2>
    <p>Anthropic presents Sonnet 5 as its most agentic Sonnet model and emphasizes planning, coding, browser and terminal use, and adjustable effort. Google describes Gemini 3.5 Flash as a stable model for agentic loops, coding, long-horizon work, and sub-agent deployment. Those descriptions define product intent; they do not replace repository-level evaluation.</p>
  </section>

  <section>
    <h2>Multimodal and platform tools</h2>
    <p>Gemini's official model page lists broad multimodal input and a wide built-in tool set. That can reduce integration work for Google-centered applications. Sonnet 5 may be more natural for teams already using Claude Code or Anthropic's API patterns. Platform fit can matter more than a small benchmark difference.</p>
  </section>

  <section>
    <h2>Pricing and cost control</h2>
    <p>Anthropic announced introductory Sonnet 5 pricing through August 31, 2026 and a higher standard rate after that date. Gemini pricing should be checked on Google's live pricing page for the relevant consumption option. Compare successful-task cost rather than headline token rates.</p>
  </section>

  <section>
    <h2>Best choice by workload</h2>
    <ul>
      <li><strong>Claude Code and Anthropic workflows:</strong> Start with Sonnet 5.</li>
      <li><strong>Google AI Studio or multimodal agents:</strong> Start with Gemini 3.5 Flash.</li>
      <li><strong>High-volume production:</strong> Evaluate latency, caching, batch options, and accepted-output cost.</li>
      <li><strong>Security-sensitive agents:</strong> Test prompt injection resistance, permissions, logging, and human approval independently of model choice.</li>
    </ul>
  </section>

  <section>
    <h2>Hussein's Take</h2>
    <p>Choose the platform whose tools and controls remove the most engineering work, then verify model quality on your own tasks. Sonnet 5 is a strong coding-agent baseline; Gemini 3.5 Flash is a compelling multimodal-agent baseline.</p>
  </section>

  <section class="review-methodology">
    <h2>Comparison methodology</h2>
    <p>This documentation-based comparison uses Anthropic's Sonnet 5 announcement and system card plus Google's Gemini 3.5 Flash model documentation. Provider benchmarks are not presented as independent AI Profit Hub results.</p>
  </section>

  <section class="editorial-sources">
    <h2>Primary sources</h2>
    <ul>
      <li><a href="https://www.anthropic.com/news/claude-sonnet-5" target="_blank" rel="noopener noreferrer">Anthropic: Introducing Claude Sonnet 5</a></li>
      <li><a href="https://www-cdn.anthropic.com/73ad94ca3c0502e75e46637cc62c8bd9532a7f2c/Claude%20Sonnet%205%20System%20Card.pdf" target="_blank" rel="noopener noreferrer">Claude Sonnet 5 System Card</a></li>
      <li><a href="https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash" target="_blank" rel="noopener noreferrer">Google: Gemini 3.5 Flash model documentation</a></li>
      <li><a href="https://ai.google.dev/gemini-api/docs/whats-new-gemini-3.5" target="_blank" rel="noopener noreferrer">Google: What's new in Gemini 3.5 Flash</a></li>
    </ul>
  </section>
</main>
""",
    "guides/how-to-use-deepseek-v4-for-coding-2026.html": """
<main class="article-container" id="main-content">
  <header class="article-header">
    <span class="article-card-tag">Documentation-based guide</span>
    <h1>How to Use DeepSeek V4 for Coding</h1>
    <p class="article-subtitle">A practical setup and evaluation guide for using DeepSeek V4 through the official API without relying on unverified model names or benchmark claims.</p>
    <p class="editorial-byline">Editorial guide by <a href="../author/hussein-harby.html">Hussein Harby</a>. Reviewed July 29, 2026. No independent benchmark is claimed.</p>
  </header>

  <section>
    <h2>Choose the documented V4 model</h2>
    <p>DeepSeek announced V4-Pro and V4-Flash on April 24, 2026. The provider describes Pro as the model for higher-quality reasoning and Flash as the lower-latency option. Model availability and identifiers can change, so query the API model list or check DeepSeek's current documentation before deploying a fixed model name.</p>
    <p>Use Flash for fast iteration, routine transformations, and high-volume assistance. Start with Pro when the task needs deeper repository context, multi-step debugging, or careful architectural reasoning. This is a workflow recommendation, not an independent performance ranking.</p>
  </section>

  <section>
    <h2>Set up the official API</h2>
    <p>Store the API key in an environment variable named <code>DEEPSEEK_API_KEY</code>. Do not place credentials in source control, browser code, prompts, or screenshots. DeepSeek documents an OpenAI-compatible API base URL, which means the official OpenAI Python client can be pointed at DeepSeek's endpoint.</p>
    <pre><code class="language-python">import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

models = client.models.list()
for model in models.data:
    print(model.id)</code></pre>
    <p>Run the model-list request first and select a currently returned V4 model identifier. This avoids copying an obsolete or invented ID from a secondary article.</p>
  </section>

  <section>
    <h2>Send a coding request</h2>
    <p>A useful coding prompt supplies the relevant files, the expected behaviour, constraints, and the command that will verify the result. Ask for a focused patch and an explanation of assumptions. Do not send secrets, customer records, or proprietary code unless your organisation has approved the provider and data-handling terms.</p>
    <pre><code class="language-python">model_id = "REPLACE_WITH_A_CURRENT_V4_MODEL_ID"

response = client.chat.completions.create(
    model=model_id,
    messages=[
        {
            "role": "system",
            "content": (
                "You are a careful software engineer. Preserve existing "
                "project conventions and explain uncertain assumptions."
            ),
        },
        {
            "role": "user",
            "content": (
                "Review the supplied function, fix the failing edge case, "
                "and return a minimal patch plus the tests to run."
            ),
        },
    ],
)

print(response.choices[0].message.content)</code></pre>
    <p>The placeholder is intentional. Replace it only with an identifier returned by the official API or listed in current DeepSeek documentation.</p>
  </section>

  <section>
    <h2>Use a repeatable coding workflow</h2>
    <ol>
      <li><strong>Define the acceptance test:</strong> State the failing command, expected output, or observable behaviour.</li>
      <li><strong>Provide bounded context:</strong> Include the smallest relevant files, interfaces, and error logs.</li>
      <li><strong>Request a focused change:</strong> Tell the model to preserve public behaviour and existing project conventions.</li>
      <li><strong>Review the patch:</strong> Check security, error handling, dependencies, and unrelated edits.</li>
      <li><strong>Run deterministic checks:</strong> Execute tests, formatters, type checks, and static analysis locally.</li>
      <li><strong>Measure the result:</strong> Record accepted-output rate, retries, latency, and token cost on representative tasks.</li>
    </ol>
  </section>

  <section>
    <h2>Evaluate quality and cost</h2>
    <p>Do not select a coding model from a provider benchmark alone. Build a small private evaluation set that covers bug fixes, tests, refactoring, documentation, and repository navigation. Score whether each task passes its acceptance test without introducing regressions.</p>
    <p>DeepSeek publishes separate input, cache-hit, and output pricing. Calculate the cost of an accepted result rather than the cost of one request, because retries and long generated patches can dominate a workflow. Recheck the official pricing page before budgeting.</p>
  </section>

  <section>
    <h2>Security checklist</h2>
    <ul>
      <li>Keep API keys in a secret manager or local environment variable.</li>
      <li>Exclude credentials, private keys, production data, and customer records from prompts.</li>
      <li>Review generated dependency changes and shell commands before execution.</li>
      <li>Use least-privilege tools and require human approval for production actions.</li>
      <li>Scan generated code and run the project's normal security checks.</li>
    </ul>
  </section>

  <section>
    <h2>Hussein's Take</h2>
    <p>DeepSeek V4 is worth evaluating when API economics and long-context coding workflows matter, but the decision should come from your own acceptance tests. Start with the official model list, keep the integration reversible, and compare accepted-output cost with the other providers your team can support.</p>
  </section>

  <section class="review-methodology">
    <h2>Guide methodology</h2>
    <p>This documentation-based guide uses DeepSeek's release notice, API quick start, model-list endpoint, and pricing documentation as checked on July 29, 2026. AI Profit Hub did not run an independent coding benchmark for this page.</p>
  </section>

  <section class="editorial-sources">
    <h2>Primary sources</h2>
    <ul>
      <li><a href="https://api-docs.deepseek.com/news/news260424/" target="_blank" rel="noopener noreferrer">DeepSeek: V4-Pro and V4-Flash release</a></li>
      <li><a href="https://api-docs.deepseek.com/" target="_blank" rel="noopener noreferrer">DeepSeek API quick start</a></li>
      <li><a href="https://api-docs.deepseek.com/api/list-models" target="_blank" rel="noopener noreferrer">DeepSeek: List Models endpoint</a></li>
      <li><a href="https://api-docs.deepseek.com/quick_start/pricing" target="_blank" rel="noopener noreferrer">DeepSeek API pricing</a></li>
    </ul>
  </section>
</main>
""",
}

COMPANIES = {
    "companies/anthropic.html": {
        "name": "Anthropic",
        "summary": "Anthropic develops the Claude model family and related products for chat, coding, tool use, and enterprise AI.",
        "products": [
            "Claude applications for individual and business users",
            "Claude Code for agentic software-development workflows",
            "The Claude API and supported cloud-platform access",
            "Published system cards and safety research",
        ],
        "analysis": "Anthropic's practical distinction is its focus on model behaviour, safety documentation, and agent-oriented developer workflows. Model names, access, and pricing change frequently, so this page points readers to the live catalog rather than preserving an outdated list.",
        "take": "Anthropic is most relevant to teams that value strong coding and tool-use workflows plus detailed safety documentation. Compare current model pricing and run representative tasks before committing to a provider.",
        "sources": [
            ("Anthropic official site", "https://www.anthropic.com/"),
            ("Claude model documentation", "https://docs.anthropic.com/en/docs/about-claude/models/overview"),
            ("Anthropic pricing", "https://www.anthropic.com/pricing"),
        ],
    },
    "companies/deepseek.html": {
        "name": "DeepSeek",
        "summary": "DeepSeek publishes open model research, model weights, chat products, and APIs, including the V4-Pro and V4-Flash model family.",
        "products": [
            "DeepSeek chat and mobile access",
            "OpenAI-compatible and Anthropic-compatible APIs",
            "DeepSeek V4-Pro and V4-Flash",
            "Published model cards, technical reports, and open weights",
        ],
        "analysis": "DeepSeek combines low published API pricing with open technical material and model weights. Provider benchmark claims should be read alongside the technical report and then tested on the intended workload.",
        "take": "DeepSeek is a serious option for cost-sensitive API work and open-model evaluation. V4-Flash is the practical first baseline; use V4-Pro only when measured task quality justifies it.",
        "sources": [
            ("DeepSeek transparency center", "https://www.deepseek.com/en/transparency/"),
            ("DeepSeek API change log", "https://api-docs.deepseek.com/updates/"),
            ("DeepSeek official pricing", "https://api-docs.deepseek.com/quick_start/pricing"),
        ],
    },
    "companies/google.html": {
        "name": "Google AI",
        "summary": "Google develops the Gemini model family, Gemma open models, AI Studio, NotebookLM, and AI services across Google Cloud and consumer products.",
        "products": [
            "Gemini models and the Gemini API",
            "Google AI Studio and Vertex AI access",
            "Gemma open models for local and custom deployment",
            "NotebookLM and other source-grounded productivity products",
        ],
        "analysis": "Google's advantage is the breadth of its multimodal models, built-in grounding and tool support, cloud deployment, and consumer-product integration. Readers should distinguish Gemini API specifications from features available only in a specific Google product or plan.",
        "take": "Google AI is strongest when multimodal input, grounding, and the Google platform reduce integration effort. Verify the exact model, region, plan, and product surface before comparing features.",
        "sources": [
            ("Google Gemini model documentation", "https://ai.google.dev/gemini-api/docs/models"),
            ("Google AI official site", "https://ai.google/"),
            ("Google Gemma documentation", "https://ai.google.dev/gemma"),
        ],
    },
    "companies/microsoft.html": {
        "name": "Microsoft AI",
        "summary": "Microsoft offers AI through Copilot products, Azure and Microsoft Foundry services, GitHub, and its own MAI model research.",
        "products": [
            "Microsoft Copilot products for work and development",
            "Azure AI and Microsoft Foundry services",
            "GitHub Copilot and developer tooling",
            "Microsoft's MAI model family and research",
        ],
        "analysis": "Microsoft's main value is distribution across enterprise identity, productivity, cloud, and developer systems. A model or Copilot feature may have different availability, data controls, and commercial terms across products.",
        "take": "Microsoft AI is most compelling for organisations already operating on Microsoft identity, productivity, and cloud systems. Evaluate the complete product contract and governance controls, not only the underlying model.",
        "sources": [
            ("Microsoft AI official site", "https://www.microsoft.com/en-us/ai"),
            ("Microsoft Build 2026 official announcement", "https://blogs.microsoft.com/blog/2026/06/02/microsoft-build-2026-be-yourself-at-work/"),
            ("Microsoft Foundry documentation", "https://learn.microsoft.com/azure/ai-foundry/"),
        ],
    },
    "companies/openai.html": {
        "name": "OpenAI",
        "summary": "OpenAI develops ChatGPT, API models, developer tools, and multimodal services for individuals, developers, and organisations.",
        "products": [
            "ChatGPT plans and workspace products",
            "The Responses API and developer platform",
            "GPT-5.6 Sol, Terra, and Luna models",
            "Image, realtime, speech, transcription, and specialised models",
        ],
        "analysis": "OpenAI's platform combines general models with first-party tools and a broad developer ecosystem. Product-plan features and API capabilities are not identical, and aliases can change, so production systems should use documented model IDs and migration tests.",
        "take": "OpenAI is a strong default when platform breadth and integrated tools matter. Use Sol as a quality baseline, then route simpler work to a lower-cost model when the measured result is equivalent.",
        "sources": [
            ("OpenAI model catalog", "https://developers.openai.com/api/docs/models"),
            ("OpenAI model comparison", "https://developers.openai.com/api/docs/models/compare"),
            ("OpenAI announcements", "https://openai.com/news/"),
        ],
    },
    "companies/perplexity.html": {
        "name": "Perplexity",
        "summary": "Perplexity builds an answer and research product that combines web retrieval, cited responses, and access to multiple AI models.",
        "products": [
            "Perplexity search and answer experiences",
            "Paid plans with expanded research and model access",
            "File and source-based research workflows",
            "Business and API offerings described in current product documentation",
        ],
        "analysis": "Perplexity's core value is its source-oriented research workflow. Citations improve traceability but do not guarantee that a source supports every generated statement, so readers should open and verify important references.",
        "take": "Perplexity is best for research workflows where seeing sources quickly matters. It should accelerate verification, not replace it.",
        "sources": [
            ("Perplexity official site", "https://www.perplexity.ai/"),
            ("Perplexity Help Center", "https://www.perplexity.ai/help-center"),
        ],
    },
}


def company_main(data: dict) -> str:
    products = "\n".join(f"      <li>{html.escape(item)}</li>" for item in data["products"])
    sources = "\n".join(
        f'      <li><a href="{html.escape(url, quote=True)}" target="_blank" '
        f'rel="noopener noreferrer">{html.escape(label)}</a></li>'
        for label, url in data["sources"]
    )
    name = html.escape(data["name"])
    return f"""
<main id="main-content" class="main">
  <header class="article-header">
    <span class="article-card-tag">Company profile</span>
    <h1>{name}</h1>
    <p>{html.escape(data["summary"])}</p>
    <p class="editorial-byline">Editorial review by <a href="../author/hussein-harby.html">Hussein Harby</a>. Reviewed {REVIEWED}.</p>
  </header>

  <section>
    <h2>Company overview</h2>
    <p>{html.escape(data["summary"])}</p>
    <p>{html.escape(data["analysis"])}</p>
  </section>

  <section>
    <h2>Main products and research areas</h2>
    <ul>
{products}
    </ul>
  </section>

  <section>
    <h2>How to evaluate {name}</h2>
    <p>Start with the official product and model documentation. Confirm the exact plan, model ID, availability region, privacy terms, and current pricing. Provider benchmarks and marketing language should be treated as company claims until reproduced independently.</p>
  </section>

  <section>
    <h2>Decision checklist</h2>
    <p>Before adopting a product, run representative tasks with a written success rubric. Compare accepted-output cost, latency, reliability, data controls, regional availability, and integration effort. Recheck the provider's current documentation before purchase because model catalogs, limits, and prices can change.</p>
  </section>

  <section>
    <h2>Hussein's Take</h2>
    <p>{html.escape(data["take"])}</p>
  </section>

  <section class="editorial-sources">
    <h2>Official sources</h2>
    <ul>
{sources}
    </ul>
  </section>
</main>
"""


def replace_main(text: str, replacement: str) -> str:
    for class_name in ("page-header", "cmp-hero"):
        text = re.sub(
            rf'<section\b[^>]*class=["\'][^"\']*\b{class_name}\b[^"\']*["\'][^>]*>'
            r".*?</section>",
            "",
            text,
            count=1,
            flags=re.IGNORECASE | re.DOTALL,
        )
    main_start = re.search(r"<main\b", text, re.IGNORECASE)
    if main_start:
        prefix = re.sub(
            r'<header\b[^>]*class=["\'][^"\']*\barticle-header\b[^"\']*["\'][^>]*>'
            r".*?</header>",
            "",
            text[: main_start.start()],
            flags=re.IGNORECASE | re.DOTALL,
        )
        text = prefix + text[main_start.start() :]
    pattern = re.compile(r"<main\b.*?</main>", re.IGNORECASE | re.DOTALL)
    if not pattern.search(text):
        raise RuntimeError("Page does not contain a main element")
    return pattern.sub(replacement.strip(), text, count=1)


def canonical_url(text: str) -> str:
    soup = BeautifulSoup(text, "html.parser")
    node = soup.find("link", rel=lambda value: value and "canonical" in value)
    return str(node.get("href", "")) if node else ""


def clean_json_ld(text: str) -> str:
    soup = BeautifulSoup(text, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    description_node = soup.find("meta", attrs={"name": "description"})
    description = str(description_node.get("content", "")) if description_node else ""
    canonical = canonical_url(text)
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": re.sub(r"\s*\|\s*AI Profit Hub\s*$", "", title),
        "description": description,
        "url": canonical,
        "author": {
            "@type": "Person",
            "name": "Hussein Harby",
            "url": "https://ai-profit-hub.com/author/hussein-harby.html",
        },
        "publisher": {
            "@type": "Organization",
            "name": "AI Profit Hub",
            "url": "https://ai-profit-hub.com/",
        },
        "dateModified": "2026-07-29",
    }
    block = (
        '<script type="application/ld+json">\n'
        + json.dumps(schema, indent=2)
        + "\n</script>"
    )
    pattern = re.compile(
        r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>.*?</script>',
        re.IGNORECASE | re.DOTALL,
    )
    without_old_schema = pattern.sub("", text)
    return without_old_schema.replace("</head>", block + "\n</head>", 1)


def main() -> int:
    pages = dict(PRIORITY_MAINS)
    pages.update({path: company_main(data) for path, data in COMPANIES.items()})
    changed = 0
    for rel, replacement in pages.items():
        path = ROOT / rel
        text = path.read_text(encoding="utf-8-sig")
        updated = replace_main(text, replacement)
        updated = clean_json_ld(updated)
        if updated != text:
            path.write_text(updated, encoding="utf-8", newline="")
            changed += 1
    print(json.dumps({"priority_pages_rewritten": changed}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
