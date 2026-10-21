import pandas as pd

PRE = [
    "discussion",      # 1  Salicylic Acid Serum (title only, no concern named)
    "skin_help",       # 2  crepey skin
    "discussion",      # 3  DEBUNKING MYTHS
    "skin_help",       # 4  Face reddening and burning
    "routine_review",  # 5  Basic skincare help (could be skin_help)
    "skin_help",       # 6  Is this shininess over-exfoliation?
    "discussion",      # 7  best alternative for retinoids (Tie-break A)
    "discussion",      # 8  firming products that work (Tie-break A)
    "discussion",      # 9  good products that aren't viral
    "skin_help",       # 10 concerning pimple cluster
    "skin_help",       # 11 my dad's blemishes (someone else's skin)
    "routine_review",  # 12 How should I form my routine? (Tie-break B)
    "discussion",      # 13 affordable routines opinion
    "skin_help",       # 14 lip balm safe for acne-prone skin (could be discussion)
    "skin_help",       # 15 dehydrated acne prone skin
    "discussion",      # 16 sunscreen reviews (could be routine_review)
    "skin_help",       # 17 Amoxicillin cleared my acne (could be discussion)
    "skin_help",       # 18 dark inner thighs
    "discussion",      # 19 Heavenly product! (could be routine_review)
    "discussion",      # 20 spray bottle vs tap water (Tie-break A)
]

VALID = {"skin_help", "routine_review", "discussion"}
assert len(PRE) == 20 and all(p in VALID for p in PRE)

d = pd.read_csv("labels.csv", keep_default_na=False)
for i, lab in enumerate(PRE):
    d.loc[i, "label"] = lab
    note = d.loc[i, "note"]
    if "pre-labeled" not in note:
        d.loc[i, "note"] = (note + "; pre-labeled") if note else "pre-labeled"
d.to_csv("labels.csv", index=False)
print(d.head(20)[["text", "label", "note"]].to_string())