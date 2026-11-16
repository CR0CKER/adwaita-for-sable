# Changelog

## 0.4.0 (2026-11-16)

- Distributed from GitHub releases. The theme isn't in Sable's theme catalogue (Sable doesn't accept
  AI-assisted contributions); the preview files and the catalogue's `fullThemeUrl` are gone.
- Fixed: with Sable's title bar on, the close button didn't respond to clicks since 0.2.0. The header
  bars' window-drag area covered it; a no-drag strip at the end of each header bar cuts it out.
- README: recommends turning on Settings → Desktop app → *Use Sable's title bar*.
- Rail tiles and bottom tools no longer move on hover (Sable nudges them 2px right and 3px up);
  GNOME buttons only change their tint.
- Media panel: the sticky month headings take the panel's colour instead of Sable's grey band.
- Docs: where to report Sable issues (Sable-next), and Ctrl+Q not quitting Sable 2.3.9 (#1919).

## 0.3.0 (2026-11-15)

- Threads, search, media and widgets panels: the room view's colour with a hairline, like the
  members panel.
- Timeline: hovering a message lifts it with libadwaita's 3% card hover, on a 12px rounded box
  inset from the timeline's edges, instead of a 7% edge-to-edge band.
- Fixed: the scrollbar fade replaced Sable's own transitions on elements with simpler selectors
  (switch knob, row and button hover fades, progress bars). It no longer overrides them.
- `scripts/build.py` rejects an accent that isn't a GNOME accent name or `#rrggbb`.
- Tests: `python3 -m unittest discover -s tests` checks the accent argument, that every `--adw-*`
  variable is declared and used, that `dist/` matches the sources, and the transition fix.
- Removed unused tokens and the Logseq printer in `scripts/accent.py`.

## 0.2.0 (2026-11-15)

- Window decoration: when Sable draws its own decoration, its title strip folds into the header bars.
  The only button is GNOME's round 24px close button, and the header bars move the window.
- Icons at 20px (sidebar, header bar, composer; 18px in menus), the optical size of GNOME's 16px
  symbolic icons for Sable's outline icons.
- Scrollbars: GTK overlay-style sliders without arrow buttons. They fade in while the pointer is over
  a scrollable area and fade out after it leaves.
- Members panel: the room view's colour, set off by a hairline.
- Space rail: libadwaita's secondary sidebar colour, with shade lines between the panes.
- Settings outline links are dim rows, not accent-coloured links.

## 0.1.0 (2026-11-15)

- First version for Sable 2.3.9: light and dark themes built from libadwaita 1.8, with a Files-style
  sidebar, flat header bars, libadwaita controls and menus, preferences-style settings, and Adwaita
  Sans/Mono.
