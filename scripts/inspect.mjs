#!/usr/bin/env node
// Live-inspect a running Sable started with --remote-debugging-port=9333.
//   inspect.mjs eval '<js expression>'      print JSON result
//   inspect.mjs shot <out.png>              screenshot the window
//   inspect.mjs css <file.css>              inject CSS as #adw-dev (live preview, not persisted)
//   inspect.mjs uncss                       remove the #adw-dev preview
import { connect } from './lib/cdp.mjs';
import { readFileSync, writeFileSync } from 'node:fs';

const port = Number(process.env.SABLE_PORT ?? 9333);
const [cmd, arg] = process.argv.slice(2);
const cdp = await connect(port);
try {
  if (cmd === 'eval') {
    console.log(JSON.stringify(await cdp.evaluateJson(`JSON.stringify(${arg})`), null, 1));
  } else if (cmd === 'shot') {
    const { data } = await cdp.call('Page.captureScreenshot', { format: 'png' });
    writeFileSync(arg, Buffer.from(data, 'base64'));
    console.log(arg);
  } else if (cmd === 'click' || cmd === 'hover') {
    // click/hover <css selector> | <x,y>: real input events at the element's centre.
    let [x, y] = /^\d+(\.\d+)?,\d+(\.\d+)?$/.test(arg) ? arg.split(',').map(Number) : [];
    if (x === undefined) {
      const r = JSON.parse(await cdp.evaluate(`JSON.stringify(document.querySelector(${JSON.stringify(arg)})?.getBoundingClientRect())`) ?? 'null');
      if (!r) throw new Error(`no element ${arg}`);
      [x, y] = [r.x + r.width / 2, r.y + r.height / 2];
    }
    await cdp.call('Input.dispatchMouseEvent', { type: 'mouseMoved', x, y });
    if (cmd === 'click') {
      await cdp.call('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', clickCount: 1 });
      await cdp.call('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', clickCount: 1 });
    }
    console.log(`${cmd} ${Math.round(x)},${Math.round(y)}`);
  } else if (cmd === 'upload') {
    // upload <css selector> <file>: hand a file to an <input type=file>, as a
    // file chooser would. The path must be visible inside Sable's sandbox
    // (~/Downloads).
    const file = process.argv[4];
    const { root } = await cdp.call('DOM.getDocument', { depth: 0 });
    const { nodeId } = await cdp.call('DOM.querySelector', { nodeId: root.nodeId, selector: arg });
    if (!nodeId) throw new Error(`no element ${arg}`);
    await cdp.call('DOM.setFileInputFiles', { nodeId, files: [file] });
    console.log(`uploaded ${file}`);
  } else if (cmd === 'key') {
    await cdp.call('Input.dispatchKeyEvent', { type: 'keyDown', key: arg, code: arg, windowsVirtualKeyCode: arg === 'Escape' ? 27 : 0 });
    await cdp.call('Input.dispatchKeyEvent', { type: 'keyUp', key: arg, code: arg, windowsVirtualKeyCode: arg === 'Escape' ? 27 : 0 });
    console.log(`key ${arg}`);
  } else if (cmd === 'theme') {
    // Swap a built .sable.css into Sable's own #sable-custom-theme slot, with the
    // same renames Sable applies on import (function zt in its bundle). Lasts
    // until Sable re-applies its stored theme (a reload or a theme change).
    const renames = { avatar: 'avatar-root', button: 'btn', current: 'selection-current',
      highlight: 'selection-highlight', menu: 'menu-surface', open: 'selection-open',
      progress: 'progress-track', switch: 'switch-root' };
    const css = readFileSync(arg, 'utf8')
      .replace(/--sable-([a-z0-9-]+)/g, (_, t) => (t === 'shadow' ? '--shadow-color' : `--${t}`))
      .replace(/--font-secondary(?![a-z0-9-])/g, '--font-family')
      .replace(/--font-monospace(?![a-z0-9-])/g, '--font-family-mono')
      .replace(/\.sable-([a-z0-9-]+)/g, (_, t) => (renames[t] ? `.${renames[t]}`
        : t.startsWith('button-') ? `.btn-${t.slice(7)}` : `.${t}`));
    const mode = /kind:\s*dark/.test(css) ? 'dark' : 'light';
    await cdp.evaluate(`(() => {
      const s = document.getElementById('sable-custom-theme');
      if (!s) throw new Error('no custom theme slot: select any custom theme first');
      s.textContent = ${JSON.stringify(css)};
      const r = document.documentElement;
      r.classList.toggle('dark', ${JSON.stringify(mode)} === 'dark');
      r.classList.toggle('light', ${JSON.stringify(mode)} === 'light');
      r.dataset.theme = ${JSON.stringify(mode)}; r.style.colorScheme = ${JSON.stringify(mode)};
    })()`);
    console.log(`theme ${mode} applied`);
  } else if (cmd === 'css' || cmd === 'uncss') {
    const css = cmd === 'css' ? readFileSync(arg, 'utf8') : '';
    await cdp.evaluate(`(() => {
      let s = document.getElementById('adw-dev');
      if (!${JSON.stringify(css)}) { s?.remove(); return; }
      if (!s) { s = document.createElement('style'); s.id = 'adw-dev'; document.head.append(s); }
      s.textContent = ${JSON.stringify(css)};
    })()`);
    console.log(cmd === 'css' ? 'injected' : 'removed');
  } else {
    console.error('usage: inspect.mjs eval|shot|css|uncss ...');
    process.exitCode = 2;
  }
} finally {
  cdp.close();
}
