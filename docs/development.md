# Development notes

How Sable's theming works, why the theme is built the way it is, and how to work on it. Everything
here was read from Sable 2.3.9's installed bundle
(`/var/lib/flatpak/app/moe.sable.client/current/active/files/sable/resources/`) or measured in the
running app; re-check it after Sable updates.

## Sable's theme system

- **Format.** A theme is a `.sable.css` file under 1 MiB with a comment header holding
  `@sable-theme` (or `@sable-tweak`) and `id`, `name`, `author`, `description`, `kind: light|dark`,
  `contrast`, `tags`. Settings → Appearance → Themes has one slot for light mode and one for dark;
  *Light or dark* picks which one is shown.
- **Import rewrite.** Sable rewrites the CSS on import (function `zt` in its bundle): `--sable-X`
  becomes `--X` (`--sable-shadow` becomes `--shadow-color`), `.sable-remote-theme` becomes
  `.remote-theme`, and a few `.sable-*` classes are renamed (`button` to `btn`, `menu` to
  `menu-surface`, `avatar` to `avatar-root`, and so on). The CSS goes into
  `<style id="sable-custom-theme">`, and `body` gets the class `remote-theme`.
- **Storage.** Imported themes and the slot choice live in localStorage `sable-custom-themes`
  (`themes[]`, `lightThemeId`, `darkThemeId`). The choice is also synced to the Matrix account
  (`sable-sync-base:a1:moe.sable.next.settings`).
- **Tokens.** Colours are tokens on `html`: `bg-*`, `surface-*`, `surface-var-*`, `primary-*`,
  `sec-*`, `success-*`, `warn-*`, `crit-*`, each as `-container/-hover/-active/-line/on-*`, plus
  `focus-ring`, `shadow-color` and `overlay`. Spacing, radii, control heights, font sizes, icon
  sizes, `--header-height` and `--titlebar-height` are tokens too.
- **`var()` chains.** `--font-family`, `--font-family-mono` and `--radius` are defined on `:root` as
  `var()` chains, and a custom property resolves where it is declared. So a theme on `body` sets both
  the alias and its base (`--font-family` and `--font-family-base`). The `--font-size-*` tokens are
  also redeclared on `.text-scale-scope`, so the theme sets them there too.
- **Markup.** The UI is Svelte. Elements carry semantic classes (`rail`, `nav-tab`, `room-nav`,
  `room-row`, `rooms-heading`, `panel-header`, `room-identity`, `room-topic`, `members-drawer`,
  `composer`, `menu-surface`, `menu-item`, `tooltip`, `form-control`, `switch-root`, `switcher`,
  `settings-*`, `titlebar`) plus `svelte-xxxxxx` hashes that change with every build. The theme never
  selects hashes, and `scripts/build.py` refuses a build that does. A plain `<a>` carries only a hash,
  so it is matched as "an `a` whose single class starts with `svelte-`":
  `a[class^="svelte-"]:not([class*=" "])`.
- **One accent token.** `--primary-main` serves both as fill (buttons, switches, badges: 73 uses) and
  as text (links, accent labels: about 30). The theme keeps it as the fill and lists the text uses in
  structure.css's "Accent as text" block. After a Sable update, find new text uses with
  `grep -E '[{;]color:var\(--primary-main\)'` over `dist/_app/immutable/assets/*.css`.
- **Scrollbars.** Sable styles `::-webkit-scrollbar`. Setting the standard `scrollbar-width` or
  `scrollbar-color` anywhere switches Chromium to its classic scrollbars, arrow buttons included, and
  overrides Sable's `.scrollbar-hidden`. Don't.
- **Window decoration.** With Settings → Desktop app → *Use Sable's title bar* (client decorations),
  `<html data-client-decorations="desktop">` and a fixed `.titlebar` (`.drag` with the title, then
  `.controls` with Minimise, Maximise and `.close`). Sable pushes the layout down through
  `--safe-top = safe-area-inset-top + --titlebar-height (2rem)`. With the native frame,
  `--titlebar-height` is 0 and there is no `.titlebar`.
- **Sandbox.** The Flatpak can read `~/Downloads` (`xdg-download`) and nothing else of the home folder.
- **Launcher.** `/app/bin/sable` passes its arguments to Electron, so
  `flatpak run moe.sable.client --remote-debugging-port=9333` exposes the Chrome DevTools Protocol.

