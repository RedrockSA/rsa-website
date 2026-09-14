"""Match the cover manifest against the Goodreads export to attach ISBNs.

Writes covers/manifest_isbn.csv adding goodreads_title, goodreads_author,
isbn13, isbn, match_method, match_score. Nothing is fetched here - run this
first and review the unmatched rows.
"""

import csv
import difflib
import os
import re
import sys
import unicodedata

MANIFEST = os.path.join("covers", "manifest.csv")
OUT = os.path.join("covers", "manifest_isbn.csv")
GOODREADS = "goodreads_library_export_full_read_list_260913.csv"

# Below this ratio a fuzzy title match is not trusted.
FUZZY_MIN = 0.82


def fold(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.encode("ascii", "ignore").decode("ascii")


def norm(s):
    """Aggressive title key: lowercase alphanumerics, leading article dropped."""
    s = fold(s).lower()
    s = s.replace("&", " and ")
    s = re.sub(r"['’]", "", s)
    s = re.sub(r"[^a-z0-9]+", " ", s).strip()
    s = re.sub(r"^(the|a|an)\s+", "", s)
    return re.sub(r"\s+", " ", s)


def surname(author):
    if not author.strip():
        return ""
    first = re.split(r"\s+and\s+|\s*&\s*|\s*;\s*", author.strip())[0].split(",")[0]
    toks = [t for t in fold(first).split() if t]
    while toks and re.sub(r"[^a-z]", "", toks[-1].lower()) in {
            "jr", "sr", "ii", "iii", "iv", "md", "phd"}:
        toks.pop()
    return re.sub(r"[^a-z]", "", toks[-1].lower()) if toks else ""


def author_ok(cover_author, g):
    """True if the cover surname appears among the Goodreads credits."""
    sn = surname(cover_author)
    if not sn:
        return False
    pool = []
    for field in ("Author", "Additional Authors"):
        for part in re.split(r",|\s+and\s+|&|;", g.get(field, "") or ""):
            if part.strip():
                pool.append(re.sub(r"[^a-z]", "", fold(part).strip().lower().split()[-1])
                            if part.strip().split() else "")
    pool = [p for p in pool if p]
    if sn in pool:
        return True
    # Transliteration drift, e.g. Dostoyevsky / Dostoevsky.
    return bool(difflib.get_close_matches(sn, pool, n=1, cutoff=0.85))


def clean_isbn(v):
    """Goodreads wraps ISBNs as ="0525429565" in some exports."""
    return re.sub(r'[^0-9Xx]', "", v or "").upper()


def main():
    with open(MANIFEST, encoding="utf-8-sig") as fh:
        covers = list(csv.DictReader(fh))
    with open(GOODREADS, encoding="utf-8-sig") as fh:
        gr = list(csv.DictReader(fh))

    # Index Goodreads rows by normalised full title and by title-before-colon.
    def title_keys(t):
        """All the shapes a Goodreads title might match on."""
        variants = {t}
        # "Title (Series, #1)" -> "Title"; also drop every parenthetical.
        variants.add(re.sub(r"\s*\([^()]*\)\s*$", "", t))
        variants.add(re.sub(r"\s*\([^()]*\)", " ", t))
        out = set()
        for v in variants:
            if v.strip():
                out.add(norm(v))
                out.add(norm(v.split(":", 1)[0]))
        return {k for k in out if k}

    by_key = {}
    for g in gr:
        if not g["Title"].strip():
            continue
        for key in title_keys(g["Title"]):
            by_key.setdefault(key, []).append(g)
    gr_keys = list(by_key)

    used = set()
    out = []
    unmatched = []

    for c in covers:
        sn = surname(c["author"])
        cands = []
        method = ""
        for key, how in ((norm(c["title_full"]), "title_full"),
                         (norm(c["title_short"]), "title_short")):
            if key in by_key:
                cands = by_key[key]
                method = how
                break

        if not cands:
            # Fuzzy fall back, but only accept if the surname also agrees.
            best = difflib.get_close_matches(norm(c["title_short"]), gr_keys,
                                             n=3, cutoff=FUZZY_MIN)
            for b in best:
                if any(author_ok(c["author"], g) for g in by_key[b]):
                    cands = by_key[b]
                    method = "fuzzy"
                    break

        # Prefer a candidate whose author surname matches and that is unused.
        pick = None
        for g in cands:
            if author_ok(c["author"], g) and id(g) not in used:
                pick = g
                break
        if pick is None:
            for g in cands:
                if id(g) not in used:
                    pick = g
                    method += "+author-mismatch"
                    break

        row = dict(c)
        if pick is None:
            row.update(goodreads_title="", goodreads_author="", isbn13="",
                       isbn="", match_method="UNMATCHED", match_score="")
            unmatched.append(c)
        else:
            used.add(id(pick))
            score = difflib.SequenceMatcher(
                None, norm(c["title_short"]), norm(pick["Title"])).ratio()
            row.update(goodreads_title=pick["Title"],
                       goodreads_author=pick["Author"],
                       isbn13=clean_isbn(pick["ISBN13"]),
                       isbn=clean_isbn(pick["ISBN"]),
                       match_method=method,
                       match_score="%.2f" % score)
        out.append(row)

    leftovers = [g for g in gr if id(g) not in used]

    with open(OUT, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)

    matched = len(out) - len(unmatched)
    no_isbn = [r for r in out if r["match_method"] != "UNMATCHED"
               and not r["isbn13"] and not r["isbn"]]
    flagged = [r for r in out if "author-mismatch" in r["match_method"]
               or r["match_method"] == "fuzzy"]

    print("covers: %d   goodreads rows: %d" % (len(covers), len(gr)))
    print("matched: %d   unmatched: %d   matched-but-no-ISBN: %d"
          % (matched, len(unmatched), len(no_isbn)))

    if flagged:
        print("\nMatches worth eyeballing (fuzzy or author mismatch):")
        for r in flagged:
            print("  %-42s -> %-48s [%s %s]"
                  % (r["title_short"][:42], r["goodreads_title"][:48],
                     r["match_method"], r["match_score"]))
    if no_isbn:
        print("\nMatched but Goodreads has no ISBN (needs another lookup key):")
        for r in no_isbn:
            print("  %-42s (%s)" % (r["title_short"][:42], r["goodreads_title"][:40]))
    if unmatched:
        print("\nNo Goodreads row found:")
        for r in unmatched:
            print("  %-42s  %s" % (r["title_short"][:42], r["author"]))
    if leftovers:
        print("\nGoodreads rows with no cover image:")
        for g in leftovers:
            print("  %-52s  %s" % (g["Title"][:52], g["Author"]))

    print("\nWrote", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
