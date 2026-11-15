"""Adwaita colours (libadwaita 1.8, GNOME 49) mapped onto Sable's theme tokens.

Values come from /usr/lib64/libadwaita-1.so.0's styles/default.css
(`gresource extract ... /org/gnome/Adwaita/styles/default.css`).

Sable's surfaces, as its own stylesheets use them:
  bg          space rail + room list               -> Adwaita sidebar
  surface     room view, timeline, panels          -> Adwaita view
  surface-var composer, inputs, inset fields       -> Adwaita entry/card fill on the view
  sec         neutral buttons, selected list rows  -> GTK's currentColor tints
  primary     accent fills, links, focus           -> the GNOME accent (libadwaita rules)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from accent import GNOME_ACCENTS, MODES, clamp  # noqa: E402


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def over(base, rgb, alpha):
    """Composite rgb at alpha over an opaque base hex -> opaque hex."""
    b = hex_rgb(base)
    return "#" + "".join(f"{round(b[i] * (1 - alpha) + rgb[i] * alpha):02x}" for i in range(3))


def rgba(rgb, alpha):
    return f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha:g})"


ADW = {
    "dark": {
        "window": "#222226", "view": "#1d1d20", "sidebar": "#2e2e32",
        "secondary_sidebar": "#28282c", "popover": "#36363a", "dialog": "#36363a",
        "fg_rgb": (255, 255, 255), "fg_alpha": 1.0,
        "shade": "rgba(0, 0, 6, 0.25)", "border_alpha": 0.15,
        "success": "#26a269", "warning": "#cd9309", "error": "#c01c28",
        "warning_fg": "rgba(0, 0, 0, 0.8)",
    },
    "light": {
        "window": "#fafafb", "view": "#ffffff", "sidebar": "#ebebed",
        "secondary_sidebar": "#f3f3f5", "popover": "#ffffff", "dialog": "#fafafb",
        "fg_rgb": (0, 0, 6), "fg_alpha": 0.8,
        "shade": "rgba(0, 0, 6, 0.07)", "border_alpha": 0.15,
        "success": "#2ec27e", "warning": "#e5a50a", "error": "#e01b24",
        "warning_fg": "rgba(0, 0, 0, 0.8)",
    },
}

# libadwaita's standalone-colour clamp (text-on-background versions of fills).
STANDALONE = {"dark": lambda L: max(L, 0.85), "light": lambda L: min(L, 0.5)}


def tokens(mode, accent="yellow"):
    a = ADW[mode]
    fg_rgb, fa = a["fg_rgb"], a["fg_alpha"]
    fg = rgba(fg_rgb, fa) if fa < 1 else "#ffffff"

    def tint(alpha):  # GTK's alpha(currentColor, x)
        return rgba(fg_rgb, round(alpha * fa, 3))

    def solid(base, alpha):
        return over(base, fg_rgb, alpha * fa)

    accent_hex = GNOME_ACCENTS.get(accent, accent)
    # libadwaita: fills use the system accent as-is in both modes; standalone
    # (text) accent is the fill with its oklab lightness clamped.
    acc_fill = accent_hex
    acc_text = clamp(accent_hex, STANDALONE[mode])
    acc_hover = clamp(acc_text, MODES[mode][2])
    acc_rgb = hex_rgb(acc_fill)

    t = {}

    def group(name, container, hover, active, line, on):
        t[f"{name}-container"] = container
        t[f"{name}-container-hover"] = hover
        t[f"{name}-container-active"] = active
        t[f"{name}-container-line"] = line
        t[f"{name}-on-container"] = on

    border = tint(a["border_alpha"])
    # Hover/active are GTK-style translucent tints (alpha(currentColor, x)), so
    # they read the same on the sidebar, the view and popovers.
    # Sidebar (rail + room list).
    group("bg", a["sidebar"], tint(.07), tint(.12), border, fg)
    # View (room column).
    group("surface", a["view"], tint(.07), tint(.12), border, fg)
    # Entries/cards on the view: GTK entry = alpha(currentColor, .1), made opaque
    # because Sable also uses it as a panel fill.
    entry = solid(a["view"], .1 if mode == "dark" else .08)
    group("surface-var", entry, solid(a["view"], .14), solid(a["view"], .18), border, fg)
    t["surface-var-on-container"] = fg

    # Neutral (GTK button greys).
    t.update({
        "sec-main": fg, "sec-main-hover": fg, "sec-main-active": fg, "sec-main-line": border,
        "sec-on-main": a["view"],
        "sec-container": tint(.1), "sec-container-hover": tint(.15),
        "sec-container-active": tint(.2), "sec-container-line": border, "sec-on-container": fg,
    })

    # Accent.
    t.update({
        "primary-main": acc_fill,
        "primary-main-hover": f"color-mix(in srgb, {acc_fill} 90%, {'#ffffff' if mode == 'dark' else '#000006'})",
        "primary-main-active": f"color-mix(in srgb, {acc_fill} 80%, {'#000006'})",
        "primary-main-line": acc_fill,
        "primary-on-main": "#ffffff",
        "primary-container": over(a["view"], acc_rgb, .25),
        "primary-container-hover": over(a["view"], acc_rgb, .32),
        "primary-container-active": over(a["view"], acc_rgb, .4),
        "primary-container-line": over(a["view"], acc_rgb, .5),
        "primary-on-container": fg,
    })

    # Status colours: fill + standalone text, as libadwaita derives them.
    for name, key, on_main in (("success", "success", "#ffffff"),
                               ("warn", "warning", a["warning_fg"]),
                               ("crit", "error", "#ffffff")):
        fill = a[key]
        text = clamp(fill, STANDALONE[mode])
        frgb = hex_rgb(fill)
        t.update({
            f"{name}-main": fill,
            f"{name}-main-hover": f"color-mix(in srgb, {fill} 90%, {'#ffffff' if mode == 'dark' else '#000006'})",
            f"{name}-main-active": f"color-mix(in srgb, {fill} 80%, #000006)",
            f"{name}-main-line": fill,
            f"{name}-on-main": on_main,
            f"{name}-container": over(a["view"], frgb, .2),
            f"{name}-container-hover": over(a["view"], frgb, .26),
            f"{name}-container-active": over(a["view"], frgb, .32),
            f"{name}-container-line": over(a["view"], frgb, .45),
            f"{name}-on-container": text,
        })

    t["focus-ring"] = rgba(acc_rgb, .5)
    t["shadow"] = a["shade"]
    t["overlay"] = "rgba(0, 0, 6, 0.5)" if mode == "dark" else "rgba(0, 0, 6, 0.25)"

    # Extra --adw-* values the structure CSS uses.
    extra = {
        "adw-window-bg": a["window"], "adw-view-bg": a["view"], "adw-sidebar-bg": a["sidebar"],
        "adw-secondary-sidebar-bg": a["secondary_sidebar"], "adw-popover-bg": a["popover"],
        "adw-dialog-bg": a["dialog"], "adw-fg": fg, "adw-border": border,
        "adw-dim-fg": tint(.55), "adw-row-hover": tint(.07), "adw-row-active": tint(.16),
        "adw-row-selected": tint(.1), "adw-row-selected-hover": tint(.13),
        "adw-button": tint(.1), "adw-button-hover": tint(.15), "adw-button-active": tint(.3),
        "adw-flat-hover": tint(.07), "adw-flat-active": tint(.16),
        "adw-accent": acc_fill, "adw-accent-text": acc_text, "adw-accent-text-hover": acc_hover,
        "adw-selection": rgba(acc_rgb, .25),
        "adw-shade": a["shade"],
        "adw-sidebar-border": "rgba(0, 0, 6, 0.36)" if mode == "dark" else "rgba(0, 0, 6, 0.07)",
        "adw-popover-shadow": ("0 1px 5px 1px rgba(0, 0, 6, 0.09), 0 2px 14px 3px rgba(0, 0, 6, 0.05)"
                               if mode == "light" else
                               "0 1px 5px 1px rgba(0, 0, 6, 0.36), 0 2px 14px 3px rgba(0, 0, 6, 0.2)"),
        "adw-card-bg": "rgba(255, 255, 255, 0.08)" if mode == "dark" else "#ffffff",
        "adw-card-shade": "rgba(0, 0, 6, 0.36)" if mode == "dark" else "rgba(0, 0, 6, 0.07)",
        "adw-card-shadow": "0 0 0 1px rgba(0, 0, 6, 0.03), 0 1px 3px 1px rgba(0, 0, 6, 0.07), 0 2px 6px 2px rgba(0, 0, 6, 0.03)",
        "adw-toggle-active-bg": "rgba(255, 255, 255, 0.2)" if mode == "dark" else "#ffffff",
        "adw-toggle-active-fg": fg,
        "adw-popover-outline": "rgba(0, 0, 6, 0.07)" if mode == "light" else "rgba(255, 255, 255, 0.07)",
    }
    return t, extra
