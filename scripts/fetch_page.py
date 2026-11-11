#!/usr/bin/env python3
"""Fetch a web page and print its title and readable text. Standard library only.
Usage: fetch_page.py URL [--max-chars N]"""
import argparse, re, sys, urllib.request
from html.parser import HTMLParser

SKIP = {"script", "style", "noscript", "svg", "nav", "footer", "header", "form", "iframe"}
BLOCK = {"p", "div", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "br", "section", "article", "table"}

class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.out, self.title, self.skip, self.in_title = [], "", 0, False
    def handle_starttag(self, tag, attrs):
        if tag in SKIP: self.skip += 1
        if tag == "title": self.in_title = True
        if tag in BLOCK: self.out.append("\n")
    def handle_endtag(self, tag):
        if tag in SKIP and self.skip: self.skip -= 1
        if tag == "title": self.in_title = False
    def handle_data(self, d):
        if self.in_title: self.title += d
        elif not self.skip: self.out.append(d)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("url")
    p.add_argument("--max-chars", type=int, default=8000)
    a = p.parse_args()
    req = urllib.request.Request(a.url, headers={"User-Agent": "Mozilla/5.0 (research agent)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            ctype = r.headers.get("Content-Type", "")
            raw = r.read(3_000_000)
    except Exception as e:
        print(f"ERROR: could not fetch {a.url}: {e}")
        sys.exit(1)
    if "html" not in ctype and not raw.lstrip().startswith(b"<"):
        print(f"URL: {a.url}\nNOTE: not an HTML page ({ctype or 'unknown type'}); text not extracted.")
        return
    enc = re.search(r"charset=([\w-]+)", ctype)
    html = raw.decode(enc.group(1) if enc else "utf-8", errors="replace")
    t = Text(); t.feed(html)
    text = re.sub(r"[ \t\r\f\v]+", " ", "".join(t.out))
    text = re.sub(r"\n\s*\n+", "\n", text).strip()
    print(f"URL: {a.url}\nTITLE: {t.title.strip()}\n")
    print(text[:a.max_chars] + ("\n[truncated]" if len(text) > a.max_chars else ""))

if __name__ == "__main__":
    main()
