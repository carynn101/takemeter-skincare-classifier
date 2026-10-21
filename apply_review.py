import pandas as pd

CHANGES = {
    149: ("How are you actually supposed to treat pimples", "skin_help"),
    150: ("tretinoin or retinol?", "routine_review"),
    167: ("A brief overview of acne types", "routine_review"),
}

VALID = {"skin_help", "routine_review", "discussion"}
d = pd.read_csv("labels.csv", keep_default_na=False)

for i, (start, lab) in CHANGES.items():
    assert lab in VALID
    assert i < 178, "rows 178+ are your cold labels"
    assert d.loc[i, "text"].startswith(start), f"row {i} is not '{start}'"

for i, (start, lab) in CHANGES.items():
    d.loc[i, "label"] = lab
    if "reviewed-changed" not in d.loc[i, "note"]:
        d.loc[i, "note"] += "; reviewed-changed"

d.to_csv("labels.csv", index=False)
print(len(CHANGES), "labels changed")
print(d["label"].value_counts())