## Design decisions

- **Values come from libadwaita, not from memory.** Colours and metrics were extracted from
  `/usr/lib64/libadwaita-1.so.0`
  (`gresource extract … /org/gnome/Adwaita/styles/default.css`): surfaces, the 36px/9px sidebar rows,
  34px buttons and entries, 15px popovers, 32px menu rows, 12px cards, toggle groups, switches,
  tooltips and overlay scrollbars.
- **Surfaces.** The room list is `sidebar_bg_color`, and the space rail is `secondary_sidebar_bg_color`:
  the outer pane of a nested split view, with `sidebar_border_color` shade lines between the panes and
  at the content edge. The room view is `view_bg_color`, and the side panels (members, threads,
  search, media, widgets) share it, set off by a hairline in the border colour. Settings content is
  `window_bg_color`.
- **States.** Hover, active and selected are GTK's `alpha(currentColor, x)` tints, translucent so
  they read the same on every surface. Sidebar selection is neutral (10%), never the accent.
  A hovered timeline message gets libadwaita's activatable-card lift (3%) on a 12px box inset 8px,
  drawn as `::before` because the row carries the avatar gutter in its padding.
- **Accent.** libadwaita fills with the system accent unchanged in both modes (`#c88800` for yellow),
  and writes accent text in an oklab-clamped standalone tone (lightness ≤ 0.5 in light mode, ≥ 0.85 in
  dark). This differs from Adwaita for Tine and Logseq, which also clamp the fill (light fills came
  out brown); Sable follows libadwaita exactly.
- **No hover motion.** Sable nudges rail tiles 2px right and bottom tools 3px up on hover (off only
  with its reduced-motion setting). GNOME buttons don't move, so the theme sets `transform: none`.
- **Icon size.** GNOME's symbolic icons are 16px but filled. Sable's icons are thin outlines, which
  match Files' optical size at 20px (the measurement made for Adwaita for Tine). Menu icons are 18px.
- **Icon glyphs stay Sable's (decided 2026-11-15).** Sable's icons are Phosphor (`phosphor-svelte`),
  with the weight chosen in JS per icon and no name or class on the `<svg>`. A swap to Adwaita
  symbolics is possible: match a glyph by its path data (`svg:has(> path[d^="M229.66,218.34…"])`),
  hide its children and paint the Adwaita icon as a 16px `-webkit-mask`. A live prototype worked, but
  only a whole-app swap looks consistent, several GNOME app icons (gear, paper plane, chat, members)
  are not in the system Adwaita set, and those icons are CC-BY-SA/LGPL (the theme is MIT).
- **Scrollbar fade.** A registered, non-inheriting `@property --adw-sb` holds the slider colour.
  `*:hover` sets it, and the thumb takes it from its own element with `inherit`, so hovering an
  ancestor doesn't light up every nested scrollbar. The two universal rules sit in `:where()`:
  `transition` is a shorthand, so a weighted `*` rule replaced Sable's own transitions (0.2.0 did). It fades in on hover and out 0.6s after the
  pointer leaves. CSS can't detect scrolling itself, so unlike GTK it doesn't show on wheel scrolling
  alone.
