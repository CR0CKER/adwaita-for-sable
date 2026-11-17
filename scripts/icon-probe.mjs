#!/usr/bin/env node
// Icon-alignment probe for a running Sable (started with --remote-debugging-port=9333).
// Checks every visible icon on the current screen, once with the theme and once
// as stock Sable (theme stylesheet disabled, body's remote-theme class removed,
// both restored afterwards), and prints the findings the theme adds:
//   - an icon that overflows its parent box (the presence dot in #4);
//   - an icon off its label's centre line, in a horizontal flex row;
//   - a menu whose leading icons don't share one column;
//   - a row of 3+ icon-only buttons whose icons differ in size or centre line.
// Open the menu, panel or page to check first; run at each width that matters.
//   node scripts/icon-probe.mjs          theme-only findings (exit 1 if any)
//   node scripts/icon-probe.mjs --all    also findings stock Sable has too
import { connect } from './lib/cdp.mjs';

// Runs in the page; returns [{ where, label, issues[] }].
function probe() {
  const out = [];
  const vis = (e) => {
    const r = e.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) return null;
    if (r.bottom < 0 || r.right < 0 || r.top > innerHeight || r.left > innerWidth) return null;
    for (let a = e; a && a.nodeType === 1; a = a.parentElement) {
      const c = getComputedStyle(a);
      if (c.visibility === 'hidden' || c.opacity === '0' || c.display === 'none') return null;
    }
    return r;
  };
  // Semantic classes only: svelte-* hashes change with every Sable build.
  const path = (e) => {
    const p = [];
    for (let a = e; a && a !== document.body && p.length < 5; a = a.parentElement) {
      const cls = (a.className?.baseVal ?? a.className ?? '').toString().split(/\s+/)
        .filter((c) => c && !c.startsWith('svelte-')).slice(0, 2).join('.');
      p.unshift(a.tagName.toLowerCase() + (cls ? '.' + cls : ''));
    }
    return p.join(' > ');
  };
  const label = (e) => (e.closest('[aria-label],[title]')?.getAttribute('aria-label')
    || e.closest('button,a,[role=menuitem],[role=tab],li,label')?.textContent || '').trim().slice(0, 40);

  for (const s of [...document.querySelectorAll('svg')].filter((x) => !x.parentElement.closest('svg'))) {
    const r = vis(s);
    if (!r || r.width > 80 || r.height > 80) continue; // illustrations, not icons
    const issues = [];
    const parent = s.parentElement, pr = parent.getBoundingClientRect(), pc = getComputedStyle(parent);
    const o = Math.max(pr.left - r.left, r.right - pr.right, pr.top - r.top, r.bottom - pr.bottom);
    if (o > 1 && pr.width > 0 && pr.height > 0 && pc.display !== 'contents')
      issues.push(`overflow ${o.toFixed(1)}px of ${pr.width.toFixed(0)}x${pr.height.toFixed(0)} parent`);
    // Climb single-child wrappers to the flex row, then compare with the first text sibling's first line.
    let row = s;
    while (row.parentElement && !getComputedStyle(row.parentElement).display.includes('flex')
      && row.parentElement.children.length === 1) row = row.parentElement;
    const rp = row.parentElement, rc = rp && getComputedStyle(rp);
    if (rc && rc.display.includes('flex') && !rc.flexDirection.startsWith('column')) {
      const sib = [...rp.children].find((c) => c !== row && !c.querySelector('svg') && c.textContent.trim()
        && vis(c) && getComputedStyle(c).display !== 'contents');
      if (sib) {
        const range = document.createRange(); range.selectNodeContents(sib);
        const lr = range.getClientRects()[0] ?? sib.getBoundingClientRect();
        const d = (r.top + r.height / 2) - (lr.top + lr.height / 2);
        if (Math.abs(d) > 1.5 && lr.height < 40) issues.push(`v-offset ${d.toFixed(1)}px vs "${sib.textContent.trim().slice(0, 20)}"`);
      }
    }
    if (issues.length) out.push({ where: path(s), label: label(s), issues });
  }

  for (const m of document.querySelectorAll('.menu-surface,[role=menu],[role=listbox]')) {
    if (!vis(m)) continue;
    const cols = [];
    for (const it of m.querySelectorAll('[role=menuitem],[role=menuitemradio],[role=menuitemcheckbox],[role=option],.menu-item')) {
      const ir = vis(it); if (!ir) continue;
      const first = [...it.querySelectorAll('svg,img,.presence-dot,.avatar-root')].find((e) => !e.parentElement.closest('svg') && vis(e));
      if (!first) continue;
      const fr = first.getBoundingClientRect();
      if (fr.left - ir.left > 40) continue; // a trailing icon only
      cols.push({ t: it.textContent.trim().slice(0, 25), cx: +((fr.left + fr.width / 2) - ir.left).toFixed(1) });
    }
    const cx = cols.map((c) => c.cx);
    if (cx.length > 1 && Math.max(...cx) - Math.min(...cx) > 1.5)
      out.push({ where: path(m), label: 'menu icon column', issues: cols.map((c) => `${c.t}: centre ${c.cx}`) });
  }

  const seen = new Set();
  for (const b of document.querySelectorAll('button, [role=button], a')) {
    const g = b.parentElement; if (!g || seen.has(g)) continue; seen.add(g);
    const icons = [...g.children]
      .filter((c) => c.matches('button,[role=button],a') && vis(c) && !c.textContent.trim())
      .map((c) => { const sv = [...c.querySelectorAll('svg')].find((x) => !x.parentElement.closest('svg') && vis(x));
        return sv && { l: c.getAttribute('aria-label') || '', r: sv.getBoundingClientRect() }; })
      .filter(Boolean);
    if (icons.length < 3) continue;
    const tops = icons.map((i) => i.r.top);
    if (Math.max(...tops) - Math.min(...tops) > 30) continue; // wrapped, not one row
    const cys = icons.map((i) => i.r.top + i.r.height / 2), ws = icons.map((i) => i.r.width);
    if (Math.max(...cys) - Math.min(...cys) > 1.5 || Math.max(...ws) - Math.min(...ws) > 0.5)
      out.push({ where: path(g), label: 'button row', issues: icons.map((i) => `${i.l}: ${i.r.width.toFixed(1)}px, centre ${(i.r.top + i.r.height / 2).toFixed(1)}`) });
  }
  return out;
}

