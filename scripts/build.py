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

VERSION = "0.2.0"
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


def build(mode, accent):
    t, extra = palette.tokens(mode, accent)
    lines = [HEADER.format(mode=mode, Mode=mode.capitalize(), accent=accent, version=VERSION)]
    lines.append(f"{SCOPE} {{")
    lines.append("  /* Sable colour tokens */")
    lines += [f"  --sable-{k}: {v};" for k, v in t.items()]
    lines.append("  /* Adwaita values for the structure rules */")
    lines += [f"  --{k}: {v};" for k, v in extra.items()]
    lines.append("}\n")
    with open(os.path.join(ROOT, "src", "structure.css")) as f:
        lines.append(f.read())
    css = "\n".join(lines)
    assert not re.search(r"svelte-[a-z0-9]{5,}", css), "selectors must not depend on per-build svelte hashes"
    assert len(css.encode()) < LIMIT
    out = os.path.join(ROOT, "dist", f"adwaita-{mode}.sable.css")
    with open(out, "w") as f:
        f.write(css)
    print(f"{out}  {len(css.encode())} bytes")


if __name__ == "__main__":
    accent = sys.argv[1] if len(sys.argv) > 1 else "yellow"
    for mode in ("light", "dark"):
        build(mode, accent)
