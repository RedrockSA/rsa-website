"""Regenerate scripts/tag_books.py so its table matches data/books.csv exactly.

Run this after hand-editing tags in the CSV. It makes the script idempotent:
re-running tag_books.py then reproduces the edited state instead of reverting
it to whatever was hard-coded before.
"""

import csv
import os

DB = os.path.join("data", "books.csv")
TARGET = os.path.join("scripts", "tag_books.py")

HEADER = '''"""Rewrite the classification columns in data/books.csv from the table below.

The table is the source of truth for tags. It is regenerated from the CSV by
scripts/_regen_tag_table.py after any round of hand-editing, so re-running this
reproduces that state rather than reverting it.

If you edit tags in the CSV by hand, run _regen_tag_table.py afterwards or the
next run of this script will overwrite them.

era_published is derived from the year and never appears in the table.
Columns this script never touches: notes, my_rating, date_read, ISBNs, links.
"""

import csv
import os
import sys

DB = os.path.join("data", "books.csv")

# title_short -> (type, business_genre, subject, era_subject, geography, home_shelf)
T = {
'''

FOOTER = '''}

MANAGED = ["type", "business_genre", "subject", "era_subject",
           "era_published", "geography", "home_shelf"]


def era_published(year):
    try:
        y = int(str(year).strip()[:4])
    except (ValueError, TypeError):
        return ""
    if y < 1000:
        return "ancient"
    if y < 1900:
        return "pre-1900"
    return "%ds" % (y // 10 * 10)


def main():
    with open(DB, encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    fields = list(rows[0].keys())

    titles = {r["title_short"] for r in rows}
    missing = [r["title_short"] for r in rows if r["title_short"] not in T]
    extra = [t for t in T if t not in titles]
    if missing:
        print("NOT IN TABLE (left untouched): %s" % ", ".join(missing))
    if extra:
        print("IN TABLE BUT NOT IN CSV: %s" % ", ".join(extra))

    for r in rows:
        t = T.get(r["title_short"])
        if not t:
            continue
        (r["type"], r["business_genre"], r["subject"], r["era_subject"],
         r["geography"], r["home_shelf"]) = t
        r["era_published"] = era_published(
            r["original_pub_year"] or r["year_published"])
        flat = [r[c] for c in MANAGED]
        r["tags"] = ";".join(sorted(
            {v.strip() for part in flat for v in part.split(";") if v.strip()}))

    with open(DB, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    from collections import Counter
    print("Tagged %d books -> %s\\n" % (len(rows), DB))
    for col in MANAGED:
        c = Counter()
        for r in rows:
            for v in (r[col] or "").split(";"):
                if v.strip():
                    c[v.strip()] += 1
        print("%s (%d distinct)" % (col.upper(), len(c)))
        print("   " + ", ".join("%s:%d" % kv for kv in c.most_common()))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''

COLS = ["type", "business_genre", "subject", "era_subject",
        "geography", "home_shelf"]


def main():
    with open(DB, encoding="utf-8-sig") as fh:
        rows = sorted(csv.DictReader(fh), key=lambda r: r["title_short"].lower())

    lines = []
    for r in rows:
        title = r["title_short"].replace("\\", "\\\\").replace('"', '\\"')
        vals = '","'.join(r[c] for c in COLS)
        lines.append(' "%s": ("%s"),' % (title, vals))

    with open(TARGET, "w", encoding="utf-8") as fh:
        fh.write(HEADER + "\n".join(lines) + "\n" + FOOTER)

    print("regenerated %s from %d rows in %s" % (TARGET, len(rows), DB))


if __name__ == "__main__":
    main()