const all = process.argv.includes('--all');
const cdp = await connect(Number(process.env.SABLE_PORT ?? 9333));
const run = async () => JSON.parse(await cdp.evaluate(`JSON.stringify((${probe})())`));
const setStock = (stock) => cdp.evaluate(`(() => {
  const s = document.getElementById('sable-custom-theme'); if (s) s.disabled = ${stock};
  document.body.classList.toggle('remote-theme', ${!stock}); return 1; })()`);
try {
  const themed = await run();
  await setStock(true);
  let stock;
  try { stock = await run(); } finally { await setStock(false); }
  // Compare by place and kind of issue, not by the measured numbers.
  const key = (o) => `${o.where}|${o.label}|${o.issues.map((i) => i.replace(/[-\d.]+.*/, '')).join(',')}`;
  const inStock = new Set(stock.map(key));
  const theme = themed.filter((o) => !inStock.has(key(o)));
  const both = themed.filter((o) => inStock.has(key(o)));
  const print = (title, list) => {
    console.log(`${title}: ${list.length}`);
    for (const o of list) console.log(`  ${o.label} (${o.where})\n    ${o.issues.join('\n    ')}`);
  };
  print('Added by the theme', theme);
  if (all) print('Also in stock Sable', both);
  process.exitCode = theme.length ? 1 : 0;
} finally {
  cdp.close();
}
