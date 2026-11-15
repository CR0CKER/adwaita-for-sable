# Adwaita for Sable

Makes [Sable](https://sable.moe), the Matrix client, look like a native GNOME app: Adwaita
colours, GNOME Files' sidebar, libadwaita buttons, entries, menus and preferences, light and dark.
A sibling of [Adwaita for Logseq](https://github.com/CR0CKER/adwaita-for-logseq) and
[Adwaita for Tine](https://github.com/CR0CKER/adwaita-for-tine).

Built for **Sable 2.3.9** (Flathub `moe.sable.client`) on GNOME 49 / libadwaita 1.8. The layout
rules target Sable's class names, which can change between releases.

## Install

1. Sable → Settings → Appearance → Themes → **Import file**: import `dist/adwaita-light.sable.css`
   and `dist/adwaita-dark.sable.css`. (The Flatpak can read `~/Downloads`; the file chooser
   portal reaches anything else.)
2. Pick **Adwaita Light** in the *Light mode* row and **Adwaita Dark** in the *Dark mode* row.
3. Set *Light or dark* to **System**, so Sable follows GNOME's style switch.

To undo: pick *Sable (default)* in both rows, and remove the two themes.

**Updating**: an import adds a new tile; it never replaces the old one. Remove the two Adwaita tiles,
import the new files, restart Sable, then select them again. Selecting right after importing
sometimes isn't saved. Details: [docs/development.md](docs/development.md#installing-or-updating-in-the-app).

**Fonts**: Adwaita Sans and Adwaita Mono come with GNOME 48 and later. Elsewhere, Sable falls back to
the system sans-serif and monospace fonts.

## Sharing

The two files in `dist/` are the whole theme. Send them any way you like. Sending them in a Matrix
chat works well: Sable shows an install card for `.sable.css` files (Settings → *Show install cards
for theme files*), so the recipient can install them straight from the chat. They're CSS, so Sable
asks people to install themes only from people they trust.

The accent is built in (yellow). For another GNOME accent, build a copy first:
`python3 scripts/build.py blue`.

## What changes

**Colours**: libadwaita 1.8's values, extracted from `libadwaita-1.so`. The sidebar is
`sidebar_bg_color`, the room view `view_bg_color`, settings `window_bg_color`, menus
`popover_bg_color`. Hover, active and selected states are GTK's `alpha(currentColor, …)` tints.
The accent follows libadwaita: fills use the system accent as is (yellow, `#c88800`), and accent
text (links, accent labels) uses the oklab-clamped standalone tone (`#905300` light, `#ffc057` dark).

**Type**: Adwaita Sans at 11pt and Adwaita Mono, bold titles, no semibold. Sable's text-size
setting still scales it, and a font chosen in Sable's settings still wins.

**Sidebar** (laid out like Files):
- The room list is Files' sidebar. The space rail is the outer pane of a nested split view, as
  libadwaita draws it: `secondary_sidebar_bg_color` with a shade line between the panes (and at the
  content edge).
- The list's name is the header bar title: bold 11pt, centred, 47px.
- Rows as in `.navigation-sidebar`: 36px, 9px radius, 6px side margins, regular 11pt, a neutral
  selection fill instead of an accent bar; dim, regular section headings.
- Rail tiles and the bottom tools are flat 9px buttons without outlines.

**Room view**: a flat header bar in the view's colour with no bottom line, and an AdwWindowTitle
(bold title, dim caption topic). The composer is an Adwaita entry with the 2px accent focus ring.
Avatars are round, like AdwAvatar. The side panels (members, threads, search, media, widgets)
share the view colour, set off by a hairline. Hovering a message lifts it slightly, with
libadwaita's card hover (3%) on a rounded box inset from the timeline's edges.

**Icons**: 20px in the sidebar, header bars and composer (18px in menus). Sable's icons are thin
outlines; at 20px they match the optical size of GNOME's filled 16px symbolic icons. The glyphs stay Sable's own (Phosphor); swapping in Adwaita's symbolic icons
was tried and set aside (see [docs/development.md](docs/development.md#design-decisions)).

**Controls**: 34px buttons with 9px corners and bold labels, accent-filled suggested actions;
borderless tinted entries and selects; GTK switches; AdwToggleGroup for segmented choices;
GTK tooltips. Scrollbars are GTK overlay sliders: 3px, rounded, 8px under the pointer, no arrow
buttons. They fade in while the pointer is over a scrollable area and fade out after it leaves.

**Window decoration** (when Sable draws its own, Settings → Desktop app): no title strip. The
header bars move the window, and the only button is GNOME's round 24px close button with GTK's
`window-close-symbolic`, 13px from the corner (GNOME's default `appmenu:close` layout, as in Adwaita
for Tine). Electron can't round a frameless window's corners; the GNOME Shell extension
[Rounded Window Corners Reborn](https://extensions.gnome.org/extension/7048/rounded-window-corners-reborn/)
can (15px matches libadwaita).

**Popovers and settings**: 15px menus with 32px rows and destructive items in the error text
colour. Settings reads as an AdwPreferencesDialog: a sidebar list, bold group titles, and setting
rows in 12px boxed-list cards with separators.

Unchanged by design: people's own name colours (set in their Matrix profiles) and Sable's
timeline layout.

## Limitations

- The layout rules target Sable 2.3.9's class names. A Sable update can change them; the colours
  survive that, and parts of the layout may not.
- The accent is fixed at build time: CSS can't read GNOME's accent setting. The same goes for the
  window-button layout (close only).
- Scrollbars appear on hover, not on wheel scrolling alone (CSS can't detect scrolling).
- Electron can't round the corners of a frameless window (see *Window decoration*).
- Not styled yet: the timeline layout, call UI, emoji board and the login pages.

## Changing the accent

`scripts/build.py <accent>` takes a GNOME accent name (`blue`, `teal`, `green`, `yellow`,
`orange`, `red`, `pink`, `purple`, `slate`) or `#rrggbb`, and rebuilds both files.

## Building

```bash
python3 scripts/build.py            # writes dist/adwaita-{light,dark}.sable.css
```

- `src/palette.py`: Adwaita values mapped onto Sable's colour tokens.
- `src/structure.css`: the layout rules, shared by both files.
- `scripts/accent.py`: oklab helpers (from Adwaita for Tine).
- `scripts/inspect.mjs`: drives a Sable started with
  `flatpak run moe.sable.client --remote-debugging-port=9333`. `theme <file>` previews a build
  without importing it, `shot <png>` takes a screenshot, `eval`, `click`, `hover` and `key` help
  inspect markup, and `upload` feeds a file to Sable's import button.

The build refuses selectors that use Sable's per-build `svelte-*` hashes. How Sable's theming works,
the design decisions, the dev loop and the install routine are in
[docs/development.md](docs/development.md); changes are in [CHANGELOG.md](CHANGELOG.md).

## License

MIT
