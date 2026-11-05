"""Checks index.html against the PRD. Run: python3 tests/check_site.py [URL]

With no URL it checks the local file; with a URL it checks the live site.
Uses only Python's standard library, so there is nothing to install.
"""

import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

GITHUB = "https://github.com/kennethwu08"
LINKEDIN = "https://www.linkedin.com/in/kenneth-wu-6857a0396/"
EMAIL = "mailto:wu1410@mcmaster.ca"
SECTIONS = ["projects", "about", "how-i-built-this", "contact"]
MIN_CONTRAST = 4.5  # WCAG AA minimum for normal-size text


class PageScanner(HTMLParser):
    """Walks the HTML once and records the pieces the checks need."""

    def __init__(self):
        super().__init__()
        self.html_lang = None
        self.title = ""
        self.h1_texts = []
        self.links = []
        self.has_viewport = False
        self.stylesheets = []
        self.sections_with_h2 = []
        self._section = None  # id of the <section> we are currently inside
        self._in = None  # the tag whose text we are currently collecting

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.html_lang = a.get("lang")
        elif tag == "meta" and a.get("name") == "viewport":
            self.has_viewport = True
        elif tag == "a" and "href" in a:
            self.links.append(a["href"])
        elif tag == "link" and a.get("rel") == "stylesheet":
            self.stylesheets.append(a.get("href"))
        elif tag == "section":
            self._section = a.get("id")
        elif tag == "h2" and self._section:
            self.sections_with_h2.append(self._section)
        if tag in ("title", "h1"):
            self._in = tag
            if tag == "h1":
                self.h1_texts.append("")

    def handle_endtag(self, tag):
        if tag == self._in:
            self._in = None
        if tag == "section":
            self._section = None

    def handle_data(self, data):
        if self._in == "title":
            self.title += data
        elif self._in == "h1":
            self.h1_texts[-1] += data


def load(source):
    if source.startswith("http"):
        # curl, not urllib: python.org's macOS Python ships without HTTPS certificates.
        # -f makes curl fail on 404/500, so a missing page fails the test.
        result = subprocess.run(["curl", "-fsSL", "--max-time", "15", source],
                                capture_output=True, text=True)
        if result.returncode != 0:
            sys.exit(f"FAIL  could not load {source}: {result.stderr.strip()}")
        return result.stdout
    return Path(source).read_text()


def load_css(source):
    """Finds styles.css next to the page. A missing local file fails the checks, not the script."""
    if source.startswith("http"):
        return load(source.rstrip("/") + "/styles.css")
    path = Path(source).with_name("styles.css")
    return path.read_text() if path.exists() else ""


def contrast(hex_a, hex_b):
    """WCAG contrast ratio between two #rrggbb colours: 1 (identical) to 21 (black on white)."""

    def luminance(colour):
        channels = [int(colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        r, g, b = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    lighter, darker = sorted((luminance(hex_a), luminance(hex_b)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def css_colour(css, name):
    match = re.search(rf"--{name}:\s*(#[0-9a-fA-F]{{6}})", css)
    return match.group(1) if match else None


def readable_on_background(css, name):
    background, colour = css_colour(css, "bg"), css_colour(css, name)
    return bool(background and colour) and contrast(colour, background) >= MIN_CONTRAST


def run_checks(html, css):
    page = PageScanner()
    page.feed(html)
    text = " ".join(html.split())
    return [
        ("<html> has lang='en'", page.html_lang == "en"),
        ("mobile viewport meta tag", page.has_viewport),
        ("<title> mentions Kenneth Wu", "Kenneth Wu" in page.title),
        ("exactly one <h1>", len(page.h1_texts) == 1),
        ("<h1> is 'Kenneth Wu'", [t.strip() for t in page.h1_texts] == ["Kenneth Wu"]),
        ("pitch mentions McMaster", "McMaster" in text),
        ("GitHub link", GITHUB in page.links),
        ("LinkedIn link", LINKEDIN in page.links),
        ("Email link", EMAIL in page.links),
        ("links styles.css", "styles.css" in page.stylesheets),
        *[(f"section #{name} has an <h2>", name in page.sections_with_h2) for name in SECTIONS],
        ("CSS declares a dark colour scheme", "color-scheme: dark" in css),
        *[(f"--{name} is readable on --bg (contrast >= {MIN_CONTRAST})", readable_on_background(css, name))
          for name in ("text", "muted", "accent")],
        ("CSS has a visible keyboard focus style", ":focus-visible" in css),
    ]


def main():
    source = sys.argv[1] if len(sys.argv) > 1 else "index.html"
    results = run_checks(load(source), load_css(source))
    for name, ok in results:
        print(f"{'PASS' if ok else 'FAIL'}  {name}")
    failed = sum(not ok for _, ok in results)
    print(f"\n{len(results) - failed}/{len(results)} checks passed for {source}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
