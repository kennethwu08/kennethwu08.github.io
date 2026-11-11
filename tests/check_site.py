"""Checks index.html against the PRD. Run: python3 -I tests/check_site.py [URL]

With no URL it checks the local file; with a URL it checks the live site.
Uses only Python's standard library, so there is nothing to install.

This script reads the HTML and CSS as text. It cannot see the rendered page, so layout
(sideways scrolling, overlapping images, real sizes) is checked in a browser with
tests/layout_check.js. See the instructions at the top of that file.
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
EXPECTED_IMAGES = 5
MAX_IMAGE_BYTES = 250_000
MAX_TOTAL_IMAGE_BYTES = 1_000_000
MIN_TAP_PADDING_REM = 0.5  # card links get this much padding above and below at least
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source",
             "track", "wbr"}  # tags that never have a closing tag
HERE = Path(__file__).resolve().parent.parent  # the project folder, wherever you run from

# (name, GitHub link, facts the card must state), in the order they must appear.
PROJECTS = [
    ("Larpslator", "https://github.com/kennethwu08/larpslator",
     ["LarpHacks", "team of 4", "ESP32", "100%", "93%"]),
    ("Walk In My World", "https://github.com/bernardkim0805-cmyk/Disability-Awareness-Simulator-3D-",
     ["team of 3", "7 experience modes", "Accessibility Lab", "20+", "WHO"]),
    ("Physics Visualizer", "https://github.com/kennethwu08/Physics-Visualizer",
     ["8 Grade", "Gemini", "PyInstaller"]),
]


class PageScanner(HTMLParser):
    """Walks the HTML once and records the pieces the checks need."""

    def __init__(self):
        super().__init__()
        self.html_lang = None
        self.title = ""
        self.h1_texts = []
        self.h1_hidden = False
        self.pitch = ""
        self.meta_lines = []
        self.links = []
        self.has_viewport = False
        self.stylesheets = []
        self.sections_with_h2 = []
        self.images = []
        self.cards = []  # one dict per <article>: name, links, text, images, tags
        self._section = None  # id of the <section> we are currently inside
        self._card = None  # the <article> we are currently inside
        self._in = None  # the tag whose text we are currently collecting
        self._open = []  # (tag, hides_contents) for every element we are inside

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        hides = "hidden" in a or a.get("aria-hidden") == "true"
        if tag not in VOID_TAGS:
            self._open.append((tag, hides))
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
        elif tag == "img":
            self.images.append(a)
        elif tag == "article":
            self._card = {"name": "", "links": [], "text": "", "images": 0, "tags": 0}
            self.cards.append(self._card)
        if self._card is not None:
            if tag == "a" and "href" in a:
                self._card["links"].append(a["href"])
            elif tag == "img":
                self._card["images"] += 1
            elif tag == "li":
                self._card["tags"] += 1
        if tag in ("title", "h1", "h3"):
            self._in = tag
            if tag == "h1":
                self.h1_texts.append("")
                # "hidden" or aria-hidden, on the h1 or anything around it, hides the name
                # from screen readers too.
                self.h1_hidden = any(h for _, h in self._open)
        elif tag == "p" and a.get("class") in ("pitch", "project-meta"):
            self._in = a["class"]
            if self._in == "project-meta":
                self.meta_lines.append("")

    def handle_endtag(self, tag):
        while self._open:  # close this tag, and any unclosed tags inside it
            if self._open.pop()[0] == tag:
                break
        if tag == self._in or (tag == "p" and self._in in ("pitch", "project-meta")):
            self._in = None
        if tag == "section":
            self._section = None
        if tag == "article":
            self._card = None

    def handle_data(self, data):
        if self._card is not None:
            self._card["text"] += data
            if self._in == "h3":
                self._card["name"] += data
        if self._in == "title":
            self.title += data
        elif self._in == "h1":
            self.h1_texts[-1] += data
        elif self._in == "pitch":
            self.pitch += data
        elif self._in == "project-meta":
            self.meta_lines[-1] += data


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
    path = Path(source).parent / "styles.css"
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


def readable_on(css, name, background_name):
    background, colour = css_colour(css, background_name), css_colour(css, name)
    return bool(background and colour) and contrast(colour, background) >= MIN_CONTRAST


def strip_comments(css):
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def media_block(css, query):
    """The text inside `@media <query> { ... }`, found by counting braces."""
    start = css.find(f"@media {query}")
    if start < 0:
        return ""
    depth, open_at = 0, css.index("{", start)
    for i in range(open_at, len(css)):
        depth += {"{": 1, "}": -1}.get(css[i], 0)
        if depth == 0:
            return css[open_at + 1:i]
    return ""


def outside_media(css):
    """The CSS with every @media block removed: the rules that apply at every width."""
    while (block := re.search(r"@media[^{]*\{", css)):
        inner = media_block(css, css[block.start() + 7:block.end() - 1].strip())
        css = css[:block.start()] + css[block.end() + len(inner) + 1:]
    return css


def css_rule(css, selector):
    """The declarations inside every rule whose selector list includes `selector`."""
    bodies = []
    css = strip_comments(css)  # a comment above a rule would hide its selector
    for selectors, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        if selector in [s.strip() for s in selectors.split(",")]:
            bodies.append(body)
    return " ".join(bodies)


def literal_colours_outside_root(css):
    """Colours written directly in rules instead of through a --variable in :root."""
    rules = strip_comments(re.sub(r":root\s*\{[^}]*\}", "", css))
    literals = re.findall(r"#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(", rules)
    # Named colours like "white": any colour or background value must go through var().
    for value in re.findall(r"(?<![-\w])(?:color|background(?:-color)?|[a-z-]+-color)\s*:\s*([^;}]+)", rules):
        if "var(" not in value and value.strip() not in ("none", "inherit", "transparent", "currentColor"):
            literals.append(value.strip())
    return literals


def link_resolves(url):
    result = subprocess.run(["curl", "-fsSIL", "--max-time", "15", "-o", "/dev/null", url],
                            capture_output=True, text=True)
    return result.returncode == 0


def focus_outline_removed(css):
    """True if any rule for a focused element sets its outline to none or 0."""
    for selectors, body in re.findall(r"([^{}]+)\{([^{}]*)\}", strip_comments(css)):
        if ":focus" in selectors and re.search(r"outline(?:-style|-width)?\s*:\s*(none|0)\b", body):
            return True
    return False


def css_checks(css):
    focus = css_rule(css, ":focus-visible")
    everywhere = outside_media(strip_comments(css))
    h1 = css_rule(css, "h1")
    card_link = css_rule(css, ".project-body > a")
    padding = re.search(r"padding-block:\s*([\d.]+)rem", card_link)
    return [
        ("CSS declares a dark colour scheme", "color-scheme: dark" in css),
        *[(f"--{name} is readable on --{bg} (contrast >= {MIN_CONTRAST})", readable_on(css, name, bg))
          for bg in ("bg", "surface") for name in ("text", "muted", "accent")],
        ("page uses the theme colours (body background and text)",
         "var(--bg)" in css_rule(css, "body") and "var(--text)" in css_rule(css, "body")),
        ("every colour comes from a :root variable", not literal_colours_outside_root(css)),
        ("keyboard focus shows an outline",
         re.search(r"outline:\s*\d+px solid", focus) is not None and not focus_outline_removed(css)),
        ("the h1 is never hidden by CSS",
         "display: none" not in h1 and "visibility: hidden" not in h1),
        ("html and body clip sideways overflow",
         all("overflow-x: clip" in css_rule(css, tag) for tag in ("html", "body"))),
        ("project cards are one column on phones",
         "grid-template-columns" not in css_rule(everywhere, ".project")),
        ("project cards switch to two columns from 768 px",
         "minmax(0," in css_rule(media_block(css, "(min-width: 768px)"), ".project")),
        (f"card GitHub links have at least {MIN_TAP_PADDING_REM}rem tap padding",
         padding is not None and float(padding.group(1)) >= MIN_TAP_PADDING_REM),
    ]


def image_size(source, src):
    """Size of an image in bytes, or 0 if it can't be found."""
    if source.startswith("http"):
        url = source.rstrip("/") + "/" + src
        result = subprocess.run(["curl", "-fsSL", "--max-time", "30", "-o", "/dev/null",
                                 "-w", "%{size_download}", url], capture_output=True, text=True)
        return int(result.stdout) if result.returncode == 0 else 0
    path = Path(source).parent / src
    return path.stat().st_size if path.exists() else 0


