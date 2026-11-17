# Changelog

## 0.4.6 (2026-11-17)

- The profile popover (click an avatar in the timeline) no longer shows square corners around its
  rounded card: popover and card share libadwaita's 15px popover radius, with one outline (#1).
- A profile card's avatar shows a round keyboard focus ring instead of a rounded square.

## 0.4.5 (2026-11-16)

- The emoji picker's category column no longer takes the space rail's sidebar colour (Sable gives
  both, and the login cards' carousel, the class `rail`); the space rail's styling is now scoped to
  the sidebar.

## 0.4.4 (2026-11-16)

- The separator between the space rail and the room list no longer doubles in width next to the
  account button at fractional display scales.
- The image viewer's close button no longer sits under the window's close button: while the viewer
  is open, the window close is hidden.

## 0.4.3 (2026-11-16)

- Side panels in the wide layout (threads, media, widgets) also close with the sidebar icon; 0.4.2
  only changed the drawers of the narrow layout.

## 0.4.2 (2026-11-16)

- Side panels opened as drawers (narrow window) close with a sidebar icon (Phosphor's
  SidebarSimple, from Sable's own icon set) instead of a cross, so their button no longer looks
  like a second window close button.
- README: credits the icons the theme embeds (Adwaita's window close, Phosphor's SidebarSimple).

## 0.4.1 (2026-11-16)

- Fixed: in a narrow window (below Sable's 70.25rem / 1124px breakpoint) the room header's
  buttons ran under the close button, and side panels opened as drawers put their own close button
  under it too. Both header bars now leave room for it.

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
