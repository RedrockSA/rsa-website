"""Resolve ISBNs for the books Goodreads exported without one.

Searches isbnsearch.org by title + author (robots.txt allows it), accepts a
result only when both the title and the author surname agree, and writes the
ISBNs back into covers/manifest_isbn.csv.

Throttled to one request every couple of seconds - this is a small free site.
"""

import argparse
import csv
import html
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

SRC = os.path.join("covers", "manifest_isbn.csv")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
      "RedRockSA-book-covers/1.0 (gloos@redrocksa.com)")
DELAY = 2.0

RESULT_RE = re.compile(
    r'<h2><a href="/isbn/[0-9Xx]+">(?P<title>.*?)</a></h2>.*?'
    r'(?:<p>Author[s]?:\s*(?P<author>.*?)</p>.*?)?'
    r'<p>ISBN-13:\s*(?P<isbn13>[0-9Xx]+)</p>.*?'
    r'<p>ISBN-10:\s*(?P<isbn10>[0-9Xx]+)</p>',
    re.S)


def fold(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.encode("ascii", "ignore").decode("ascii")


def norm(s):
    s = fold(html.unescape(s)).lower().replace("&", " and ")
    s = re.sub(r"['’]", "", s)
    s = re.sub(r"\s*\([^()]*\)", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s).strip()
    s = re.sub(r"^(the|a|an)\s+", "", s)
    return re.sub(r"\s+", " ", s)


def surnames(author):
    out = set()
    for part in re.split(r",|\s+and\s+|&|;", fold(author or "")):
        toks = part.split()
        while toks and re.sub(r"[^a-z]", "", toks[-1].lower()) in {
                "jr", "sr", "ii", "iii", "iv", "md", "phd"}:
            toks.pop()
        if toks:
            out.add(re.sub(r"[^a-z]", "", toks[-1].lower()))
    return {s for s in out if s}


def search(title, author):
    q = urllib.parse.urlencode({"s": "%s %s" % (title, author)})
    req = urllib.request.Request("https://isbnsearch.org/search?" + q,
                                 headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            page = r.read().decode("utf-8", "replace")
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
        return [], "error: %s" % e
    hits = []
    for m in RESULT_RE.finditer(page):
        hits.append({
            "title": html.unescape((m.group("title") or "").strip()),
            "author": html.unescape((m.group("author") or "").strip()),
            "isbn13": m.group("isbn13"),
            "isbn10": m.group("isbn10"),
        })
    return hits, ""


def pick(hits, want_title, want_author):
    """Best-scoring hit: title and author agreement, preferring real editions.

    isbnsearch returns every edition, including 979-8 print-on-demand reprints
    of public-domain classics. Those are usually not the edition that was read
    and cannot convert to an ISBN-10 for an Amazon /dp/ link, so they are
    ranked below genuine 978 publisher editions.
    """
    wt = norm(want_title)
    wa = surnames(want_author)
    scored = []
    for h in hits:
        ht = norm(h["title"])
        author_ok = bool(wa & surnames(h["author"])) if wa else False
        score = 0
        if ht == wt:
            score += 4
        elif ht.startswith(wt) or wt.startswith(ht):
            score += 2
        if author_ok:
            score += 3
        if h["isbn13"].startswith("9798"):
            score -= 4          # Amazon KDP reprint
        elif h["isbn13"].startswith("978"):
            score += 2
        scored.append((score, author_ok, h))

    scored.sort(key=lambda t: -t[0])
    if not scored or scored[0][0] < 4:
        return None, ""
    score, author_ok, h = scored[0]
    return h, ("title+author" if author_ok else "title-only") + " s%d" % score


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    with open(SRC, encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))

    todo = [r for r in rows if not r["isbn13"] and not r["isbn"]]
    if args.limit:
        todo = todo[:args.limit]
    print("books missing an ISBN: %d\n" % len(todo))

    found = 0
    for i, r in enumerate(todo, 1):
        hits, err = search(r["title_short"], r["author"])
        time.sleep(DELAY)
        if err:
            print("[%2d/%d] %-38s %s" % (i, len(todo), r["title_short"][:38], err))
            continue
        hit, how = pick(hits, r["title_short"], r["author"])
        if hit:
            r["isbn13"] = hit["isbn13"]
            r["isbn"] = hit["isbn10"]
            r["match_method"] = (r["match_method"] + "+isbnsearch").strip("+")
            found += 1
            print("[%2d/%d] %-38s %s  (%s | %s)"
                  % (i, len(todo), r["title_short"][:38], hit["isbn13"], how,
                     hit["title"][:34]))
        else:
            print("[%2d/%d] %-38s no confident match (%d hits)"
                  % (i, len(todo), r["title_short"][:38], len(hits)))

    print("\nresolved %d of %d" % (found, len(todo)))
    if args.dry_run:
        print("[dry run] manifest not written")
        return 0

    with open(SRC, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("Updated", SRC)
    return 0


if __name__ == "__main__":
    sys.exit(main())
