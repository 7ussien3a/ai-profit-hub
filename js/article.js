/* ============================================================
   article.js  —  Shared JavaScript for all article pages
   AI Profit Hub | https://ai-profit-hub.com
   ============================================================ */
(function () {
  'use strict';

  /* ---- Reading progress bar + Back-to-top button ---- */
  var bar = document.getElementById('read-progress');
  var btn = document.getElementById('backTop');

  window.addEventListener('scroll', function () {
    var d = document.documentElement;
    var s = d.scrollTop || document.body.scrollTop;
    var t = d.scrollHeight - d.clientHeight;
    if (bar) bar.style.width = (t > 0 ? s / t * 100 : 0) + '%';
    if (btn) btn.style.opacity = s > 400 ? '1' : '0';
  }, { passive: true });

  /* ---- Copy link button ---- */
  function initCopyLink() {
    var btns = document.querySelectorAll('[data-copy-link], .share-btn-copy');
    btns.forEach(function (b) {
      b.addEventListener('click', function () {
        navigator.clipboard.writeText(window.location.href).then(function () {
          var orig = b.textContent;
          b.textContent = 'Copied!';
          setTimeout(function () { b.textContent = orig; }, 2000);
        });
      });
    });
  }

  /* ---- Smooth scroll for TOC links ---- */
  function initTocScroll() {
    var links = document.querySelectorAll('.toc-list a[href^="#"]');
    links.forEach(function (link) {
      link.addEventListener('click', function (e) {
        var target = document.querySelector(this.getAttribute('href'));
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });
  }

  /* ---- Lazy-load images ---- */
  function initLazyImages() {
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            var img = entry.target;
            if (img.dataset.src) {
              img.src = img.dataset.src;
              img.removeAttribute('data-src');
            }
            io.unobserve(img);
          }
        });
      }, { rootMargin: '200px' });
      document.querySelectorAll('img[data-src]').forEach(function (img) {
        io.observe(img);
      });
    } else {
      // Fallback: load all immediately
      document.querySelectorAll('img[data-src]').forEach(function (img) {
        img.src = img.dataset.src;
      });
    }
  }

  /* ---- Init on DOM ready ---- */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      initCopyLink();
      initTocScroll();
      initLazyImages();
    });
  } else {
    initCopyLink();
    initTocScroll();
    initLazyImages();
  }
})();
