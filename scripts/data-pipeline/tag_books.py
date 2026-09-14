"""Rewrite the classification columns in data/books.csv from the table below.

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
 "\"Surely You're Joking, Mr. Feynman!\"": ("non-fiction","","memoir;science","mid-20th-century","united-states","memoir-biography"),
 "12 Rules for Life": ("non-fiction","personal-effectiveness","psychology;philosophy","","global","psychology"),
 "1776": ("non-fiction","leadership","history;war","early-modern","united-states","history"),
 "1984": ("fiction","","philosophy","","britain","relevant-fiction"),
 "21 Lessons for the 21st Century": ("non-fiction","strategy","history;technology;philosophy","","global","history"),
 "A Brief History of Motion": ("non-fiction","innovation","history;technology","ancient","global","history"),
 "A Brief History of Time": ("non-fiction","","science;space","","space","technology-and-science"),
 "A History of the World in 6 Glasses": ("non-fiction","economics","history;food","ancient","global","history"),
 "A Necessary Lie": ("non-fiction","","memoir","contemporary","east-asia","memoir-biography"),
 "A. Lincoln": ("non-fiction","leadership","biography;history;politics","19th-century","united-states","memoir-biography"),
 "Alexander Hamilton": ("non-fiction","leadership;economics","biography;history;politics","early-modern","united-states","memoir-biography"),
 "All Creatures Great and Small": ("fiction","","memoir;nature","early-20th-century","britain","memoir-biography"),
 "American Sherlock": ("non-fiction","","true-crime;science;biography","early-20th-century","united-states","history"),
 "An Economic History of the World since 1400": ("non-fiction","economics","history;economics","ancient","global","economics"),
 "Ancient Rome": ("non-fiction","","history;war","ancient","ancient-rome","history"),
 "Animal Farm": ("fiction","","philosophy","","russia","relevant-fiction"),
 "Applied Economics": ("non-fiction","economics","economics","","global","economics"),
 "Assyria": ("non-fiction","","history","ancient","mesopotamia","history"),
 "Astrophysics for People in a Hurry": ("non-fiction","","science;space","","space","technology-and-science"),
 "Atlas Shrugged": ("fiction","","philosophy","","united-states","relevant-fiction"),
 "Atomic Habits": ("non-fiction","productivity;personal-effectiveness","psychology","","global","personal-effectiveness"),
 "Ayn Rand and the World She Made": ("non-fiction","","biography","mid-20th-century","united-states","memoir-biography"),
 "Band of Brothers": ("non-fiction","leadership","history;war","wwii","europe","teamwork"),
 "Basic Economics": ("non-fiction","economics","economics","","global","corporate-history"),
 "Be Useful": ("non-fiction","personal-effectiveness","memoir;psychology","contemporary","united-states","memoir-biography"),
 "Be Where Your Feet Are": ("non-fiction","leadership;personal-effectiveness","memoir;psychology","contemporary","united-states","leadership"),
 "Benjamin Franklin": ("non-fiction","entrepreneurship;leadership","biography;history","early-modern","united-states","memoir-biography"),
 "Brave Companions": ("non-fiction","","biography;history;essays","19th-century","united-states","history"),
 "Cable Cowboy": ("non-fiction","strategy;entrepreneurship;investing","biography;technology","late-20th-century","united-states","corporate-history"),
 "Capitalism": ("non-fiction","economics","economics;philosophy;politics","","united-states","economics"),
 "Churchill & Orwell": ("non-fiction","leadership","biography;history;politics","wwii","britain","memoir-biography"),
 "Creativity, Inc.": ("non-fiction","leadership;innovation;culture;management","memoir;technology","late-20th-century","united-states","corporate-history"),
 "Critical Chain": ("non-fiction","project-management;operations","business;business-novel","","global","operations"),
 "David and Goliath": ("non-fiction","strategy","psychology","","global","social-commentary"),
 "Educated": ("non-fiction","","memoir","contemporary","united-states","memoir-biography"),
 "Elon Musk": ("non-fiction","entrepreneurship;innovation","biography;technology","contemporary","united-states","memoir-biography"),
 "Empire of Pain": ("non-fiction","culture","history;true-crime;medicine","contemporary","united-states","corporate-history"),
 "Endurance": ("non-fiction","leadership","history;nature","early-20th-century","antarctica","memoir-biography"),
 "Essentialism": ("non-fiction","productivity;personal-effectiveness;strategy","psychology","","global","personal-effectiveness"),
 "Fooled by Randomness": ("non-fiction","investing;decision-making","economics;psychology","","global","psychology"),
 "From Beirut to Jerusalem": ("non-fiction","","history;politics;memoir","late-20th-century","middle-east","history"),
 "Genghis Khan and the Making of the Modern World": ("non-fiction","leadership;strategy","history;biography","medieval","mongolia","history"),
 "Genius": ("non-fiction","","biography;science","mid-20th-century","united-states","memoir-biography"),
 "Good Energy": ("non-fiction","","medicine;health","","global","health"),
 "Good to Great": ("non-fiction","leadership;strategy;management","business","","united-states","strategy"),
 "Grit": ("non-fiction","personal-effectiveness","psychology","","global","personal-effectiveness"),
 "Henry V": ("non-fiction","leadership","biography;history;war","medieval","britain","history"),
 "How to Know a Person": ("non-fiction","leadership;culture;psychology","psychology","","global","psychology"),
 "It Worked for Me": ("non-fiction","leadership","memoir","late-20th-century","united-states","leadership"),
 "John Adams": ("non-fiction","leadership","biography;history","early-modern","united-states","memoir-biography"),
 "Leonardo da Vinci": ("non-fiction","innovation","biography","early-modern","europe","memoir-biography"),
 "Loonshots": ("non-fiction","innovation;strategy;management","business;science","","global","history"),
 "Making It So": ("non-fiction","","memoir","contemporary","britain","memoir-biography"),
 "Man's Search for Meaning": ("non-fiction","personal-effectiveness","memoir;psychology;philosophy","wwii","europe","psychology"),
 "Meditations": ("non-fiction","leadership;personal-effectiveness","philosophy","ancient","ancient-rome","personal-effectiveness"),
 "Muppets in Moscow": ("non-fiction","operations;culture","memoir;history","late-20th-century","russia","corporate-history"),
 "My Next Breath": ("non-fiction","","memoir","contemporary","united-states","memoir-biography"),
 "Never Split the Difference": ("non-fiction","negotiation","psychology","","global","strategy"),
 "Originals": ("non-fiction","innovation;leadership","psychology;business","","global","psychology"),
 "Outliers": ("non-fiction","strategy","psychology;economics","","global","social-commentary"),
 "Outlive": ("non-fiction","","medicine;health","","global","health"),
 "Poor Charlie's Almanack": ("non-fiction","investing;decision-making","essays;philosophy","contemporary","united-states","psychology"),
 "Powers and Thrones": ("non-fiction","","history","medieval","europe","history"),
 "Principles": ("non-fiction","leadership;management;decision-making;investing","business;memoir","","united-states","operations"),
 "Project Hail Mary": ("fiction","","science;space","","space","relevant-fiction"),
 "Romney": ("non-fiction","leadership","biography;politics","contemporary","united-states","memoir-biography"),
 "Salt": ("non-fiction","economics","history;food","ancient","global","history"),
 "Shoe Dog": ("non-fiction","entrepreneurship;leadership","memoir;business","late-20th-century","united-states","memoir-biography"),
 "Source Code": ("non-fiction","entrepreneurship","memoir;biography;technology","late-20th-century","united-states","memoir-biography"),
 "Steve Jobs": ("non-fiction","entrepreneurship;innovation;leadership","biography;technology","late-20th-century","united-states","memoir-biography"),
 "Subscribed": ("non-fiction","strategy;marketing;operations","business","","global","economics"),
 "Talking to Strangers": ("non-fiction","negotiation;leadership","psychology","","global","social-commentary"),
 "Team of Rivals": ("non-fiction","leadership;management","biography;history","19th-century","united-states","leadership"),
 "Team of Teams": ("non-fiction","leadership;management;operations","business;war","contemporary","middle-east","leadership"),
 "The Anxious Generation": ("non-fiction","culture","psychology;technology","","global","psychology"),
 "The Box": ("non-fiction","operations;strategy;economics","history;technology;economics","late-20th-century","global","operations"),
 "The Boys in the Boat": ("non-fiction","leadership","history;sports","early-20th-century","united-states","memoir-biography"),
 "The Checklist Manifesto": ("non-fiction","operations;project-management;management","medicine;psychology","","global","operations"),
 "The Coddling of the American Mind": ("non-fiction","culture","psychology","contemporary","united-states","psychology"),
 "The Conquer Code": ("non-fiction","personal-effectiveness;leadership","psychology","contemporary","united-states","memoir-biography"),
 "The Double Helix": ("non-fiction","","science;memoir","mid-20th-century","britain","technology-and-science"),
 "The Emperor of All Maladies": ("non-fiction","","medicine;history;science","multi-era","global","health"),
 "The Emperors of Chocolate": ("non-fiction","competitive-landscape;strategy;marketing","history;business","20th-century","united-states","corporate-history"),
 "The Food Lab": ("non-fiction","","food;science","","global","health"),
 "The Fountainhead": ("fiction","entrepreneurship","philosophy;politics","","united-states","relevant-fiction"),
 "The Gene": ("non-fiction","","science;medicine;history","multi-era","global","health"),
 "The Goal": ("non-fiction","operations;project-management;management","business;business-novel","","united-states","operations"),
 "The Greater Journey": ("non-fiction","","history;biography","19th-century","europe","history"),
 "The History of Money": ("non-fiction","economics;investing","history;economics","ancient","global","economics"),
 "The Infinite Game": ("non-fiction","leadership;strategy","business","","global","strategy"),
 "The Last Lecture": ("non-fiction","personal-effectiveness","memoir;philosophy","contemporary","united-states","memoir-biography"),
 "The Martian": ("fiction","","science;space","","space","relevant-fiction"),
 "The Mysterious Case of Rudolf Diesel": ("non-fiction","innovation","history;biography;technology;true-crime","early-20th-century","europe","memoir-biography"),
 "The Omnivore's Dilemma": ("non-fiction","operations","food;nature;economics","contemporary","united-states","health"),
 "The Only Plane in the Sky": ("non-fiction","leadership","history","contemporary","united-states","history"),
 "The Personal MBA": ("non-fiction","management;strategy;marketing;operations;entrepreneurship","business","","global","operations"),
 "The Purpose Code": ("non-fiction","personal-effectiveness","psychology","","global","psychology"),
 "The Ruthless Elimination of Hurry": ("non-fiction","productivity","religion;psychology","","global","personal-effectiveness"),
 "The Smartest Guys in the Room": ("non-fiction","management;culture;economics","business;true-crime;history","contemporary","united-states","corporate-history"),
 "The Snowball": ("non-fiction","investing;entrepreneurship","biography;business","20th-century","united-states","memoir-biography"),
 "The Theory of Everything": ("non-fiction","","science;space","","space","technology-and-science"),
 "The Thinking Machine": ("non-fiction","strategy;innovation;entrepreneurship","biography;technology;business","contemporary","united-states","technology-and-science"),
 "The Wright Brothers": ("non-fiction","innovation;entrepreneurship","biography;history;technology","early-20th-century","united-states","memoir-biography"),
 "Thinking, Fast and Slow": ("non-fiction","decision-making","psychology;economics","","global","psychology"),
 "Titan": ("non-fiction","entrepreneurship;investing;strategy","biography;history;business","19th-century","united-states","memoir-biography"),
 "Truman": ("non-fiction","leadership","biography;history","mid-20th-century","united-states","memoir-biography"),
 "Undaunted Courage": ("non-fiction","leadership;project-management","history;biography","19th-century","united-states","teamwork"),
 "What It Takes": ("non-fiction","entrepreneurship;leadership;investing","memoir;business","contemporary","united-states","memoir-biography"),
 "Why Nations Fail": ("non-fiction","economics;strategy","economics;history;politics","multi-era","global","economics"),
 "William Shakespeare": ("non-fiction","","essays;literature","early-modern","britain","relevant-fiction"),
}

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
    print("Tagged %d books -> %s\n" % (len(rows), DB))
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
