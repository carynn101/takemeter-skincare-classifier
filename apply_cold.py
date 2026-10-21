import pandas as pd

COLD = [
    "discussion",  # 1  What is wrong with my nose?
    "skin_help",  # 2  need help figuring how to treat dry patches on face
    "discussion",  # 3  Light lasers or retinal?
    "skin_help",  # 4  my terrible blackheads that just won't go away no matter what i try
    "routine_review",  # 5  Is exfoliation necessary?
    "discussion",  # 6  I vaguely knew heavy sunscreen use could affect vitamin D...
    "skin_help",  # 7  can't seem to get rid of clogged pores
    "discussion",  # 8  Is there any truth to "drinking retinol" by consuming carrot juice...
    "routine_review",  # 9  Something for blackheads please
    "discussion",  # 10 You can now only use one skincare product that's not cleanser...
    "discussion",  # 11 Does anyone have eyes like mine?
    "routine_review",  # 12 Has anyone tried this Sephora waterproof eye makeup remover?
    "skin_help",  # 13 Good sunscreen for sensitive skin?
    "skin_help",  # 14 red and irritated :(
    "skin_help",  # 15 This moisturiser burnt my skin
    "skin_help",  # 16 Lost with what to do to combat skin redness/ inflammation...
    "routine_review",  # 17 Wondering if this is a good / safe routine
    "discussion",  # 18 My face is dead
    "routine_review",  # 19 I've been using adapalene for ~6 weeks and I'm suffering:(
    "skin_help",  # 20 I'm 18 and I'm starting to see forehead wrinkles
]

VALID = {"skin_help", "routine_review", "discussion"}
assert len(COLD) == 20 and all(c in VALID for c in COLD), "fill all 20, check spelling"

d = pd.read_csv("labels.csv", keep_default_na=False)
start = len(d) - 20
for k, lab in enumerate(COLD):
    i = start + k
    d.loc[i, "label"] = lab
    note = d.loc[i, "note"]
    if "cold" not in note:
        d.loc[i, "note"] = (note + "; cold") if note else "cold"
d.to_csv("labels.csv", index=False)
print(d.tail(20)[["text", "label", "note"]].to_string())