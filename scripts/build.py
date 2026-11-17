#!/usr/bin/env python3
"""Build dist/adwaita-{light,dark}.sable.css from src/palette.py + src/structure.css.

Usage: scripts/build.py [accent]   (GNOME accent name or #rrggbb; default yellow)
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
import palette  # noqa: E402

VERSION = "0.4.8"
SCOPE = "body.sable-remote-theme"
LIMIT = 1024 * 1024

HEADER = """/*
@sable-theme
id: adwaita-{mode}
name: Adwaita {Mode}
author: CR0CKER
description: GNOME's Adwaita, laid out like GNOME Files ({accent} accent). v{version}
kind: {mode}
contrast: low
tags: {mode}, gnome, adwaita
*/
"""


def parse_accent(arg):
    """Return a GNOME accent name or a #rrggbb colour; anything else is an error.

    The value lands in the theme header comment and in colour maths, so it is
    checked here rather than trusted.
    """
    if arg in palette.GNOME_ACCENTS or re.fullmatch(r"#[0-9a-fA-F]{6}", arg):
        return arg
    names = ", ".join(palette.GNOME_ACCENTS)
    raise SystemExit(f"accent must be one of {names} or #rrggbb, not {arg!r}")


def header(mode, accent):
    return HEADER.format(mode=mode, Mode=mode.capitalize(), accent=accent, version=VERSION)


def render(mode, accent):
    """Return the theme CSS for one mode."""
    t, extra = palette.tokens(mode, accent)
    lines = [header(mode, accent)]
    lines.append(f"{SCOPE} {{")
    lines.append("  /* Sable colour tokens */")
    lines += [f"  --sable-{k}: {v};" for k, v in t.items()]
    lines.append("  /* Adwaita values for the structure rules */")
    lines += [f"  --{k}: {v};" for k, v in extra.items()]
    lines.append("}\n")
    with open(os.path.join(ROOT, "src", "structure.css")) as f:
        lines.append(f.read())
    css = "\n".join(lines)
    if re.search(r"svelte-[a-z0-9]{5,}", css):
        raise SystemExit("selectors must not depend on per-build svelte hashes")
    if len(css.encode()) >= LIMIT:
        raise SystemExit("theme is over Sable's 1 MiB limit")
    return css


def build(mode, accent):
    """Write dist/adwaita-<mode>.sable.css."""
    css = render(mode, accent)
    out = os.path.join(ROOT, "dist", f"adwaita-{mode}.sable.css")
    with open(out, "w") as f:
        f.write(css)
    print(f"{out}  {len(css.encode())} bytes")


if __name__ == "__main__":
    accent = parse_accent(sys.argv[1] if len(sys.argv) > 1 else "yellow")
    for mode in ("light", "dark"):
        build(mode, accent)
