import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();

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

const issues = [];

for (const file of htmlFiles) {
  const html = fs.readFileSync(file, 'utf8');
  const rel = path.relative(root, file);
  const skipLinks = html.match(/class="skip-link"/g) || [];
  const mainTags = html.match(/<main\b/g) || [];
  const schema = html.match(/<script type="application\/ld\+json" data-schema="primary">([\s\S]*?)<\/script>/);

  if (skipLinks.length !== 1) issues.push(`${rel}: expected 1 skip link, found ${skipLinks.length}`);
  if (mainTags.length !== 1) issues.push(`${rel}: expected 1 main element, found ${mainTags.length}`);
  if (!schema) {
    issues.push(`${rel}: missing primary JSON-LD`);
  } else {
    try {
      JSON.parse(schema[1]);
    } catch (error) {
      issues.push(`${rel}: invalid JSON-LD (${error.message})`);
    }
  }
}

const sitemap = fs.readFileSync(path.join(root, 'sitemap.xml'), 'utf8');
if (/C:\\/i.test(sitemap) || /مشروع/.test(sitemap)) {
  issues.push('sitemap.xml contains a local filesystem path');
}

const robotsPath = path.join(root, 'robots.txt');
if (!fs.existsSync(robotsPath)) {
  issues.push('robots.txt is missing');
} else if (!fs.readFileSync(robotsPath, 'utf8').includes('Sitemap: https://ai-profit-hub.com/sitemap.xml')) {
  issues.push('robots.txt does not reference the production sitemap');
}

if (issues.length) {
  console.error(issues.join('\n'));
  process.exit(1);
}

console.log(`Validated ${htmlFiles.length} HTML files, sitemap.xml, and robots.txt.`);
