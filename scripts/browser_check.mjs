#!/usr/bin/env node
/**
 * browser_check.mjs — headless verification of the customer index.html.
 *
 * Drives the built artifact in Chromium and asserts the things a static
 * check can't see: no console errors, no horizontal overflow at desktop or
 * 390px mobile, the interactive engine actually populates (galleries, grid,
 * ladder, pool table), the lightbox opens/steps/closes by keyboard, the
 * condition toggle re-renders the estimate, and the table-of-contents anchors
 * resolve. Saves evidence screenshots to evidence/.
 *
 * Requires Playwright + Chromium. If not installed in this repo, install once:
 *   mkdir -p /tmp/pw && cd /tmp/pw && npm i playwright && npx playwright install chromium
 * then run from the repo root with a local server already serving index.html:
 *   python3 -m http.server 8817 &
 *   NODE_PATH=/tmp/pw/node_modules node scripts/browser_check.mjs http://localhost:8817/index.html
 */
import { mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

// Resolve Playwright from PW_PATH (e.g. /tmp/pw) or the local node_modules.
const require = createRequire(import.meta.url);
const pwBase = process.env.PW_PATH || process.cwd();
const { chromium } = require(require.resolve('playwright', { paths: [pwBase, process.cwd()] }));

const URL = process.argv[2] || 'http://localhost:8817/index.html';
const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const EV = resolve(ROOT, 'evidence');
mkdirSync(EV, { recursive: true });

const results = [];
let failed = 0;
function check(name, cond, detail = '') {
  const ok = !!cond;
  if (!ok) failed++;
  results.push({ name, ok, detail });
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${name}${detail ? '  — ' + detail : ''}`);
}

const browser = await chromium.launch();

async function newPage(opts) {
  const ctx = await browser.newContext(opts);
  const errors = [];
  ctx.on('weberror', e => errors.push('pageerror: ' + e.error().message));
  return { ctx, errors };
}

// Capture console + page errors on a page bound to an error sink.
function bindConsole(page, errors) {
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
}

async function overflow(page) {
  return page.evaluate(() => {
    const de = document.documentElement;
    return { scrollW: de.scrollWidth, clientW: de.clientWidth,
             over: de.scrollWidth - de.clientWidth };
  });
}

/* ---------- desktop ---------- */
{
  const { ctx, errors } = await newPage({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  bindConsole(page, errors);
  await page.goto(URL, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(400);

  // engine populated?
  const counts = await page.evaluate(() => ({
    gal: document.querySelectorAll('#gal .gitem').length,
    twin: document.querySelectorAll('#twingal .shot').length,
    cards: document.querySelectorAll('#gridcards .panel').length,
    gridRows: document.querySelectorAll('#gridtable tbody tr').length,
    ladder: document.querySelectorAll('#ladder .lrow').length,
    pool: document.querySelectorAll('#pooltable tbody tr').length,
    qtr: document.querySelectorAll('#qtrchart svg').length,
    scatter: document.querySelectorAll('#scatter svg').length,
    recon: (document.querySelector('#recon') || {}).textContent,
    mD: (document.querySelector('#mD') || {}).textContent,
  }));
  check('gallery populated', counts.gal > 0, counts.gal + ' items');
  check('twin strip populated', counts.twin > 0, counts.twin + ' photos');
  check('comp cards populated', counts.cards === 6, counts.cards + ' cards');
  check('adjustment grid rows', counts.gridRows > 8, counts.gridRows + ' rows');
  check('value ladder rows', counts.ladder === 6, counts.ladder + ' rows');
  check('pool table rows', counts.pool > 0, counts.pool + ' rows');
  check('quarterly chart drawn', counts.qtr === 1);
  check('scatter chart drawn', counts.scatter === 1);
  check('reconciled estimate shows $814,000', counts.recon === '$814,000', counts.recon);
  check('method D shows $848,000', counts.mD === '$848,000', counts.mD);

  const ov = await overflow(page);
  check('no horizontal overflow @1280', ov.over <= 1, `scrollW ${ov.scrollW} vs clientW ${ov.clientW}`);

  // condition toggle re-renders the estimate
  await page.click('#condtoggle button[data-state="fixed"]');
  await page.waitForTimeout(200);
  const reconFixed = await page.textContent('#recon');
  check('condition toggle updates estimate', reconFixed && reconFixed !== counts.recon, `as-is ${counts.recon} → fixed ${reconFixed}`);
  await page.click('#condtoggle button[data-state="asis"]');
  await page.waitForTimeout(150);

  // GLA toggle updates method D basis
  await page.click('#glaseg button[data-gla="1532"]');
  await page.waitForTimeout(150);
  const mD1532 = await page.textContent('#mD');
  check('GLA toggle moves method D', mD1532 !== counts.mD, `1832→${counts.mD} / 1532→${mD1532}`);
  await page.click('#glaseg button[data-gla="1832"]');
  await page.waitForTimeout(150);

  // TOC anchors resolve to real sections
  const badAnchors = await page.evaluate(() => {
    const bad = [];
    document.querySelectorAll('.toc a[href^="#"]').forEach(a => {
      const id = a.getAttribute('href').slice(1);
      if (!document.getElementById(id)) bad.push(id);
    });
    return bad;
  });
  check('all TOC anchors resolve', badAnchors.length === 0, badAnchors.join(','));

  // lightbox: open first gallery item, step, keyboard-close
  await page.click('#gal .gitem');
  await page.waitForTimeout(200);
  let lbOpen = await page.evaluate(() => document.getElementById('lb').open);
  check('lightbox opens on gallery click', lbOpen);
  await page.keyboard.press('Escape');
  await page.waitForTimeout(150);
  lbOpen = await page.evaluate(() => document.getElementById('lb').open);
  check('lightbox closes on Escape', !lbOpen);

  // lightbox arrow-key nav on a multi-photo comp strip
  await page.click('#gridcards .strip .shot');
  await page.waitForTimeout(200);
  const before = await page.textContent('#lbcount');
  await page.keyboard.press('ArrowRight');
  await page.waitForTimeout(150);
  const after = await page.textContent('#lbcount');
  check('lightbox arrow-key steps photos', before !== after, `${before} → ${after}`);
  await page.keyboard.press('Escape');

  check('no console/page errors @desktop', errors.length === 0, errors.slice(0, 4).join(' | '));

  await page.screenshot({ path: resolve(EV, 'desktop-top.png'), clip: { x: 0, y: 0, width: 1280, height: 900 } });
  await page.screenshot({ path: resolve(EV, 'desktop-full.png'), fullPage: true });
  await ctx.close();
}

/* ---------- mobile 390px ---------- */
{
  const { ctx, errors } = await newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true });
  const page = await ctx.newPage();
  bindConsole(page, errors);
  await page.goto(URL, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(400);
  const ov = await overflow(page);
  check('no horizontal overflow @390', ov.over <= 1, `scrollW ${ov.scrollW} vs clientW ${ov.clientW}`);
  check('no console/page errors @mobile', errors.length === 0, errors.slice(0, 4).join(' | '));
  await page.screenshot({ path: resolve(EV, 'mobile-top.png'), clip: { x: 0, y: 0, width: 390, height: 844 } });
  await page.screenshot({ path: resolve(EV, 'mobile-full.png'), fullPage: true });
  await ctx.close();
}

/* ---------- reduced motion ---------- */
{
  const { ctx, errors } = await newPage({ viewport: { width: 1280, height: 900 }, reducedMotion: 'reduce' });
  const page = await ctx.newPage();
  bindConsole(page, errors);
  await page.goto(URL, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(300);
  const smooth = await page.evaluate(() => getComputedStyle(document.documentElement).scrollBehavior);
  check('reduced-motion disables smooth scroll', smooth === 'auto', 'scroll-behavior=' + smooth);
  check('no console/page errors @reduced-motion', errors.length === 0, errors.slice(0, 4).join(' | '));
  await ctx.close();
}

await browser.close();
console.log(`\n${results.length - failed}/${results.length} checks passed`);
process.exit(failed ? 1 : 0);