def states(text, fact):
    """True if the fact appears as whole words, so '8 Grade' doesn't match '18 Grade'."""
    return re.search(rf"(?<!\w){re.escape(fact)}(?!\w)", text) is not None


def project_checks(page):
    names = [card["name"].strip() for card in page.cards]
    checks = [("project cards are in the planned order", names == [p[0] for p in PROJECTS])]
    for card, (name, repo, facts) in zip(page.cards, PROJECTS):
        text = " ".join(card["text"].split())
        checks += [
            (f"{name}: links to its GitHub repo", repo in card["links"]),
            (f"{name}: GitHub repo link resolves", link_resolves(repo)),
            (f"{name}: has an image", card["images"] >= 1),
            (f"{name}: lists tech tags", card["tags"] >= 2),
            *[(f"{name}: states '{fact}'", states(text, fact)) for fact in facts],
        ]
    return checks


def image_checks(page, source):
    sizes = {img.get("src", ""): image_size(source, img.get("src", "")) for img in page.images}
    return [
        (f"page has {EXPECTED_IMAGES} project images", len(page.images) == EXPECTED_IMAGES),
        ("no image is used twice", len(sizes) == len(page.images)),
        ("every image has alt text", all(img.get("alt", "").strip() for img in page.images)),
        ("every image sets width and height (no layout jump)",
         all(img.get("width") and img.get("height") for img in page.images)),
        ("no image comes from assets/raw", not any("assets/raw" in src for src in sizes)),
        ("every image file exists", all(sizes.values())),
        (f"every image is under {MAX_IMAGE_BYTES // 1000} KB",
         all(size < MAX_IMAGE_BYTES for size in sizes.values())),
        (f"images total under {MAX_TOTAL_IMAGE_BYTES // 1000} KB",
         sum(sizes.values()) < MAX_TOTAL_IMAGE_BYTES),
    ]


