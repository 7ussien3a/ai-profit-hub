// ========================================
// TechMind AI - Main JavaScript
// ========================================

document.addEventListener('DOMContentLoaded', () => {
  // === Header Scroll Effect ===
  const header = document.querySelector('.header');
  if (header) {
    window.addEventListener('scroll', () => {
      header.classList.toggle('scrolled', window.scrollY > 20);
    });
  }

  // === Mobile Menu Toggle ===
  const mobileToggle = document.querySelector('.mobile-toggle');
  const navLinks = document.querySelector('.nav-links');
  if (mobileToggle && navLinks) {
    mobileToggle.addEventListener('click', () => {
      navLinks.classList.toggle('active');
      mobileToggle.setAttribute('aria-expanded', String(navLinks.classList.contains('active')));
      const spans = mobileToggle.querySelectorAll('span');
      if (navLinks.classList.contains('active')) {
        spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
        spans[1].style.opacity = '0';
        spans[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
      } else {
        spans[0].style.transform = '';
        spans[1].style.opacity = '';
        spans[2].style.transform = '';
      }
    });

    // Close menu on link click
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('active');
        mobileToggle.setAttribute('aria-expanded', 'false');
        const spans = mobileToggle.querySelectorAll('span');
        spans[0].style.transform = '';
        spans[1].style.opacity = '';
        spans[2].style.transform = '';
      });
    });
  }

  // === Scroll Animations ===
  const animateElements = document.querySelectorAll('.animate-in');
  if (animateElements.length > 0) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.animationPlayState = 'running';
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });

    animateElements.forEach(el => {
      el.style.animationPlayState = 'paused';
      observer.observe(el);
    });
  }

  // === Newsletter Form ===
  const newsletterForm = document.querySelector('.newsletter-form');
  if (newsletterForm) {
    newsletterForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const input = newsletterForm.querySelector('input');
      const btn = newsletterForm.querySelector('button');
      if (input.value.trim()) {
        btn.textContent = '✓ Subscribed!';
        btn.style.background = 'linear-gradient(135deg, #00D4AA, #00B892)';
        input.value = '';
        setTimeout(() => {
          btn.textContent = 'Subscribe';
          btn.style.background = '';
        }, 3000);
      }
    });
  }

  // === Active Nav Link ===
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a').forEach(link => {
    const href = link.getAttribute('href');
    if (href && (href === currentPage || (currentPage === '' && href === 'index.html'))) {
      link.classList.add('active');
    }
  });

  // === Reading Time Calculator ===
  const articleContent = document.querySelector('.article-content');
  const readTimeEl = document.querySelector('.read-time-value');
  if (articleContent && readTimeEl) {
    const text = articleContent.textContent;
    const words = text.trim().split(/\s+/).length;
    const minutes = Math.ceil(words / 200);
    readTimeEl.textContent = `${minutes} min read`;
  }
  // === Dynamic Table of Contents ===
  if (articleContent) {
    const headings = articleContent.querySelectorAll('h2');
    if (headings.length > 0) {
      const toc = document.createElement('div');
      toc.className = 'article-toc animate-in';
      toc.innerHTML = '<h3>Table of Contents</h3><ul></ul>';
      const ul = toc.querySelector('ul');
      
      headings.forEach((heading, index) => {
        heading.id = `heading-${index}`;
        const li = document.createElement('li');
        const a = document.createElement('a');
        a.href = `#heading-${index}`;
        a.textContent = heading.textContent;
        li.appendChild(a);
        ul.appendChild(li);
      });
      
      articleContent.insertBefore(toc, articleContent.firstChild);
    }
  }

  // === Dynamic Social Share Buttons ===
  const articleMeta = document.querySelector('.article-meta');
  if (articleMeta && document.querySelector('.article-header h1')) {
    const shareUrl = encodeURIComponent(window.location.href);
    const shareTitle = encodeURIComponent(document.title);
    
    const shareContainer = document.createElement('div');
    shareContainer.className = 'social-shares animate-in';
    shareContainer.innerHTML = `
      <a href="https://twitter.com/intent/tweet?url=${shareUrl}&text=${shareTitle}" target="_blank" class="share-btn twitter">𝕏 Post</a>
      <a href="https://www.facebook.com/sharer/sharer.php?u=${shareUrl}" target="_blank" class="share-btn facebook">f Share</a>
      <a href="https://www.linkedin.com/shareArticle?mini=true&url=${shareUrl}&title=${shareTitle}" target="_blank" class="share-btn linkedin">in Share</a>
    `;
    
    articleMeta.parentElement.appendChild(shareContainer);
  }

  // === Dynamic Related Articles ===
  if (articleContent) {
    const allArticles = [
      {"title":"10 AI Tools to Start a Faceless YouTube Channel (And Actually Make Money)","link":"ai-tools-faceless-youtube.html","description":"Want to make money on YouTube without showing your face? Discover the exact 10 AI tools you need to write, voice, and edit faceless videos automatically.","category":"🎥 Video Creation"},
      {"title":"10 Best Free AI Tools for Students in 2026 (Save Hours Every Week)","link":"best-free-ai-tools-students.html","description":"Discover the 10 best free AI tools every student needs in 2026. From ChatGPT to Perplexity AI, save hours every week with these powerful tools.","category":"🔥 AI Tools"},
      {"title":"15 ChatGPT Prompts That Will Double Your Productivity at Work","link":"chatgpt-prompts-productivity.html","description":"Stop wasting time on repetitive tasks. I've tested hundreds of ChatGPT prompts, and these 15 will genuinely transform your workflow and save you hours.","category":"🚀 Productivity"},
      {"title":"5 AI Coding Assistants That Will Help You Code Faster in 2026","link":"ai-coding-assistants.html","description":"Stop writing boilerplate code. Discover the top 5 AI coding assistants in 2026 that will double your programming speed and reduce bugs.","category":"💻 Programming"},
      {"title":"5 Best AI Voice Generators for Podcasters and Video Creators","link":"ai-voice-generators.html","description":"Looking for realistic AI voice generation? Compare the top 5 tools like ElevenLabs, Murf, and Descript to find the perfect voice for your videos.","category":"🎙️ Audio & Voice"},
      {"title":"7 Must-Have AI Chrome Extensions to Save You Hours Every Day","link":"ai-chrome-extensions.html","description":"Stop opening ChatGPT in a new tab. These 7 free AI Chrome extensions bring the power of artificial intelligence directly to your browser to supercharge your workflow.","category":"🧩 Extensions"},
      {"title":"Best AI Writing Assistants: Grammarly vs. Jasper vs. Copy.ai","link":"best-ai-writing-assistants.html","description":"Which AI writing tool is actually worth your money in 2026? We compare Grammarly, Jasper, and Copy.ai to find the best assistant for your writing needs.","category":"📝 Copywriting"},
      {"title":"Best Free Alternatives to Midjourney for AI Art Generation in 2026","link":"free-alternatives-midjourney.html","description":"Midjourney is great, but it's expensive. After testing dozens of AI art generators, here are the absolute best free alternatives you should be using in 2026.","category":"🎨 AI Art"},
      {"title":"DeepSeek & Qwen vs. Claude: The New Era of AI in 2026","link":"deepseek-qwen-claude-comparison.html","description":"Discover how Chinese open-source AI models like DeepSeek and Qwen are challenging giants like Claude 3 and ChatGPT in 2026.","category":"🤖 Tech News"},
      {"title":"DeepSeek-R1 vs. Qwen: How Open-Source AI is Changing the World","link":"deepseek-r1-vs-qwen.html","description":"Discover how DeepSeek-R1 and Alibaba's Qwen are breaking America's AI monopoly with open-source reasoning models.","category":"🇨🇳 Tech News"},
      {"title":"DuckDuckGo Installs Surge 30% as Users Reject Being \"Force-Fed\" Google's AI Search","link":"duckduckgo-vs-google-ai-search.html","description":"DuckDuckGo sees a 30% install surge as millions reject Google's AI Overviews. Why users are fleeing AI-powered search and what it means for the future of the web.","category":"🔍 Search & Privacy"},
      {"title":"Gemini 3.1 Pro & Veo 3: Google's Multimodal Masterpiece","link":"google-gemini-3-veo-3.html","description":"Explore how Google's Gemini 3.1 Pro and Veo 3 are revolutionizing video generation and multimodal AI applications.","category":"🌐 Google AI"},
      {"title":"Google's Agentic Search Revolution: How Gemini 3.5 Flash Is Redefining the Internet","link":"google-agentic-search-gemini-flash.html","description":"Google I/O 2026 unveiled agentic search powered by Gemini 3.5 Flash. Information agents, generative UI, and the end of traditional search as we know it.","category":"🚀 Google & Search"},
      {"title":"Googlebook & Autonomous Gemini: Is This the End of the Traditional OS?","link":"googlebook-gemini-android-update.html","description":"Google's AI-native laptop Googlebook and the revolutionary Android Gemini update that lets AI perform multistep tasks autonomously. Full analysis.","category":"📱 Hardware & OS"},
      {"title":"GPT-5.5 vs Claude 4.7: The Ultimate Showdown in 2026","link":"gpt-5-vs-claude-4.html","description":"A comprehensive comparison between OpenAI's GPT-5.5 and Anthropic's Claude 4.7. Which premium AI model is worth your money?","category":"⚔️ AI Battles"},
      {"title":"How to Automate Your Daily Tasks Using AI — Complete Beginner's Guide","link":"automate-tasks-ai.html","description":"Feeling overwhelmed by repetitive tasks? Learn how to use AI to automate your inbox, schedule, and data entry. No coding required. A true beginner's guide.","category":"🤖 Automation"},
      {"title":"How to Build a Custom GPT for Your Business Without Coding (2026 Guide)","link":"custom-gpt-business.html","description":"Learn how to create a custom GPT trained on your specific business data in less than 20 minutes. No coding experience required. Full step-by-step tutorial.","category":"🛠️ Tutorials"},
      {"title":"How to Create an AI Avatar of Yourself in 5 Minutes","link":"ai-avatar-creation.html","description":"Don't want to be on camera? Learn how to create a hyper-realistic AI avatar of yourself that speaks with your voice. Perfect for YouTube and presentations.","category":"🎥 Video Creation"},
      {"title":"How to Make Money with AI Art: 5 Proven Methods","link":"make-money-ai-art.html","description":"Generating beautiful AI art is fun, but how do you monetize it? Discover 5 proven, realistic methods to make money online using AI art generators.","category":"💰 Make Money"},
      {"title":"How to Use AI for Stock Market Analysis (Beginner's Guide)","link":"ai-stock-market-analysis.html","description":"Can AI predict the stock market? Learn how beginners are using AI tools to analyze stocks, read financial reports, and make better investment decisions.","category":"📈 Finance & AI"},
      {"title":"How to Use Notion AI to Organize Your Entire Life","link":"notion-ai-organization.html","description":"Notion is powerful, but Notion AI is a game-changer. Learn how to automate your to-do lists, summarize meeting notes, and organize your life.","category":"🗂️ Organization"},
      {"title":"Is AI Going to Steal Your Job? The Truth in 2026","link":"ai-stealing-jobs-truth.html","description":"Will AI replace humans? We break down the reality of the job market in 2026, which jobs are at risk, and how to future-proof your career.","category":"🔮 Future of Work"},
      {"title":"Meta Lays Off Thousands to Fund AI: The Human Cost of Big Tech's AI Arms Race","link":"meta-layoffs-fund-ai-arms-race.html","description":"Meta fires thousands of employees to redirect budgets toward AI infrastructure. The human stories behind Big Tech's AI pivot and what it means for workers.","category":"📉 Industry Impact"},
      {"title":"Meta's Llama 4 & Muse Spark: The Open-Source Battle for AI's Future","link":"meta-llama-4-muse-spark.html","description":"Meta's Llama 4 and consumer AI assistant Muse Spark are challenging closed-source giants. Analysis of Meta's open-source strategy and its impact.","category":"🔓 Open Source"},
      {"title":"Meta's TRIBE v2: The AI That Creates a Digital Twin of Your Brain","link":"meta-tribe-v2-digital-twin.html","description":"Deep dive into Meta's TRIBE v2 foundation model that predicts brain neural activity. How digital brain twins could revolutionize healthcare and neuroscience.","category":"🧠 Healthcare AI"},
      {"title":"NVIDIA Hits $81.6 Billion Revenue: The Company That Became the Backbone of AI","link":"nvidia-record-revenue-ai-dominance.html","description":"NVIDIA posts record $81.6B quarterly revenue with $75.2B from data centers alone. How one company became the backbone of the entire AI industry in 2026.","category":"💰 Business & Markets"},
      {"title":"OpenAI's $4 Billion Enterprise Push & ChatGPT Ads: What It Means for You","link":"openai-enterprise-ads-2026.html","description":"Analyzing OpenAI's new $4 Billion deployment company and the introduction of ChatGPT Ads in 2026. How will this reshape the AI industry?","category":"💼 Enterprise AI"},
      {"title":"The 2026 AI Layoffs: What The Cloudflare Case Tells Us About the Future of Work","link":"cloudflare-ai-layoffs-2026.html","description":"How AI-driven automation led to 1,100 layoffs at Cloudflare. Analysis of the 2026 AI layoff wave, which jobs are at risk, and how to future-proof your career.","category":"💼 Future of Work"},
      {"title":"The AI Skin Patch: A Wearable Doctor That Computes Directly on Your Body","link":"ai-skin-patch-wearable-doctor.html","description":"Scientists created a stretchable AI skin patch with 10,000 transistors per cm² that detects heart attacks in milliseconds. How this breakthrough changes healthcare forever.","category":"🏥 Healthcare AI"},
      {"title":"The Autonomous Agent Illusion: Why AI Still Fails at Complex Tasks","link":"autonomous-agents-microsoft-research.html","description":"Microsoft's latest research reveals how AI agents still struggle with complex workflows. Why autonomous AI isn't ready and what needs to change.","category":"🔍 Research"},
      {"title":"The Best AI Resume Builders to Land Your Dream Job","link":"ai-resume-builders.html","description":"Beat the ATS (Applicant Tracking Systems) and get hired faster. Discover the best AI resume builders that tailor your CV to specific job descriptions instantly.","category":"💼 Career"},
      {"title":"The Colorado AI Law Dilemma: How Regulation is Finally Catching Up to AI","link":"colorado-ai-law-regulation.html","description":"Analysis of Colorado's AI law setback and how regulations are shaping AI deployments in 2026. What businesses need to know about AI compliance.","category":"⚖️ Law & Regulation"},
      {"title":"The End of the Hype: Welcome to the \"Cost-Per-Task\" AI Economy","link":"ai-cost-per-task-economy.html","description":"Why businesses in 2026 are ditching the AI hype and measuring real ROI. The cost-per-task revolution, SLM rise, and the death of API wrappers explained.","category":"💰 AI Economics"},
      {"title":"The Ethics of AI: What You Need to Know Before Using It","link":"ai-ethics-guide.html","description":"As AI becomes more powerful, ethical concerns grow. Learn about copyright issues, bias in AI models, and how to use artificial intelligence responsibly.","category":"⚖️ Ethics"},
      {"title":"The Future of AI in Digital Marketing: 2026 Trends You Can't Ignore","link":"ai-digital-marketing-trends.html","description":"Discover how artificial intelligence is reshaping digital marketing in 2026. Learn the top trends you need to adapt to stay ahead of the competition.","category":"📈 Marketing"},
      {"title":"The Global AI Hardware Race: How China is Building AI Independence","link":"global-ai-hardware-race-china.html","description":"Analysis of the global AI hardware race in 2026. How China is building cost-conscious AI models despite US chip sanctions, and what it means for the industry.","category":"🌍 Global Tech"},
      {"title":"The Ultimate Guide to AI Updates in 2026","link":"ai-tech-news-2026.html","description":"A comprehensive timeline of the biggest AI releases in 2025 and 2026, including GPT-5, Claude 4, DeepSeek, and Gemini updates.","category":"📈 Timeline"},
      {"title":"The Ultimate Guide to SEO Optimization Using AI Tools","link":"ai-seo-optimization-guide.html","description":"Rank higher on Google with less effort. Learn how to use AI tools for keyword research, content briefs, and on-page SEO optimization.","category":"🔍 SEO"},
      {"title":"Top 5 AI Video Editors That Will Replace Premiere Pro","link":"ai-video-editors.html","description":"Editing video is tedious. Discover the 5 best AI video editors that auto-cut silences, generate captions, and apply b-roll automatically.","category":"🎬 Video Editing"},
      {"title":"What is Agentic Coding? The Rise of Autonomous AI Developers","link":"agentic-coding-future.html","description":"Learn about Vibe Coding and Agentic Coding. How AI agents are writing, testing, and deploying entire applications autonomously in 2026.","category":"💻 Programming"},
      {"title":"Why Anthropic is Beating OpenAI in the Enterprise Market","link":"anthropic-claude-surpasses-openai.html","description":"Discover why businesses are choosing Claude over ChatGPT in 2026. Anthropic's dreaming technique, safety focus, and enterprise strategy explained.","category":"📈 Business AI"},
      {"title":"Google Gemini Omni: Edit Any Video With Just Your Words","link":"gemini-omni-video-revolution.html","description":"Google unveils Gemini Omni at I/O 2026, a revolutionary AI model that lets you edit and generate videos using natural language conversation.","category":"🎬 Video AI"},
      {"title":"KPMG Gives Claude AI to All 276,000 Employees: What Happens Next?","link":"kpmg-claude-276000-employees.html","description":"The biggest enterprise AI deployment in consulting history. KPMG partners with Anthropic to deploy Claude globally.","category":"🏢 Enterprise"},
      {"title":"Samsung's HBM4E: The Tiny Chip That Powers the Entire AI Revolution","link":"samsung-hbm4e-ai-memory-chips.html","description":"Samsung ships the world's first 12-layer HBM4E memory chips with 3.6 TB/s bandwidth. The most important AI hardware breakthrough of 2026.","category":"🔧 Hardware"},
      {"title":"6G is Coming: How Samsung & LG Are Building the AI-Native Internet","link":"6g-samsung-lg-ai-native-networks.html","description":"Samsung and LG partner to develop 6G networks with integrated sensing and AI-native communication technology.","category":"📡 Next-Gen Tech"},
      {"title":"OpenAI's DeployCo: A $4 Billion Army of AI Engineers for Hire","link":"openai-deployco-enterprise-consulting.html","description":"OpenAI launches a standalone subsidiary to embed AI engineers inside Fortune 500 companies. The deployment race begins.","category":"🚀 Breaking"}
    ];
    
    const currentFileName = window.location.pathname.split('/').pop();
    const availableArticles = allArticles.filter(a => a.link !== currentFileName);
    
    // Pick stable internal links so article recommendations do not shift between visits.
    const selected = availableArticles
      .map((article, index) => ({ article, score: article.category.length + article.title.length + index }))
      .sort((a, b) => b.score - a.score)
      .slice(0, 3)
      .map(({ article }) => article);
    
    const relatedDiv = document.createElement('div');
    relatedDiv.className = 'related-articles animate-in';
    relatedDiv.innerHTML = '<h3>Read Next</h3><div class="related-grid"></div>';
    
    const grid = relatedDiv.querySelector('.related-grid');
    selected.forEach(article => {
      const card = document.createElement('a');
      card.href = article.link;
      card.className = 'related-card';
      card.innerHTML = `<h4>${article.title}</h4><span class="read-more">Read Article →</span>`;
      grid.appendChild(card);
    });
    
    articleContent.appendChild(relatedDiv);
  }
});
