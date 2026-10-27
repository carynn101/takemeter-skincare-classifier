# Acceptance Criteria

These targets were set before training, before I saw any results.

## 1. Overall accuracy
**Criterion:** Accuracy on `test_split.csv` is at least 0.65.
**Why:** My test split is about 30 rows, and always predicting `skin_help` (50% of my data) would score about 0.50. A target of 0.65 means roughly 20 of 30 correct, 5 more than the always-guess baseline, which is the least I would call useful.

## 2. Per-label F1 for the two larger labels
**Criterion:** F1 for `skin_help` and for `discussion`, each measured on `test_split.csv`, is at least 0.60.
**Why:** These labels have about 12-15 test rows each, so one or two mistakes move F1 noticeably. I chose 0.60 because my titles-only text is short and I hesitated on 6 of my 20 cold labels (30%), so I do not expect near-perfect scores.

## 3. Per-label F1 for the thin label
**Criterion:** F1 for `routine_review` on `test_split.csv` is at least 0.50.
**Why:** `routine_review` has only 20 labeled rows (10%), so the test split holds about 3 of them. With 3 rows, F1 moves in big steps, and 0.50 means catching at least 1 of 3 without false alarms. I set it lower than the other labels because the sample is tiny, not because I expect it to be unimportant.

## 4. Balance
**Criterion:** In `labels.csv`, no label makes up more than 60% of rows, and every label makes up at least 8%.
**Why:** My actual counts are 99 `skin_help` (50%), 79 `discussion` (40%), and 20 `routine_review` (10%). The brief caps any label at 70%, and I chose 60% to catch a drift before it reaches the cap. The 8% minimum is about 16 rows and protects my thinnest label from becoming too small to measure.

## 5. Labeling consistency
**Criterion:** When a second person labels the 20 rows marked `cold` in the `note` column of `labels.csv` using only `notes/label_taxonomy.md`, they agree with my labels on at least 13 of 20 (65%).
**Why:** I hesitated on 6 of those 20 rows (30%), mostly where a post mixes a personal concern with a general question. Because roughly a third of posts are borderline even for me, I expect some disagreement despite my tie-break rules, so 65% is realistic and still well above chance for my 50/40/10 label split.

**Note added after training:** The counts in criteria 3 and 4 were true when I wrote them. After I reviewed my pre-labeled rows I changed 3 labels, so the final counts in `labels.csv` are 100 `skin_help`, 76 `discussion`, and 22 `routine_review` (50.5% / 38.4% / 11.1%). I did not change any target or reason.

> **Revised in unit 6:** I agree with the staff labels on at least 20 of the 30 staff posts (65%).
>
> **Why revised:** The original needs a second person to label my 20 `cold` rows under my own taxonomy, and this unit gave me no such labeler, so I could not produce a verdict from it. The 65% threshold is unchanged. Only the instrument changed. I added this revision after the agreement run showed 20 of 30 (67%), so it was not set in advance. The original criterion is left above unchanged.

---

## Pick numbers you can defend

Not numbers that sound impressive. Three labels means a coin-flip guesser gets
about 33%, so a target of 0.40 is barely a target. Your number should sit
somewhere you'd honestly call useful.

**Cover at least three of these five areas.** They're here as prompts, not as a
form to fill in — a criterion that fits none of them is fine if it names a
number.

| Area | A question it could answer |
|---|---|
| Overall accuracy | How often does it need to be right to be worth using? |
| Per-label performance | Is one label allowed to be much worse than the others? |
| Balance | How lopsided can your label counts get before it's a problem? |
| Consistency | If someone else labelled the same posts, how often should you agree? |
| Confidence | Should a confident prediction be right more often than an unsure one? |

Two things worth knowing before you pick numbers, because both will affect
whether you hit them:

- **Your smallest label will have the jumpiest score.** If a label has 50
  examples, about 8 land in the test split. An F1 computed on 8 examples moves
  a lot between seeds. A target for that label should be looser than one for
  your biggest label, and saying so is a good reason.
- **Unit 6 tests across three seeds, and the target has to hold across all
  three.** A target of 0.65 against results of 0.71, 0.62, 0.68 is a **miss**.
  Pick with that in mind — it is stricter than it first sounds.

---
