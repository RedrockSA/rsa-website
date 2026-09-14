"""Rename extracted covers to authorlastname_title-slug.png per the manifest.

Run with --dry-run first to review the mapping. The manifest is rewritten with
a final_filename column so the provisional -> final mapping is preserved.
"""

import argparse
import csv
import os
import re
import sys
import unicodedata

MANIFEST = os.path.join("covers", "manifest.csv")
COVERS = "covers"

# Name suffixes that are not the surname.
SUFFIXES = {"jr", "sr", "ii", "iii", "iv", "md", "phd"}


def ascii_fold(s):
    """Strip accents and drop anything outside ASCII."""
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).encode(
        "ascii", "ignore").decode("ascii")


def last_name(author):
    """Surname of the first credited author, lowercased, letters/digits only."""
    if not author.strip():
        return ""
    # First author only: split on "and" / "&" / ";"
    first = re.split(r"\s+and\s+|\s*&\s*|\s*;\s*", author.strip())[0]
    # Drop a trailing ", Jr." style suffix.
    first = first.split(",")[0]
    tokens = [t for t in ascii_fold(first).split() if t]
    while tokens and re.sub(r"[^a-z]", "", tokens[-1].lower()) in SUFFIXES:
        tokens.pop()
    if not tokens:
        return ""
    return re.sub(r"[^a-z0-9]", "", tokens[-1].lower())


def title_slug(title):
    """Lowercase, hyphen-separated, ASCII, no punctuation."""
    s = ascii_fold(title).lower()
    s = s.replace("&", " and ")
    s = re.sub(r"['’]", "", s)      # apostrophes vanish, not hyphenate
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="print the mapping without touching any files")
    args = ap.parse_args()

    with open(MANIFEST, encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))

    used = {}
    blocked = []
    for r in rows:
        ln = last_name(r["author"])
        slug = title_slug(r["title_short"])
        if not ln or not slug:
            r["final_filename"] = ""
            blocked.append(r["filename"])
            continue
        base = "%s_%s" % (ln, slug)
        n = used.get(base, 0) + 1
        used[base] = n
        r["final_filename"] = ("%s.png" % base) if n == 1 else ("%s-%d.png" % (base, n))

    if blocked:
        print("Cannot name (author and/or title missing in manifest) - left in place:")
        for f in blocked:
            print("   ", f)
        print()

    renames = [(r["filename"], r["final_filename"]) for r in rows if r["final_filename"]]
    collisions = sorted(b for b, n in used.items() if n > 1)
    if collisions:
        print("Collision groups resolved with -2/-3: %s\n" % ", ".join(collisions))

    for src, dst in renames:
        print("%-16s -> %s" % (src, dst))

    if args.dry_run:
        print("\n[dry run] %d files would be renamed; manifest unchanged." % len(renames))
        return 0

    # Two-phase rename so a new name never clobbers a file not yet renamed.
    tmp = []
    for src, dst in renames:
        s = os.path.join(COVERS, src)
        if not os.path.exists(s):
            print("missing, skipped:", src)
            continue
        t = os.path.join(COVERS, "__tmp__" + src)
        os.replace(s, t)
        tmp.append((t, os.path.join(COVERS, dst)))
    for t, d in tmp:
        os.replace(t, d)

    fields = list(rows[0].keys())
    with open(MANIFEST, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print("\nRenamed %d files; manifest updated with final_filename." % len(tmp))
    return 0


if __name__ == "__main__":
    sys.exit(main())
