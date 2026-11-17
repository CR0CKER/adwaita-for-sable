"""Checks on the generated themes: run with `python3 -m unittest`."""
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import build  # noqa: E402

STRUCTURE = open(os.path.join(ROOT, "src", "structure.css")).read()


class AccentArgument(unittest.TestCase):
    def test_accepts_gnome_accent_names_and_hex_colours(self):
        self.assertEqual(build.parse_accent("blue"), "blue")
        self.assertEqual(build.parse_accent("#1A2b3c"), "#1A2b3c")

    def test_rejects_anything_that_could_break_out_of_the_header_comment(self):
        for bad in ("*/ body{}", "#12345", "#1234567", "bleu", ""):
            with self.assertRaises(SystemExit, msg=bad):
                build.parse_accent(bad)


class GeneratedTheme(unittest.TestCase):
    def setUp(self):
        self.css = {mode: build.render(mode, "yellow") for mode in ("light", "dark")}

    def test_header_names_each_mode(self):
        for mode, css in self.css.items():
            self.assertIn(f"id: adwaita-{mode}", css)
            self.assertIn(f"kind: {mode}", css)

    def test_every_adw_variable_used_is_declared(self):
        for css in self.css.values():
            declared = set(re.findall(r"(--adw-[\w-]+)\s*:", css))
            declared |= set(re.findall(r"@property (--adw-[\w-]+)", css))
            used = set(re.findall(r"var\((--adw-[\w-]+)", css))
            self.assertEqual(used - declared, set())

    def test_no_adw_token_is_declared_without_a_use(self):
        for css in self.css.values():
            declared = set(re.findall(r"(--adw-[\w-]+)\s*:", css))
            used = set(re.findall(r"var\((--adw-[\w-]+)", css)) | {"--adw-sb"}
            self.assertEqual(declared - used, set())

    def test_universal_rules_carry_no_specificity(self):
        # A weighted `*` rule setting the transition shorthand replaced
        # Sable's own transitions (switch knob, row hovers, progress bars).
        for line in STRUCTURE.splitlines():
            if re.match(r"\s*body\.sable-remote-theme \*(:hover)?\s*\{", line):
                self.fail(f"universal rule outside :where(): {line.strip()}")

    def test_menu_icon_size_reaches_only_direct_icons(self):
        # A descendant `.menu-item svg` also sized the presence dot's inner
        # <svg> (10px box) to 18px, so it spilled out of its ring (#4).
        # Sable itself sizes `.menu-item>svg`.
        self.assertNotRegex(STRUCTURE, r"\.menu-item\s+svg")

    def test_header_bar_icons_share_one_size(self):
        # Sable draws Members, More options and Back at 24px
        # (`.members-button svg` etc.) beside 20px neighbours.
        self.assertRegex(
            STRUCTURE,
            r"body\.sable-remote-theme \.panel-header-button svg \{[^}]*"
            r"width: var\(--adw-icon-size\); height: var\(--adw-icon-size\);",
        )

    def test_committed_dist_matches_the_sources(self):
        for mode, css in self.css.items():
            name = f"adwaita-{mode}.sable.css"
            with open(os.path.join(ROOT, "dist", name)) as f:
                self.assertEqual(f.read(), css, f"dist/{name} is stale: run scripts/build.py")


if __name__ == "__main__":
    unittest.main()
