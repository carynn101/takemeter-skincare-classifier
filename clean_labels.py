import re
import pandas as pd

d = pd.read_csv("labels.csv", keep_default_na=False)
before = len(d)

def fix(t):
    t = str(t).strip()
    t = re.sub(r"^[&\-–—\s]+", "", t)
    for _ in range(3):
        t = re.sub(r"^\s*\[[^\]]{1,30}\]\s*", "", t)
    t = re.sub(r"\s*\[[^\]]{1,30}\]\s*$", "", t)
    return " ".join(t.split())

d["text"] = d["text"].map(fix)

DROP_EXACT = {
    "medicube", "moisturiser", "tretinoin?", "why does this happen",
    "what do i do", "please help with this", "this thing is bothering me",
    "additional products", "is this safe to use?", "skin care question",
    "struggling so badly", "advice pls!",
}
DROP_CONTAINS = ["on breast", "buttocks", "12 year old", "of going absolutely insane"]

mask = d["text"].str.split().str.len() >= 1
mask &= ~d["text"].str.lower().isin(DROP_EXACT)
for s in DROP_CONTAINS:
    mask &= ~d["text"].str.contains(s, case=False, regex=False)
dropped = d[~mask]["text"].tolist()

d = d[mask].drop_duplicates(subset="text").reset_index(drop=True)
d.to_csv("labels.csv", index=False)

print(f"{before} rows -> {len(d)} rows")
print("\nDropped:")
for t in dropped:
    print("  -", t)
bad = d[d["text"].str.contains(r"\[[^\]]*\]", regex=True)]
print(f"\nRows still containing [brackets]: {len(bad)}")
print("\nFirst 20 titles (your cold set), flair hidden:")
for i, t in enumerate(d["text"].head(20), 1):
    print(f"{i:2d}. {t}")