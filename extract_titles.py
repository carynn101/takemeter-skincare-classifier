import re

HEADER = re.compile(r"^r/\w+\s*•\s*u/(\S+)\s*•\s*.+ago\s*$", re.I)
TRAILING_TAG = re.compile(r"\s*\[[^\]]{1,30}\]\s*$")
FLAIRS = sorted([
    "Routine Help", "Product Request", "Product Question", "Acne", "Anti-Aging",
    "Anti Aging", "Miscellaneous", "Sun Care", "Skin Concerns", "Treatments",
    "Discussion", "Review", "Research", "Rant", "News", "Ingredients",
    "Selfie/B&A", "PSA", "Cringe", "Personal", "Hair Removal", "Trigger Warning",
], key=len, reverse=True)
SKIP_WORDS = ("daily help thread", "[ama]", "megathread", "weekly")

lines = [l.strip() for l in open("raw_paste.txt", encoding="utf-8")]
out, seen = [], set()
for i, line in enumerate(lines):
    m = HEADER.match(line)
    if not m or m.group(1).lower() == "automoderator":
        continue
    j = i + 1
    while j < len(lines) and not lines[j]:
        j += 1
    if j >= len(lines):
        continue
    t = lines[j]
    for tail in (" Spoiler", " NSFW"):
        if t.endswith(tail):
            t = t[: -len(tail)]
    if t.startswith("Trigger Warning"):
        continue
    for f in FLAIRS:
        if t.startswith(f + " "):
            rest = t[len(f) + 1:].strip()
            t = rest if rest.startswith("[") else f"[{f}] {rest}"
            break
    t = TRAILING_TAG.sub("", t).strip()
    if any(w in t.lower() for w in SKIP_WORDS) or len(re.sub(r"\[[^\]]*\]", "", t).strip()) < 8:
        continue
    if t.lower() in seen:
        continue
    seen.add(t.lower())
    out.append(t)

open("titles_extracted.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
print(len(out), "titles written to titles_extracted.txt")
print("\n".join(out[:20]))