def run_checks(html, css, source):
    page = PageScanner()
    page.feed(html)
    return [
        ("<html> has lang='en'", page.html_lang == "en"),
        ("mobile viewport meta tag", page.has_viewport),
        ("<title> mentions Kenneth Wu", "Kenneth Wu" in page.title),
        ("exactly one <h1>", len(page.h1_texts) == 1),
        ("<h1> is 'Kenneth Wu'", [t.strip() for t in page.h1_texts] == ["Kenneth Wu"]),
        ("<h1> is visible to screen readers (not hidden)", not page.h1_hidden),
        ("pitch paragraph mentions McMaster", "McMaster" in page.pitch),
        ("project meta lines are plain lists, not middle-dot strings",
         len(page.meta_lines) == len(PROJECTS) and not any("·" in line for line in page.meta_lines)),
        ("GitHub link", GITHUB in page.links),
        ("LinkedIn link", LINKEDIN in page.links),
        ("Email link", EMAIL in page.links),
        ("links styles.css", "styles.css" in page.stylesheets),
        *[(f"section #{name} has an <h2>", name in page.sections_with_h2) for name in SECTIONS],
        *css_checks(css),
        *project_checks(page),
        *image_checks(page, source),
    ]


def main():
    source = sys.argv[1] if len(sys.argv) > 1 else str(HERE / "index.html")
    results = run_checks(load(source), load_css(source), source)
    for name, ok in results:
        print(f"{'PASS' if ok else 'FAIL'}  {name}")
    failed = sum(not ok for _, ok in results)
    print(f"\n{len(results) - failed}/{len(results)} checks passed for {source}")
    print("Layout needs a browser too: run tests/layout_check.js at 320, 360, 375, 768 and 1280 px.")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
