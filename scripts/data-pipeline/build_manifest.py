"""Write covers/manifest.csv from vision-read title/author data.

title_short is derived mechanically: everything before the first colon.
"""

import csv
import os

# (stem, title_full, author, confidence, notes)
DATA = [
    # ---- Block 1 ----
    ("block01_r1c1", "Cable Cowboy: John Malone and the Rise of the Modern Cable Business", "Mark Robichaux", "high", ""),
    ("block01_r1c2", "The Lord God Made Them All", "James Herriot", "high", ""),
    ("block01_r1c3", "All Things Wise and Wonderful", "James Herriot", "high", ""),
    ("block01_r1c4", "All Things Bright and Beautiful", "James Herriot", "high", ""),
    ("block01_r1c5", "All Creatures Great and Small", "James Herriot", "high", ""),
    ("block01_r1c6", "The Martian", "Andy Weir", "high", ""),
    ("block01_r2c1", "Travels with Charley: In Search of America", "John Steinbeck", "high", ""),
    ("block01_r2c2", "Alexander Hamilton", "Ron Chernow", "high", ""),
    ("block01_r2c3", "The Boys in the Boat: Nine Americans and Their Epic Quest for Gold at the 1936 Berlin Olympics", "Daniel James Brown", "high", ""),
    ("block01_r2c4", "The Emperor of All Maladies: A Biography of Cancer", "Siddhartha Mukherjee", "high", "subtitle set in very small caps; read at low resolution"),
    ("block01_r2c5", "The Gene: An Intimate History", "Siddhartha Mukherjee", "high", ""),
    ("block01_r2c6", "Ancient Rome: The Rise and Fall of an Empire", "Simon Baker", "high", ""),
    ("block01_r3c1", "1776", "David McCullough", "high", ""),
    ("block01_r3c2", "John Adams", "David McCullough", "high", ""),
    ("block01_r3c3", "Brave Companions: Portraits in History", "David McCullough", "high", ""),
    ("block01_r3c4", "Good to Great", "Jim Collins", "high", "cover subtitle ('Why Some Companies Make the Leap... and Others Don't') too small to read reliably; omitted"),
    ("block01_r3c5", "Shoe Dog: A Memoir by the Creator of Nike", "Phil Knight", "high", ""),
    ("block01_r3c6", "Atlas Shrugged", "Ayn Rand", "high", ""),
    ("block01_r4c1", "Outliers: The Story of Success", "Malcolm Gladwell", "high", ""),
    ("block01_r4c2", "David and Goliath: Underdogs, Misfits, and the Art of Battling Giants", "Malcolm Gladwell", "high", "subtitle read at low resolution"),
    ("block01_r4c3", "An Economic History of the World since 1400", "Donald Harreld", "high", "Great Courses; lecturer name is illegible on the cover - supplied by user (audible.com/pd/B01K4ZNTFS)"),
    ("block01_r4c4", "The Woman in White", "Wilkie Collins", "high", ""),
    ("block01_r4c5", "Truman", "David McCullough", "high", ""),
    ("block01_r4c6", "Genghis Khan and the Making of the Modern World", "Jack Weatherford", "high", ""),

    # ---- Block 2 ----
    ("block02_r1c1", "Capitalism: The Unknown Ideal", "Ayn Rand", "high", "source crop was clipped at the top; image replaced with user-supplied Rand_Capitalism.jpg (Signet Authorized Edition - a different edition cover than the screenshot) - NOT a crop from the source screenshots"),
    ("block02_r1c2", "Salt: A World History", "Mark Kurlansky", "high", ""),
    ("block02_r1c3", "21 Lessons for the 21st Century", "Yuval Noah Harari", "high", ""),
    ("block02_r1c4", "Bossypants", "Tina Fey", "high", ""),
    ("block02_r1c5", "The Purpose Code: How to Unlock Meaning, Maximize Happiness, and Leave a Lasting Legacy", "Jordan Grumet", "high", ""),
    ("block02_r1c6", "Poor Charlie's Almanack: The Wit and Wisdom of Charles T. Munger", "Charles T. Munger", "high", "edited by Peter D. Kaufman; foreword by Warren E. Buffett"),
    ("block02_r2c1", "Henry V: The Astonishing Triumph of England's Greatest Warrior King", "Dan Jones", "high", "subtitle read at low resolution"),
    ("block02_r2c2", "A History of the World in 6 Glasses", "Tom Standage", "high", ""),
    ("block02_r2c3", "The Personal MBA", "Josh Kaufman", "high", "10th Anniversary Edition"),
    ("block02_r2c4", "The Ruthless Elimination of Hurry", "John Mark Comer", "high", "foreword by John Ortberg"),
    ("block02_r2c5", "The Three-Body Problem", "Cixin Liu", "high", "translated by Ken Liu"),
    ("block02_r2c6", "A Brief History of Time", "Stephen Hawking", "high", ""),
    ("block02_r3c1", "The Theory of Everything: The Origin and Fate of the Universe", "Stephen W. Hawking", "high", ""),
    ("block02_r3c2", "See You in the Cosmos", "Jack Cheng", "high", ""),
    ("block02_r3c3", "\"Surely You're Joking, Mr. Feynman!\": Adventures of a Curious Character", "Richard P. Feynman", "high", ""),
    ("block02_r3c4", "The Double Helix", "James D. Watson", "high", ""),
    ("block02_r3c5", "Principles", "Ray Dalio", "high", ""),
    ("block02_r3c6", "The 5 Love Languages: The Secret to Love That Lasts", "Gary Chapman", "high", ""),
    ("block02_r4c1", "Astrophysics for People in a Hurry", "Neil deGrasse Tyson", "high", ""),
    ("block02_r4c2", "The Only Plane in the Sky: An Oral History of 9/11", "Garrett M. Graff", "medium", "author name on cover is very small; read at low resolution"),
    ("block02_r4c3", "How to Know a Person: The Art of Seeing Others Deeply and Being Deeply Seen", "David Brooks", "high", ""),
    ("block02_r4c4", "The Goal", "Eliyahu M. Goldratt", "medium", "with Jeff Cox; 30th Anniversary Edition. Cover subtitle too small to read reliably"),
    ("block02_r4c5", "Source Code: My Beginnings", "Bill Gates", "high", ""),
    ("block02_r4c6", "The Way of Kings", "Brandon Sanderson", "medium", "title is heavily stylized and low-contrast; 'Book One of The Stormlight Archive' visible below"),

    # ---- Block 3 ----
    ("block03_r1c1", "Be Useful: Seven Tools for Life", "Arnold Schwarzenegger", "high", ""),
    ("block03_r1c2", "Romney: A Reckoning", "McKay Coppins", "high", ""),
    ("block03_r1c3", "Ikigai: The Japanese Secret to a Long and Happy Life", "Hector Garcia and Francesc Miralles", "medium", "author line on cover is very small; read at low resolution"),
    ("block03_r1c4", "What It Takes: Lessons in the Pursuit of Excellence", "Stephen A. Schwarzman", "high", ""),
    ("block03_r1c5", "Edgedancer", "Brandon Sanderson", "high", "'From the Stormlight Archive'"),
    ("block03_r1c6", "A Brief History of Motion: From the Wheel, to the Car, to What Comes Next", "Tom Standage", "high", ""),
    ("block03_r2c1", "The Mysterious Case of Rudolf Diesel: Genius, Power, and Deception on the Eve of World War I", "Douglas Brunt", "high", ""),
    ("block03_r2c2", "Oathbringer", "Brandon Sanderson", "high", "Book Three of The Stormlight Archive"),
    ("block03_r2c3", "It Worked for Me: In Life and Leadership", "Colin Powell", "high", "with Tony Koltz"),
    ("block03_r2c4", "Words of Radiance", "Brandon Sanderson", "high", "Book Two of The Stormlight Archive"),
    ("block03_r2c5", "The Infinite Game", "Simon Sinek", "high", ""),
    ("block03_r2c6", "The Checklist Manifesto: How to Get Things Right", "Atul Gawande", "high", ""),
    ("block03_r3c1", "Assyria: The Rise and Fall of the World's First Empire", "Eckart Frahm", "high", ""),
    ("block03_r3c2", "The History of Money: A Story of Humanity", "David McWilliams", "high", ""),
    ("block03_r3c3", "The Thinking Machine: Jensen Huang, Nvidia, and the World's Most Coveted Microchip", "Stephen Witt", "high", ""),
    ("block03_r3c4", "Persuasion", "Jane Austen", "high", "Oxford World's Classics"),
    ("block03_r3c5", "Mansfield Park", "Jane Austen", "medium", "Penguin Classics; title set in small italics, read at low resolution"),
    ("block03_r3c6", "Critical Chain", "Eliyahu M. Goldratt", "high", ""),
    ("block03_r4c1", "My Next Breath: A Memoir", "Jeremy Renner", "high", ""),
    ("block03_r4c2", "Emma", "Jane Austen", "medium", "Penguin Classics; title set in small italics, read at low resolution"),
    ("block03_r4c3", "How to Become a Federal Criminal: An Illustrated Handbook for the Aspiring Offender", "Mike Chase", "high", ""),
    ("block03_r4c4", "Northanger Abbey", "Jane Austen", "high", ""),
    ("block03_r4c5", "Sense and Sensibility", "Jane Austen", "medium", "Penguin Classics; title set in small italics, read at low resolution"),
    ("block03_r4c6", "Ready Player One", "Ernest Cline", "high", ""),

    # ---- Block 4 ----
    ("block04_r1c1", "Steve Jobs", "Walter Isaacson", "high", ""),
    ("block04_r1c2", "From Beirut to Jerusalem", "Thomas L. Friedman", "high", ""),
    ("block04_r1c3", "Band of Brothers", "Stephen E. Ambrose", "high", ""),
    ("block04_r1c4", "William Shakespeare: Comedies, Histories, and Tragedies", "Peter Saccio", "medium", "Great Courses cover; lecturer name is very small, read at low resolution"),
    ("block04_r1c5", "A. Lincoln: A Biography", "Ronald C. White, Jr.", "medium", "title appears as a signature; subtitle too small to confirm on the cover"),
    ("block04_r1c6", "Elon Musk: Tesla, SpaceX, and the Quest for a Fantastic Future", "Ashlee Vance", "high", ""),
    ("block04_r2c1", "Leonardo da Vinci", "Walter Isaacson", "high", ""),
    ("block04_r2c2", "The Princess Bride", "William Goldman", "high", "30th Anniversary Edition"),
    ("block04_r2c3", "The Glass Castle: A Memoir", "Jeannette Walls", "high", ""),
    ("block04_r2c4", "The Outsiders", "S. E. Hinton", "high", ""),
    ("block04_r2c5", "The Hobbit, or There and Back Again", "J. R. R. Tolkien", "high", ""),
    ("block04_r2c6", "Educated: A Memoir", "Tara Westover", "high", ""),
    ("block04_r3c1", "Animal Farm", "George Orwell", "high", "Centennial Edition, foreword by Ann Patchett"),
    ("block04_r3c2", "Pride and Prejudice", "Jane Austen", "high", ""),
    ("block04_r3c3", "Harry Potter and the Deathly Hallows", "J. K. Rowling", "high", ""),
    ("block04_r3c4", "Harry Potter and the Half-Blood Prince", "J. K. Rowling", "medium", "title lettering is low-contrast against the artwork; identified largely from the cover art"),
    ("block04_r3c5", "Harry Potter and the Order of the Phoenix", "J. K. Rowling", "medium", "illustrated edition (Jim Kay); title lettering is low-contrast against the artwork"),
    ("block04_r3c6", "Harry Potter and the Goblet of Fire", "J. K. Rowling", "high", ""),
    ("block04_r4c1", "Harry Potter and the Prisoner of Azkaban", "J. K. Rowling", "high", ""),
    ("block04_r4c2", "Harry Potter and the Chamber of Secrets", "J. K. Rowling", "high", ""),
    ("block04_r4c3", "Harry Potter and the Sorcerer's Stone", "J. K. Rowling", "high", ""),
    ("block04_r4c4", "1984", "George Orwell", "high", ""),
    ("block04_r4c5", "The Guns of August", "Barbara W. Tuchman", "high", ""),
    ("block04_r4c6", "The Third Chimpanzee: The Evolution and Future of the Human Animal", "Jared Diamond", "high", ""),

    # ---- Block 5 ----
    ("block05_r1c1", "The Lion, the Witch and the Wardrobe", "C. S. Lewis", "high", "The Chronicles of Narnia"),
    ("block05_r1c2", "The Return of the King", "J. R. R. Tolkien", "high", "The Lord of the Rings, Part Three"),
    ("block05_r1c3", "The Two Towers", "J. R. R. Tolkien", "high", "The Lord of the Rings, Part Two"),
    ("block05_r1c4", "The Fellowship of the Ring", "J. R. R. Tolkien", "high", "The Lord of the Rings, Part One"),
    ("block05_r1c5", "Never Split the Difference: Negotiating as If Your Life Depended on It", "Chris Voss", "high", "with Tahl Raz"),
    ("block05_r1c6", "Basic Economics: A Citizen's Guide to the Economy", "Thomas Sowell", "high", ""),
    ("block05_r2c1", "Why Nations Fail: The Origins of Power, Prosperity, and Poverty", "Daron Acemoglu and James Robinson", "high", ""),
    ("block05_r2c2", "Be Where Your Feet Are: Seven Principles to Keep You Present, Grounded, and Thriving", "Scott M. O'Neil", "high", "with Randall A. Wright"),
    ("block05_r2c3", "Seven Miracles That Saved America", "Chris Stewart and Ted Stewart", "high", ""),
    ("block05_r2c4", "The Warmth of Other Suns: The Epic Story of America's Great Migration", "Isabel Wilkerson", "high", ""),
    ("block05_r2c5", "The Coddling of the American Mind: How Good Intentions and Bad Ideas Are Setting Up a Generation for Failure", "Greg Lukianoff and Jonathan Haidt", "high", ""),
    ("block05_r2c6", "Team of Teams: New Rules of Engagement for a Complex World", "Stanley McChrystal", "high", "credited on cover as General Stanley McChrystal, U.S. Army, Retired"),
    ("block05_r3c1", "Applied Economics: Thinking Beyond Stage One", "Thomas Sowell", "high", ""),
    ("block05_r3c2", "Essentialism: The Disciplined Pursuit of Less", "Greg McKeown", "high", ""),
    ("block05_r3c3", "Loonshots: How to Nurture the Crazy Ideas That Win Wars, Cure Diseases, and Transform Industries", "Safi Bahcall", "high", ""),
    ("block05_r3c4", "The Fountainhead", "Ayn Rand", "high", ""),
    ("block05_r3c5", "Hidden Figures", "Margot Lee Shetterly", "high", ""),
    ("block05_r3c6", "Subscribed: Why the Subscription Model Will Be Your Company's Future - and What to Do About It", "Tien Tzuo", "high", ""),
    ("block05_r4c1", "Fooled by Randomness: The Hidden Role of Chance in Life and in the Markets", "Nassim Nicholas Taleb", "high", ""),
    ("block05_r4c2", "Atomic Habits: An Easy & Proven Way to Build Good Habits & Break Bad Ones", "James Clear", "high", ""),
    ("block05_r4c3", "Benjamin Franklin: An American Life", "Walter Isaacson", "high", ""),
    ("block05_r4c4", "Titan: The Life of John D. Rockefeller, Sr.", "Ron Chernow", "high", ""),
    ("block05_r4c5", "What If?: Serious Scientific Answers to Absurd Hypothetical Questions", "Randall Munroe", "high", ""),
    ("block05_r4c6", "Thinking, Fast and Slow", "Daniel Kahneman", "high", ""),

    # ---- Block 6 ----
    ("block06_r1c1", "The Anxious Generation: How the Great Rewiring of Childhood Is Causing an Epidemic of Mental Illness", "Jonathan Haidt", "high", ""),
    ("block06_r1c2", "Meditations", "Marcus Aurelius", "high", "Penguin Classics"),
    ("block06_r1c3", "The Food Lab: Better Home Cooking Through Science", "J. Kenji Lopez-Alt", "high", ""),
    ("block06_r1c4", "Ayn Rand and the World She Made", "Anne C. Heller", "high", ""),
    ("block06_r1c5", "The Last Lecture", "Randy Pausch", "high", "with Jeffrey Zaslow"),
    ("block06_r1c6", "Churchill & Orwell: The Fight for Freedom", "Thomas E. Ricks", "high", ""),
    ("block06_r2c1", "Muppets in Moscow", "Natasha Lance Rogoff", "high", "cover subtitle about making Sesame Street in Russia is too small to read reliably; omitted"),
    ("block06_r2c2", "Good Energy: The Surprising Connection Between Metabolism and Limitless Health", "Casey Means", "high", "with Calley Means"),
    ("block06_r2c3", "Man's Search for Meaning", "Viktor E. Frankl", "high", ""),
    ("block06_r2c4", "A Man Called Ove", "Fredrik Backman", "high", ""),
    ("block06_r2c5", "Genius: The Life and Science of Richard Feynman", "James Gleick", "high", ""),
    ("block06_r2c6", "The Book Thief", "Markus Zusak", "medium", "title lettering is stylized and low-contrast; the author line on the cover is not legible at this resolution"),
    ("block06_r3c1", "The Snowball: Warren Buffett and the Business of Life", "Alice Schroeder", "high", ""),
    ("block06_r3c2", "I Am the Messenger", "Markus Zusak", "high", ""),
    ("block06_r3c3", "Moby-Dick, or, The Whale", "Herman Melville", "high", "Penguin Classics"),
    ("block06_r3c4", "A Necessary Lie", "Doohyun Kim", "high", "byline is not legible on the cover - author supplied by user (amazon.com/dp/B0CH3XJJ45); cover shows a co-author credit that remains illegible"),
    ("block06_r3c5", "The Invisible Life of Addie LaRue", "V. E. Schwab", "high", ""),
    ("block06_r3c6", "Making It So: A Memoir", "Patrick Stewart", "high", ""),
    ("block06_r4c1", "The Conquer Code", "Trevor Farnes", "high", "surname corrected by user to Farnes (I misread the small cover lettering as FARMES)"),
    ("block06_r4c2", "American Sherlock: Murder, Forensics, and the Birth of American CSI", "Kate Winkler Dawson", "medium", "subtitle read at low resolution"),
    ("block06_r4c3", "Creativity, Inc.: Overcoming the Unseen Forces That Stand in the Way of True Inspiration", "Ed Catmull", "high", "with Amy Wallace"),
    ("block06_r4c4", "We Are Legion (We Are Bob)", "Dennis E. Taylor", "high", ""),
    ("block06_r4c5", "The Bomber Mafia: A Dream, a Temptation, and the Longest Night of the Second World War", "Malcolm Gladwell", "high", ""),
    ("block06_r4c6", "Decider", "Dick Francis", "high", ""),

    # ---- Block 7 ----
    ("block07_r1c1", "The Splendid and the Vile: A Saga of Churchill, Family, and Defiance During the Blitz", "Erik Larson", "high", ""),
    ("block07_r1c2", "The Great Gatsby", "F. Scott Fitzgerald", "high", "The Author's Edition, 100th anniversary"),
    ("block07_r1c3", "A Gentleman in Moscow", "Amor Towles", "high", ""),
    ("block07_r1c4", "Talking to Strangers: What We Should Know About the People We Don't Know", "Malcolm Gladwell", "high", ""),
    ("block07_r1c5", "The Christmas Box", "Richard Paul Evans", "medium", "title and author set in small script on a decorative binding; read at low resolution"),
    ("block07_r1c6", "12 Rules for Life: An Antidote to Chaos", "Jordan B. Peterson", "high", "a sliver of the row above is clipped into the top of the source screenshot"),
    ("block07_r2c1", "The Dutch House: A Novel", "Ann Patchett", "high", ""),
    ("block07_r2c2", "Empire of Pain: The Secret History of the Sackler Dynasty", "Patrick Radden Keefe", "high", ""),
    ("block07_r2c3", "Outlive: The Science & Art of Longevity", "Peter Attia", "high", "with Bill Gifford"),
    ("block07_r2c4", "Team of Rivals: The Political Genius of Abraham Lincoln", "Doris Kearns Goodwin", "high", ""),
    ("block07_r2c5", "The Box: How the Shipping Container Made the World Smaller and the World Economy Bigger", "Marc Levinson", "high", "source grid held a placeholder cover with truncated title text; image replaced at user request with the real Princeton UP cover (ISBN 0691136408) from covers.openlibrary.org, 331x500 - NOT a crop from the source screenshots"),
    ("block07_r2c6", "Oliver Twist", "Charles Dickens", "high", "Penguin Classics"),
    ("block07_r3c1", "Last Seen Wearing", "Hillary Waugh", "high", "Pan Crime Classics"),
    ("block07_r3c2", "The Child Whisperer: The Ultimate Handbook for Raising Happy, Successful, Cooperative Children", "Carol Tuttle", "high", "subtitle read at low resolution"),
    ("block07_r3c3", "The Omnivore's Dilemma: A Natural History of Four Meals", "Michael Pollan", "high", ""),
    ("block07_r3c4", "The Emperors of Chocolate: Inside the Secret World of Hershey & Mars", "Joel Glenn Brenner", "medium", "title and author appear only in a small medallion on the cover"),
    ("block07_r3c5", "To Kill a Mockingbird", "Harper Lee", "high", ""),
    ("block07_r3c6", "Powers and Thrones: A New History of the Middle Ages", "Dan Jones", "high", ""),
    ("block07_r4c1", "Project Hail Mary", "Andy Weir", "high", ""),
    ("block07_r4c2", "Crime and Punishment", "Fyodor Dostoyevsky", "high", "Penguin Classics"),
    ("block07_r4c3", "The Smartest Guys in the Room: The Amazing Rise and Scandalous Fall of Enron", "Bethany McLean and Peter Elkind", "high", ""),
    ("block07_r4c4", "The Tech-Wise Family: Everyday Steps for Putting Technology in Its Proper Place", "Andy Crouch", "high", ""),
    ("block07_r4c5", "The Greater Journey: Americans in Paris", "David McCullough", "high", ""),
    ("block07_r4c6", "Sacred Symbols: Finding Meaning in Rites, Rituals, & Ordinances", "Alonzo L. Gaskill", "high", ""),

    # ---- Block 8 (partial) ----
    ("block08_r2c1", "Undaunted Courage: The Pioneering First Mission to Explore America's Wild Frontier", "Stephen E. Ambrose", "high", ""),
    ("block08_r2c2", "Endurance: Shackleton's Incredible Voyage", "Alfred Lansing", "high", ""),
    ("block08_r2c3", "Grit: The Power of Passion and Perseverance", "Angela Duckworth", "high", ""),
    ("block08_r2c4", "Originals: How Non-Conformists Move the World", "Adam Grant", "high", ""),
    ("block08_r2c5", "The Wright Brothers", "David McCullough", "high", ""),
]

OUT = os.path.join("covers", "manifest.csv")


def short_title(title_full):
    """Everything before the first colon; the whole title if there is none."""
    return title_full.split(":", 1)[0].strip() if ":" in title_full else title_full


def main():
    have = {f[:-4] for f in os.listdir("covers") if f.startswith("block") and f.endswith(".png")}
    listed = {stem for stem, *_ in DATA}
    missing = have - listed
    extra = listed - have
    if missing:
        print("WARNING: extracted but not in manifest:", sorted(missing))
    if extra:
        print("WARNING: in manifest but no such file:", sorted(extra))

    with open(OUT, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["filename", "title_full", "title_short", "author", "confidence", "notes"])
        for stem, title_full, author, conf, notes in DATA:
            w.writerow([stem + ".png", title_full, short_title(title_full), author, conf, notes])

    counts = {}
    for _, _, _, conf, _ in DATA:
        counts[conf] = counts.get(conf, 0) + 1
    print("Wrote %s with %d rows" % (OUT, len(DATA)))
    print("Confidence:", ", ".join("%s=%d" % (k, counts[k]) for k in ("high", "medium", "low") if k in counts))


if __name__ == "__main__":
    main()
