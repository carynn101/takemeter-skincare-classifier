import pandas as pd

CODES = [
    # 20-29
    "S","D","S","D","S","D","S","S","D","D",
    # 30-39
    "S","S","D","D","D","D","S","D","S","S",
    # 40-49
    "S","S","S","S","S","D","S","S","S","D",
    # 50-59
    "D","S","S","S","S","D","D","D","S","S",
    # 60-69
    "S","S","S","D","S","S","S","R","S","S",
    # 70-79
    "S","D","S","D","S","S","D","D","S","S",
    # 80-89
    "D","D","S","D","S","D","S","S","D","S",
    # 90-99
    "R","S","D","S","S","D","R","D","S","S",
    # 100-109
    "D","S","S","D","D","D","D","D","D","S",
    # 110-119
    "D","D","D","S","D","D","S","D","R","D",
    # 120-129
    "D","D","S","S","S","R","D","S","S","D",
    # 130-139
    "D","D","D","S","D","D","R","D","S","R",
    # 140-149
    "S","S","S","S","D","R","S","R","S","D",
    # 150-159
    "D","D","S","S","R","D","S","S","S","S",
    # 160-169
    "S","S","S","S","D","D","D","D","R","S",
    # 170-177
    "S","S","D","R","S","S","S","R",
]
MAP = {"S": "skin_help", "D": "discussion", "R": "routine_review"}

d = pd.read_csv("labels.csv", keep_default_na=False)
assert len(CODES) == len(d) - 40, f"expected {len(d) - 40}, got {len(CODES)}"
assert d.loc[20, "text"].startswith("Routine minimizes"), "row order changed"

for k, c in enumerate(CODES):
    i = 20 + k
    d.loc[i, "label"] = MAP[c]
    note = d.loc[i, "note"]
    if "pre-labeled" not in note:
        d.loc[i, "note"] = (note + "; pre-labeled") if note else "pre-labeled"

d.to_csv("labels.csv", index=False)
print(d["label"].value_counts())
print("\nShare:\n", (d["label"].value_counts(normalize=True) * 100).round(1))
print("\nBlank labels:", (d["label"] == "").sum())