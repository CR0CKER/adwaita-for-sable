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
- **Storage.** Imported themes and the slot choice live in localStorage `sable-custom-themes:a1`
  (per account; `themes[]`, `lightThemeId`, `darkThemeId`). The choice is also synced to the Matrix
  account (`sable-sync-base:a1:moe.sable.next.settings`). The older key without `:a1` is no longer
  written (2026-11-17: it still listed tiles removed hours before): don't check it.
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
  Some semantic classes are reused for unrelated parts: `.rail` is the space rail (inside
  `aside.sidebar` in both layouts), the emoji board's category column (`.board-body > nav.rail`) and
  the login cards' carousel. Scope such rules to their container (`.sidebar .rail`); an unscoped
  `.rail` painted the emoji board's column in the rail's sidebar colour (fixed after 0.4.4).
  Put such a scope in `:where()` (`:where(.sidebar) .rail`) so it adds no specificity: inside a
  shared `:is(.sidebar .rail, .room-nav, .desktop-tools)` the extra class raised all three (`:is()`
  takes its heaviest argument's specificity), and the shared rule then beat `.desktop-tools`' own
  background, turning the strip under the account button grey.
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
- **Separators are borders, never 1px gradient bands.** Chrome snaps borders to whole device pixels
  but not gradient stops. At 166.67% (the Asahi laptop) a 1px band is 1.67 device pixels and smears
  over two, so it looks twice as wide as a border next to it. The bottom tool bar (`.desktop-tools`,
  under rail and room list) once continued the rail's line that way and doubled below the rail
  (fixed in 0.4.4: a `border-right` on a `::before` as wide as the rail). A colour split at a whole
  CSS pixel (66px = 110 device pixels) is fine as a gradient.
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
- **Flat room header and composer, no shadows (decided 2026-11-16).** Tried, installed and compared,
  then reverted at Nils's request ("I prefer flat UI"); don't propose them again:
  - libadwaita's undershoot under the room header (`toolbarview.undershoot-top`: a 1px line and a
    4px gradient in `shade_color` at 75%, `--adw-shade` here), shown only while messages are
    scrolled beneath it. It works in CSS: the scroller is `.timeline-stage .viewport`, which gets
    `scroll-timeline: --adw-timeline block`; `timeline-scope` on `.timeline` hoists the name so a
    `::before` on `.timeline-stage` (and anything else under `.timeline`) can animate opacity on it
    with `animation-range: 0 8px`. Sable's Electron is Chrome 156. A scope declared on an inner
    element captures the name first, so declare it once, on the common ancestor. In busy rooms
    history loading keeps moving `scrollTop` away from 0: read scroll state after it settles.
  - The same shade around the composer bubble (on `.composer::after`, because the bubble's own
    `box-shadow` is its focus ring and an animation would override it), first only while newer
    messages were below, then always.
  For a header refresh that stays flat, GNOME's chat apps agree on: a centred title with the topic as
  a dim subtitle, one to three end buttons, no avatar beside the title, and a timeline clamped to
  about 750px (Fractal). Screenshots: [Fractal](https://gitlab.gnome.org/World/fractal/raw/fractal-14/screenshots/main.png),
  [Polari](https://gitlab.gnome.org/GNOME/polari/raw/HEAD/data/metainfo/polari-main.png),
  [Dino](https://dino.im/img/appdata/screenshot-dino-0.4-main-2244x1644@2.png),
  [Flare](https://gitlab.com/Schmiddiii/flare/-/raw/master/data/screenshots/screenshot.png),
  [Paper Plane](https://github.com/paper-plane-developers/paper-plane/raw/main/data/resources/screenshots/screenshot1.png),
  [Chatty](https://gitlab.gnome.org/World/Chatty/-/raw/main/data/screenshots/desktop-unfolded-view-light.png);
  Fractal's header is `src/session_view/room_history/mod.blp` and `title.blp`. Not pursued yet.
- **The composer's top edge is left as Sable draws it (decided 2026-11-16).** `.composer-dock` has
  `margin-top: -12px`, so the timeline runs 12px under the dock and messages are clipped flat at the
  bubble's top edge; an avatar cut there squares off the bubble's rounded corner. `margin-top: 0`
  fixes it (messages end 12px above the bubble; the newest still clears it), but Nils chose not to
  ship it.
- **Window decoration.** GNOME apps have no title strip: `--titlebar-height` and `--safe-top` go to 0,
  the `.titlebar` becomes a transparent overlay holding only the close button, and the header bars get
  `-webkit-app-region: drag` (their buttons, links and inputs `no-drag`). The button is a 24px circle,
  13px from the edge, with GTK's `window-close-symbolic` as a mask. It is close only, matching GNOME's
  default `appmenu:close` (CSS can't read the GNOME setting). To show all three buttons, drop the
  `button:not(.close) { display: none }` rule, style the other two like `.close`, and set
  `--adw-wc-width` to 91px.
  The image viewer (`body > .viewer`, z-index 1001 under the titlebar's 7000) ends its toolbar in
  its own close button right under the window's. While it is open the theme hides the titlebar
  (`body:has(> .viewer)`), so the viewer's close is the only one in the corner (Nils's choice over
  a Fractal-style back arrow or two closes side by side, 2026-11-16).
- **Drag areas and the close button.** Electron applies `-webkit-app-region` areas in document order,
  and `.titlebar` comes before the header bars, so their `drag` overrides the button's `no-drag` and
  swallows real clicks. Each draggable header bar has an `::after` strip (no-drag, `--adw-wc-width`
  + 6px) at its right end, which comes after it and cuts the button out. It is absolute, not fixed:
  `.drawer-track` (`will-change: transform`) and `.room-view` (a size container) trap fixed elements.
  Which header bar reaches the corner depends on the layout: the room header is a child of
  `.room-view` in the wide layout and of `.timeline` below Sable's 70.25rem breakpoint, and narrow
  side panels open as `.dialog-content-drawer` modals from the right with their own header. Each
  gets the right padding. Check narrow widths with `Emulation.setDeviceMetricsOverride` in the
  same CDP session as the measurement (the override ends with the session).
  Side panels' own close button (inline `.room-view > aside` or in a drawer; the last button of
  the header's `.suffix`, matched by position because Sable is translated; not `section.thread-view`,
  whose last button is "Jump to original message") shows Phosphor's SidebarSimple, mirrored,
  instead of a cross (CSS `d` on Sable's own `<path>`, so size and colour stay Sable's), so it
  isn't mistaken for a second window close button.
  Members is the exception: Sable renders its close button only when the panel is modal (the
  narrow drawer); inline it closes only through the room header's Members toggle. CSS can't add a
  working button, so the theme leaves it.
  Test header changes in both layouts, with each side panel open (Threads, Media, Widgets, Members)
  and with a thread open (`section.thread-view`, whose header ends in "Jump to original message").
  Open panels from the room header with a DOM `.click()` and close them the same way before the next
  one: in the narrow layout they stack as drawers, and Escape over CDP doesn't close them.
  Test this with a real mouse: CDP input reaches the page directly and never meets Electron's drag
  areas, so a scripted click passes even when the button is dead.
  Also open an image (click `.media-image-activation` in the timeline): the window close must
  disappear, the viewer's Close must be what sits in the corner, and the window close must return
  once the viewer closes.

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
- To compare with stock Sable, empty `#sable-custom-theme` *and* remove `body`'s `remote-theme`
  class; `theme <file>` doesn't put the class back, and every rule needs it. Add it back before the
  next measurement: forgetting this made "fixed" measurements show stock Sable (2026-11-17).
- Navigate without clicking through the UI with a same-origin link, which SvelteKit routes on the
  client: create `<a href="sable-app://app/inbox">`, `.click()` it, remove it. Some triggers (account
  popover, bottom bar) ignore `.click()` and real clicks during transitions.
- Width-dependent layouts: `Emulation.setDeviceMetricsOverride` lasts for one CDP session only, so
  set it, act and measure in the same session (a small script on `scripts/lib/cdp.mjs`).
- Leave Sable running with the change applied (installed or previewed) for Nils to test; restart it
  without the debug port only once he's done.

## Installing or updating in the app

An import never replaces an installed theme: it adds another tile. So an update is:

1. Copy both `dist/*.sable.css` to `~/Downloads`.
2. Settings → Appearance: remove the two Adwaita tiles, then import both files (scripted: `upload` on
   `input[accept=".sable.css,text/css"]`).
3. Before restarting, wait until each new theme's id appears in
   `sable-sync-base:a1:moe.sable.next.settings`: a restart before the import has synced can drop it
   (the account's older list wins). That alone isn't enough: on 2026-11-16 Adwaita Dark was in that
   key and still vanished at the restart. Wait about 30 seconds after the last import, and check both
   tiles are there after the restart before selecting.
   **Restart Sable**, then select Adwaita Light and Adwaita Dark in a separate pass. Selecting right
   after removing and importing was saved as `null` twice, and Sable fell back to its default theme.
4. Wait until `lightThemeId` and `darkThemeId` are set in `sable-custom-themes:a1` and in the synced
   key (a few seconds; the save is delayed and synced), then restart. Leave the other slot alone: it
   may hold another theme (Light = macOS Light since 2026-11-17).
5. Verify after that **fresh restart**: `#sable-custom-theme` contains a string new to this build.
   An earlier `inspect.mjs theme` preview writes into the same element, so checking without a
   restart can pass falsely.

When scripting it, stop at the first failure (`set -e`), and check that Settings actually opened
(`location.href` ends in `/settings/…`) before clicking anything. Select a theme with a DOM `.click()` on its
`button.tile-hit` (match its text): clicking by coordinates can land outside the settings dialog,
which closes it.

More pitfalls (2026-11-16):
- A Sable launch can take longer than 30 seconds to open the debug port, or not come back after a
  restart at all: wait up to 60 seconds, and check `flatpak ps` before assuming it's running.
  Starting Sable while it runs only hands over to the running instance (the debug flag is ignored).
- An install run that was interrupted or rejected may have gone further than it seems. One had
  already imported a build and restarted Sable, leaving both slots `null` (Sable on its default
  theme). Before re-running, list `sable-custom-themes` (names, ids, a string from each build) and
  the slot ids, and carry on from where it stopped.
- `click()` returns nothing, so `inspect.mjs eval` around it fails to print (`"undefined" is not
  valid JSON`) even though the click ran: end such expressions with `return 1`.

## Releasing

Sable's theme catalogue (SableClient/themes) doesn't take this theme: Sable has a No-AI policy
(sable-next `CONTRIBUTING.md`, "AI-generated content"), and the submission (#78) was closed. The
theme is distributed from GitHub only.

1. Bump `VERSION` in `scripts/build.py`, rebuild, run the tests, move the changelog's *Unreleased*
   entries under the new version.
2. Commit, tag `v<version>`, push both.
3. `gh release create v<version> dist/adwaita-light.sable.css dist/adwaita-dark.sable.css --title
   v<version> --notes-file <notes>`. Notes: the install line used since 0.4.0 ("Install: download
   both `.sable.css` files below, then …"), a blank line, then the changelog entries with their
   hard wraps joined (GitHub keeps every newline). The README links
   `releases/latest/download/<file>`, so the asset names must stay the same.
4. Check: `gh release list` shows it as Latest, and the file from
   `releases/latest/download/adwaita-dark.sable.css` equals `dist/`.
5. Install the release build in Sable (above), so the installed copy is exactly the release.

## Reporting to Sable

Sable's issues and pull requests live at
[SableClient/Sable-next](https://git.sable.moe/SableClient/Sable-next) on git.sable.moe (the GitHub
`SableClient/Sable` redirects to the archived `Sable-Legacy`). Its public API answers without a
token: `https://git.sable.moe/api/v1/repos/SableClient/Sable-next/issues?state=all&q=…`.

- **Ctrl+Q / Ctrl+W** do nothing in 2.3.9: added for #954, removed with the Tauri shell, reported as
  [#1919](https://git.sable.moe/SableClient/sable-next/issues/1919). Not a theme issue (CSS can't
  touch shortcuts).

## After a Sable update

- Re-check the selectors against the new markup, above all: room header (`room-identity`,
  `room-topic`), members drawer, settings rows and outline, titlebar, scrollbar rules.
- Re-run the `--primary-main` text-use grep above.
- Not styled yet: the timeline layout, call UI, emoji board and the login pages.