- **Window decoration.** GNOME apps have no title strip: `--titlebar-height` and `--safe-top` go to 0,
  the `.titlebar` becomes a transparent overlay holding only the close button, and the header bars get
  `-webkit-app-region: drag` (their buttons, links and inputs `no-drag`). The button is a 24px circle,
  13px from the edge, with GTK's `window-close-symbolic` as a mask. It is close only, matching GNOME's
  default `appmenu:close` (CSS can't read the GNOME setting). To show all three buttons, drop the
  `button:not(.close) { display: none }` rule, style the other two like `.close`, and set
  `--adw-wc-width` to 91px.
- **Drag areas and the close button.** Electron applies `-webkit-app-region` areas in document order,
  and `.titlebar` comes before the header bars, so their `drag` overrides the button's `no-drag` and
  swallows real clicks. Each draggable header bar has an `::after` strip (no-drag, `--adw-wc-width`
  + 6px) at its right end, which comes after it and cuts the button out. It is absolute, not fixed:
  `.drawer-track` (`will-change: transform`) and `.room-view` (a size container) trap fixed elements.
  Test this with a real mouse: CDP input reaches the page directly and never meets Electron's drag
  areas, so a scripted click passes even when the button is dead.

## Dev loop

```bash
flatpak kill moe.sable.client                                # Sable must not already run
flatpak run moe.sable.client --remote-debugging-port=9333 &
python3 scripts/build.py
python3 -m unittest discover -s tests                        # build checks, run before committing
node scripts/inspect.mjs theme dist/adwaita-dark.sable.css   # live preview, not stored
node scripts/inspect.mjs shot /path/to/shot.png
```

- `inspect.mjs` needs Node 22 or later (built-in `fetch` and `WebSocket`).
- `inspect.mjs` commands: `eval <js>`, `shot <png>`, `theme <file>` (preview with Sable's import
  rewrite), `css <file>` / `uncss` (an extra `<style>` for experiments), `click` / `hover <selector|x,y>`
  (real input events), `key <name>`, and `upload <selector> <file>` (feeds a file input as a file
  chooser would).
- Wait about a second after opening a dialog or menu before taking a screenshot: they animate in.
- Restart Sable without the debug port when done.

## Installing or updating in the app

An import never replaces an installed theme: it adds another tile. So an update is:

1. Copy both `dist/*.sable.css` to `~/Downloads`.
2. Settings → Appearance: remove the two Adwaita tiles, then import both files (scripted: `upload` on
   `input[accept=".sable.css,text/css"]`).
3. Before restarting, wait until each new theme's id appears in
   `sable-sync-base:a1:moe.sable.next.settings`: a restart before the import has synced can drop it
   (the account's older list wins; it happened to Adwaita Dark once).
   **Restart Sable**, then select Adwaita Light and Adwaita Dark in a separate pass. Selecting right
   after removing and importing was saved as `null` twice, and Sable fell back to its default theme.
4. Wait until `lightThemeId` and `darkThemeId` are set in both localStorage keys (a few seconds; the
   save is delayed and synced), then restart.
5. Verify after that **fresh restart**: `#sable-custom-theme` contains a string new to this build.
   An earlier `inspect.mjs theme` preview writes into the same element, so checking without a
   restart can pass falsely.

When scripting it, stop at the first failure (`set -e`), and check that Settings actually opened
(`location.href` ends in `/settings/…`) before clicking anything.

## Theme catalogue

Sable's catalogue is the repo [SableClient/themes](https://git.sable.moe/SableClient/themes) on the
Sable team's Forgejo; themes go in by pull request (submitted as #78).

- **Files.** `themes/<basename>.sable.css` plus `themes/<basename>.preview.sable.css`, same basename.
  Light and dark are separate entries (`adwaita-light`, `adwaita-dark`). `scripts/build.py` writes all
  four into `dist/`.
- **Preview file.** The `@sable-theme` block first, then a `.sable-theme-preview { … }` rule with only
  `--sable-bg-container`, `--sable-bg-on-container`, `--sable-surface-container`,
  `--sable-surface-container-line`, `--sable-surface-on-container`, `--sable-primary-main` and
  `--sable-primary-on-main`; the client ignores anything else. The full file mirrors the same block.
- **Metadata.** Both files carry `fullThemeUrl:
  https://git.sable.moe/SableClient/themes/raw/branch/main/themes/<basename>.sable.css`.
- **`catalog.json`** is regenerated by the repo's CI after a merge: never edit it in a PR. Its
  `scripts/build-catalog.mjs` can be run locally as a dry run (then discard the change).
- **Licence.** That repo is AGPL-3.0; this theme is MIT, which allows including it there.
- **Updating.** After a release here: copy the four `dist/` files into `themes/` on a new branch of
  the fork, push, and open a new PR. The preview card can only be checked once the files are on
  their `main` (the catalogue reads from there).

## After a Sable update

- Re-check the selectors against the new markup, above all: room header (`room-identity`,
  `room-topic`), members drawer, settings rows and outline, titlebar, scrollbar rules.
- Re-run the `--primary-main` text-use grep above.
- Not styled yet: the timeline layout, call UI, emoji board and the login pages.
