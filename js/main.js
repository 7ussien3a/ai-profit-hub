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
      { title: "10 Best Free AI Tools for Students in 2026", link: "best-free-ai-tools-students.html" },
      { title: "15 ChatGPT Prompts That Will Double Your Productivity", link: "chatgpt-prompts-productivity.html" },
      { title: "7 Must-Have AI Chrome Extensions to Save Hours", link: "ai-chrome-extensions.html" },
      { title: "How to Make Money with AI Art", link: "make-money-ai-art.html" },
      { title: "Is AI Going to Steal Your Job? The Truth in 2026", link: "ai-stealing-jobs-truth.html" },
      { title: "How to Build a Custom GPT for Your Business", link: "custom-gpt-business.html" }
    ];
    
    const currentFileName = window.location.pathname.split('/').pop();
    const availableArticles = allArticles.filter(a => a.link !== currentFileName);
    
    // Pick 3 random articles
    const shuffled = availableArticles.sort(() => 0.5 - Math.random());
    const selected = shuffled.slice(0, 3);
    
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
