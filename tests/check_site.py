"""Checks index.html against the PRD. Run: python3 tests/check_site.py [URL]

With no URL it checks the local file; with a URL it checks the live site.
Uses only Python's standard library, so there is nothing to install.
"""

import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

GITHUB = "https://github.com/kennethwu08"
LINKEDIN = "https://www.linkedin.com/in/kenneth-wu-6857a0396/"
EMAIL = "mailto:wu1410@mcmaster.ca"


class PageScanner(HTMLParser):
    """Walks the HTML once and records the pieces the checks need."""

    def __init__(self):
        super().__init__()
        self.html_lang = None
        self.title = ""
        self.h1_texts = []
        self.links = []
        self.has_viewport = False
        self._in = None  # the tag whose text we are currently collecting

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.html_lang = a.get("lang")
        elif tag == "meta" and a.get("name") == "viewport":
            self.has_viewport = True
        elif tag == "a" and "href" in a:
            self.links.append(a["href"])
        if tag in ("title", "h1"):
            self._in = tag
            if tag == "h1":
                self.h1_texts.append("")

    def handle_endtag(self, tag):
        if tag == self._in:
            self._in = None

    def handle_data(self, data):
        if self._in == "title":
            self.title += data
        elif self._in == "h1":
            self.h1_texts[-1] += data


def load(source):
    if source.startswith("http"):
        with urllib.request.urlopen(source, timeout=15) as r:
            assert r.status == 200, f"{source} returned {r.status}"
            return r.read().decode()
    return Path(source).read_text()


def run_checks(html):
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
    ]


def main():
    source = sys.argv[1] if len(sys.argv) > 1 else "index.html"
    results = run_checks(load(source))
    for name, ok in results:
        print(f"{'PASS' if ok else 'FAIL'}  {name}")
    failed = sum(not ok for _, ok in results)
    print(f"\n{len(results) - failed}/{len(results)} checks passed for {source}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
