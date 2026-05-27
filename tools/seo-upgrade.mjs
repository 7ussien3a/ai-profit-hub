import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const baseUrl = 'https://ai-profit-hub.com';
const today = '2026-05-27';

const walk = (dir) => {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  return entries.flatMap((entry) => {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) return walk(full);
    return full;
  });
};

const htmlFiles = walk(root)
  .filter((file) => file.endsWith('.html'))
  .filter((file) => !file.includes(`${path.sep}.git${path.sep}`));

const relUrl = (file) => {
  const rel = path.relative(root, file).replaceAll(path.sep, '/');
  return rel === 'index.html' ? '/' : `/${rel}`;
};

const get = (html, pattern, fallback = '') => {
  const match = html.match(pattern);
  return match ? match[1].trim() : fallback;
};

const stripTags = (value) => value.replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();

const cleanTitle = (title) => stripTags(title).replace(/\s+[—-]\s+AI Profit Hub$/i, '').trim();

const getMetaContent = (html, attrName, attrValue) => {
  const tags = html.match(/<meta\b[^>]*>/gi) || [];
  const wanted = new RegExp(`\\b${attrName}=["']${attrValue}["']`, 'i');
  for (const tag of tags) {
    if (!wanted.test(tag)) continue;
    const doubleQuoted = tag.match(/\bcontent="([^"]*)"/i);
    const singleQuoted = tag.match(/\bcontent='([^']*)'/i);
    return (doubleQuoted?.[1] || singleQuoted?.[1] || '').trim();
  }
  return '';
};

const insertBeforeHeadEnd = (html, block) => html.replace(/\s*<\/head>/i, `\n${block}\n</head>`);

const upsertMetaName = (html, name, content) => {
  const escaped = content.replaceAll('"', '&quot;');
  const tag = `<meta name="${name}" content="${escaped}">`;
  const re = new RegExp(`<meta\\s+name=["']${name}["'][^>]*>`, 'i');
  return re.test(html) ? html.replace(re, tag) : html.replace(/<title>[\s\S]*?<\/title>/i, `$&\n  ${tag}`);
};

