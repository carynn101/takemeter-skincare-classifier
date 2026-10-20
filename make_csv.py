import csv, random, re

FLAIR = re.compile(r"^\s*\[([^\]]{1,30})\]\s*")
seen, rows = set(), []
for line in open("titles.txt", encoding="utf-8"):
    t = " ".join(line.split())
    flair = ""
    while True:
        m = FLAIR.match(t)
        if not m:
            break
        flair = flair or m.group(1)
        t = t[m.end():]
    if len(t) < 8 or t.lower() in seen:
        continue
    seen.add(t.lower())
    rows.append({"text": t, "label": "", "note": f"flair:{flair}" if flair else ""})

random.seed(42)
random.shuffle(rows)
with open("raw_posts.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["text", "label", "note"])
    w.writeheader()
    w.writerows(rows)
print(len(rows), "titles written to raw_posts.csv")