const upsertMetaProperty = (html, property, content) => {
  const escaped = content.replaceAll('"', '&quot;');
  const tag = `<meta property="${property}" content="${escaped}">`;
  const re = new RegExp(`<meta\\s+property=["']${property}["'][^>]*>`, 'i');
  return re.test(html) ? html.replace(re, tag) : html.replace(/<meta\s+name=["']description["'][^>]*>/i, `$&\n  ${tag}`);
};

const upsertLink = (html, rel, href, attrs = '') => {
  const tag = `<link rel="${rel}" href="${href}"${attrs}>`;
  const re = new RegExp(`<link\\s+rel=["']${rel}["'][^>]*href=["']${href.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}["'][^>]*>`, 'i');
  return re.test(html) ? html : html.replace(/<meta\s+name=["']viewport["'][^>]*>/i, `$&\n  ${tag}`);
};

const makeSchema = (file, html) => {
  const url = `${baseUrl}${relUrl(file)}`;
  const title = cleanTitle(get(html, /<title>([\s\S]*?)<\/title>/i, 'AI Profit Hub'));
  const description = getMetaContent(html, 'name', 'description');
  const h1 = stripTags(get(html, /<h1[^>]*>([\s\S]*?)<\/h1>/i, title));
  const image = get(html, /<img[^>]+src=["']([^"']+)["'][^>]*>/i).replaceAll('&amp;', '&');
  const isArticle = relUrl(file).startsWith('/articles/');
  const graph = [
    {
      '@type': 'Organization',
      '@id': `${baseUrl}/#organization`,
      name: 'AI Profit Hub',
      url: baseUrl,
      contactPoint: {
        '@type': 'ContactPoint',
        email: 'contact@ai-profit-hub.com',
        contactType: 'editorial support'
      }
    },
    {
      '@type': 'WebSite',
      '@id': `${baseUrl}/#website`,
      url: baseUrl,
      name: 'AI Profit Hub',
      publisher: { '@id': `${baseUrl}/#organization` },
      inLanguage: 'en'
    }
  ];

  if (isArticle) {
    const date = getMetaContent(html, 'property', 'article:published_time') || today;
    graph.push({
      '@type': 'BlogPosting',
      '@id': `${url}#article`,
      headline: h1,
      description,
      image: image ? [image] : undefined,
      datePublished: date,
      dateModified: today,
      author: { '@type': 'Organization', name: 'AI Profit Hub' },
      publisher: { '@id': `${baseUrl}/#organization` },
      mainEntityOfPage: url,
      inLanguage: 'en'
    });
  } else {
    graph.push({
      '@type': relUrl(file) === '/' ? 'CollectionPage' : 'WebPage',
      '@id': `${url}#webpage`,
      url,
      name: title,
      description,
      isPartOf: { '@id': `${baseUrl}/#website` },
      inLanguage: 'en'
    });
  }

  graph.push({
    '@type': 'BreadcrumbList',
    '@id': `${url}#breadcrumb`,
    itemListElement: relUrl(file) === '/'
      ? [{ '@type': 'ListItem', position: 1, name: 'Home', item: baseUrl }]
      : [
          { '@type': 'ListItem', position: 1, name: 'Home', item: baseUrl },
          { '@type': 'ListItem', position: 2, name: isArticle ? 'Articles' : title, item: url }
        ]
  });

  return JSON.stringify({ '@context': 'https://schema.org', '@graph': graph }, null, 2)
    .replace(/"image": undefined,\n/g, '');
};

const articleMeta = [];

for (const file of htmlFiles) {
  let html = fs.readFileSync(file, 'utf8');
  const url = `${baseUrl}${relUrl(file)}`;
  const depth = path.relative(root, file).split(path.sep).length - 1;
  const prefix = depth ? '../'.repeat(depth) : '';
  const title = cleanTitle(get(html, /<title>([\s\S]*?)<\/title>/i, 'AI Profit Hub'));
  const description = getMetaContent(html, 'name', 'description');
  const firstImage = get(html, /<img[^>]+src=["']([^"']+)["'][^>]*>/i);

  html = html.replace(/<script[^>]+data-schema=["']primary["'][\s\S]*?<\/script>\s*/gi, '');
  html = upsertLink(html, 'preconnect', 'https://images.unsplash.com');
  html = upsertLink(html, 'preconnect', 'https://pagead2.googlesyndication.com');
  html = upsertMetaName(html, 'theme-color', '#0A0E1A');
  html = upsertMetaName(html, 'format-detection', 'telephone=no');
  html = upsertMetaProperty(html, 'og:site_name', 'AI Profit Hub');
  html = upsertMetaProperty(html, 'og:url', url);
  if (firstImage) {
    html = upsertMetaProperty(html, 'og:image', firstImage);
    html = upsertMetaName(html, 'twitter:image', firstImage);
  }
  html = upsertMetaName(html, 'twitter:card', firstImage ? 'summary_large_image' : 'summary');
  html = upsertMetaName(html, 'twitter:title', title);
  if (description) html = upsertMetaName(html, 'twitter:description', description);

  html = html.replace(/\s*<a class="skip-link" href="#main-content">Skip to content<\/a>/gi, '');
  html = html.replace(/<body>/i, `<body>\n  <a class="skip-link" href="#main-content">Skip to content</a>`);
  html = html.replace(/<main(?![^>]*\sid=)/i, '<main id="main-content"');
  html = html.replace(/<div class="page-content">/i, '<main id="main-content" class="page-content">');
  html = html.replace(/<\/div>\s*(\n\s*<footer class="footer">)/i, '</main>$1');
  html = html.replace(/<div class="article-page">/i, '<main id="main-content" class="article-page">');
  html = html.replace(/<\/div>\s*(\n\s*<footer class="footer">)/i, '</main>$1');

  html = html.replace(/<ul class="nav-links"(?![^>]*\sid=)/g, '<ul class="nav-links" id="navLinks"');
  html = html.replace(/<button class="mobile-toggle"(?![^>]*type=)/g, '<button class="mobile-toggle" type="button"');
  html = html.replace(/<button class="mobile-toggle" type="button"([^>]*)aria-label="Toggle menu"/g, '<button class="mobile-toggle" type="button"$1aria-label="Toggle menu" aria-controls="navLinks" aria-expanded="false"');

  html = html.replace(/<script src="([^"]*js\/main\.js)"><\/script>/g, '<script src="$1" defer></script>');

  let imageIndex = 0;
  html = html.replace(/<img\b([^>]*?)>/gi, (match, attrs) => {
    imageIndex += 1;
    let next = `<img${attrs}>`;
    if (!/\bdecoding=/.test(next)) next = next.replace(/>$/, ' decoding="async">');
    if (!/\bloading=/.test(next)) next = next.replace(/>$/, imageIndex === 1 ? ' loading="eager">' : ' loading="lazy">');
    if (imageIndex === 1 && !/\bfetchpriority=/.test(next)) next = next.replace(/>$/, ' fetchpriority="high">');
    if (/\bclass=["'][^"']*article-card-image/.test(next) && !/\bwidth=/.test(next)) next = next.replace(/>$/, ' width="800" height="450">');
    if (/\bclass=["'][^"']*article-cover/.test(next) && !/\bwidth=/.test(next)) next = next.replace(/>$/, ' width="900" height="506">');
    next = next.replace(/images\.unsplash\.com\/([^"']+)\?([^"']*)/g, (full, imgPath, query) => {
      const params = new URLSearchParams(query.replaceAll('&amp;', '&'));
      if (!params.has('auto')) params.set('auto', 'format');
      if (!params.has('fit')) params.set('fit', 'crop');
      return `images.unsplash.com/${imgPath}?${params.toString().replaceAll('&', '&amp;')}`;
    });
    return next;
  });

  html = html.replace(/target="_blank"(?![^>]*rel=)/g, 'target="_blank" rel="noopener noreferrer"');

  const schema = `<script type="application/ld+json" data-schema="primary">\n${makeSchema(file, html)}\n  </script>`;
  html = insertBeforeHeadEnd(html, `  ${schema}`);

  fs.writeFileSync(file, html, 'utf8');

  if (relUrl(file).startsWith('/articles/')) {
    articleMeta.push({
      title: cleanTitle(get(html, /<h1[^>]*>([\s\S]*?)<\/h1>/i, title)),
      link: path.basename(file),
      description,
      category: stripTags(get(html, /<span class="article-card-tag">([\s\S]*?)<\/span>/i, 'AI'))
    });
  }
}

const mainJsPath = path.join(root, 'js', 'main.js');
let mainJs = fs.readFileSync(mainJsPath, 'utf8');
const articleArray = articleMeta
  .sort((a, b) => a.title.localeCompare(b.title))
  .map((article) => `      ${JSON.stringify(article)}`)
  .join(',\n');
mainJs = mainJs.replace(
  /const allArticles = \[[\s\S]*?\n    \];/,
  `const allArticles = [\n${articleArray}\n    ];`
);
mainJs = mainJs.replace(
  /\/\/ Pick 3 random articles[\s\S]*?const selected = shuffled\.slice\(0, 3\);/,
  `// Pick stable internal links so article recommendations do not shift between visits.\n    const selected = availableArticles\n      .map((article, index) => ({ article, score: article.category.length + article.title.length + index }))\n      .sort((a, b) => b.score - a.score)\n      .slice(0, 3)\n      .map(({ article }) => article);`
);
fs.writeFileSync(mainJsPath, mainJs, 'utf8');

const sitemapUrls = htmlFiles
  .map((file) => {
    const urlPath = relUrl(file);
    const priority = urlPath === '/' ? '1.0' : urlPath.startsWith('/articles/') ? '0.8' : '0.7';
    const changefreq = urlPath === '/' || urlPath.startsWith('/articles/') ? 'weekly' : 'monthly';
    return `  <url>\n    <loc>${baseUrl}${urlPath}</loc>\n    <lastmod>${today}</lastmod>\n    <changefreq>${changefreq}</changefreq>\n    <priority>${priority}</priority>\n  </url>`;
  })
  .sort();

fs.writeFileSync(
  path.join(root, 'sitemap.xml'),
  `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${sitemapUrls.join('\n')}\n</urlset>\n`,
  'utf8'
);

fs.writeFileSync(
  path.join(root, 'robots.txt'),
  `User-agent: *\nAllow: /\n\nSitemap: ${baseUrl}/sitemap.xml\n`,
  'utf8'
);
