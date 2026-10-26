# TakeMeter: Skincare Post Classifier

A fine-tuned text classifier that sorts r/SkincareAddiction post titles by what the poster is doing. This is the build unit of a two-unit project: here I design the labels, label the data, train a model, and write down what "working" means before seeing any results. The next unit tests the model against a baseline and a second labeler.

**Status:** trained, but the model has not learned much beyond the majority class (see [The Training Run](#the-training-run)). The data, the labeling decisions, and the pre-registered criteria are the main deliverables of this unit.

## What This Does

TakeMeter reads the title of a public r/SkincareAddiction post and predicts one of three labels:

- `skin_help`: the poster asks about their own skin concern
- `routine_review`: the poster centers their own products or routine
- `discussion`: a general question, opinion, or piece of information

I chose this community because its posts range from detailed help requests to general conversation, so there is real variation to learn.

## Label Taxonomy

| Label | Definition | Example 1 | Example 2 |
|---|---|---|---|
| `skin_help` | The poster centers their own skin concern or appearance, or asks what works for a skin problem, and wants advice or opinions. | "I need some product recommendations for my skin" | "It's been five years and I'm tired. Has anyone else had skin like this and been able to clear it?" |
| `routine_review` | The poster centers their own products or regimen, either asking for feedback on it or sharing it as something that works for them. | "Is my routine too much?" | "I've spent $10000 on skincare and this is my skincare routine" |
| `discussion` | The post starts a general conversation or shares information (trends, ingredients, marketing, news, community meta) rather than centering the poster's own skin or routine. | "Overrated vs underrated ingredients?" | "The first new sunscreen in 25 years is finally arriving in stores in the U.S." |

### Hardest boundary: `skin_help` vs. `routine_review`

Many posts name a skin problem and also mention products. The decision rule:

> Ask what the post is centered on. If the poster's own routine or products are the subject, label it `routine_review`, even if a skin concern is mentioned as context. If the poster's own skin concern or appearance is the subject and products are background or a request, label it `skin_help`.

My first version of this rule was built around "the main question," but a borderline post I found ("I think I've found a good routine for my decades-persistent acne!") asks no question, so I rewrote it around what the post is centered on.

### Tie-breaks

Applied in this order:

1. **Tie-break A (personal detail + general question):** if the question would still make sense without the poster's personal details, label it `discussion`.
2. The main rule above.
3. **Tie-break B (both appear):** label by the first ask in the title.

I added A and B after an eight-post boundary stress test (see [How I Used AI](#how-i-used-ai)).

### Dropped label

I considered a fourth label, `news`, and folded it into `discussion`. In about 40 posts I read, 5 were news or regulation posts (about 12%), which would give roughly 25 examples in 200 rows and about 4 in a 15% test split. That is too few to train on or measure reliably.

## The Dataset

**Source.** Public post titles from r/SkincareAddiction, collected in October 2026 from the Hot, New, and Top (day, week, month, year) views. Reddit's own listings required a login, so I read the same public posts through a public Reddit mirror. No account or private content was used.

**What a row is.** `labels.csv` has three columns: `text`, `label`, and `note`.

- `text` is the **post title only**. The pages I copied also showed post bodies, but I kept only the titles and saved no usernames or comments, which keeps personal details out of the data.
- Reddit's flair tags (such as "Routine Help") were stripped from `text`, because a model could use them as a shortcut instead of learning from the title. The flair is kept in `note` for reference.

**Cleaning.** About 214 collected titles became 198 rows. I removed duplicates, moderator threads, titles with no usable content (for example single-word product names), and a few rows that were too personal or about minors. I deliberately kept short but labelable titles such as "red spots" and "Double Cleansing." Removing every ambiguous row would have made the dataset artificially easy.

**Labeling process.**

- **20 rows labeled cold:** I labeled these myself, using only my written definitions and tie-breaks, with no tools and without looking at any suggested labels. They are marked `cold` in `note`.
- **178 rows pre-labeled with Claude:** I gave Claude my definitions and tie-breaks, it suggested labels, and I reviewed them. I changed 3 of them (marked `reviewed-changed` in `note`) and left the rest. Pre-labeled rows are marked `pre-labeled`. I reviewed about 20 of the 178, focusing on rows near my label boundaries.

**Count per label (198 rows):**

| Label | Rows | Share |
|---|---|---|
| `skin_help` | 100 | 50.5% |
| `discussion` | 76 | 38.4% |
| `routine_review` | 22 | 11.1% |

No label is above the 70% cap. `routine_review` is the thinnest label, which is itself a finding: in this community, few posts center on someone's own routine.

### Hard cases

1. **"my terrible blackheads that just won't go away no matter what i try"** (cold). Chose `skin_help` over `routine_review`. The blackheads are the subject; the products the poster tried are background.
2. **"Something for blackheads please"** (cold). Chose `routine_review` over `skin_help`. The poster asks for a product, but the underlying concern is a skin problem. This is the case where my rule is least clear.
3. **"I've been using adapalene for ~6 weeks and I'm suffering:("** (cold). Chose `routine_review` over `skin_help`. The poster centers a product they are using, but the suffering is a skin issue.
4. **"A brief overview of acne types & treatments"** (review). Pre-labeled `discussion`, then changed to `routine_review` because it is about specific treatments. This is the weakest of my changes: my definition centers the poster's own routine, and this reads more like general information, so it could reasonably be `discussion`.

### Limitations

- Only titles are labeled, so some are genuinely ambiguous without the body.
- I pulled posts from several Reddit views, so the sample may favor popular or recent posts.
- `routine_review` has only 22 rows, so the test split holds just 3 of them.
- 178 of 198 labels started as suggestions from an AI tool, so the labels may reflect that tool's reading of my definitions.

## The Training Run

- **Starting model:** `distilbert-base-uncased`, fine-tuned for 3-way text classification
- **Settings:** seed 42, 3 epochs, learning rate 2e-5, batch size 16, 128 tokens per post. I did not change any hyperparameter.
- **Split:** the notebook's 70/15/15 split gave 138 train, 30 validation, and 30 test rows.

| Label | Train | Val | Test |
|---|---|---|---|
| `skin_help` | 70 | 15 | 15 |
| `routine_review` | 16 | 3 | 3 |
| `discussion` | 52 | 12 | 12 |

- **Device:** Apple Silicon GPU (`mps`) on an arm64 Mac. The notebook kernel inside VS Code started under Intel emulation and could not load the arm64 packages, so I ran the notebook through JupyterLab from an arm64 terminal.

### Results

Final run, after reviewing my pre-labels (metrics in `results.json`):

| Metric | Value |
|---|---|
| Accuracy | 0.500 |
| Macro F1 | 0.222 |
| `skin_help` F1 (n=15) | 0.667 |
| `discussion` F1 (n=12) | 0.000 |
| `routine_review` F1 (n=3) | 0.000 |

These numbers match what a model predicting `skin_help` for every post would score, so the model most likely learned the majority class and little else. I have not diagnosed why; that is the next unit's work. Plausible contributors I will check: a small model trained for only 27 steps on 138 short titles, class imbalance, and ambiguous labels.

My first training run, before I corrected 3 labels, scored accuracy 0.567 and macro F1 0.328. It is preserved in the git history. The final run uses the final labels, so it is the one reported above.

### Results against my pre-registered criteria

I wrote `criteria.md` before training and did not edit it afterward.

| Criterion | Target | Result | Outcome |
|---|---|---|---|
| 1. Accuracy | ≥ 0.65 | 0.500 | Missed |
| 2. `skin_help` F1 | ≥ 0.60 | 0.667 | Met |
| 2. `discussion` F1 | ≥ 0.60 | 0.000 | Missed |
| 3. `routine_review` F1 | ≥ 0.50 | 0.000 | Missed |
| 4. Balance | No label above 60% or below 8% | 50.5% / 38.4% / 11.1% | Met |
| 5. Agreement with a second labeler | ≥ 13 of 20 | Not measured yet | Next unit |

## How I Used AI

1. **Stress-testing my labels.** I gave Claude my label definitions, and it wrote eight invented posts that sit on my boundaries. I labeled them cold and hesitated on three. Posts that mixed a personal detail with a general question exposed a gap in my first decision rule, so I added Tie-break A and Tie-break B.
2. **Pre-labeling.** Claude suggested labels for 178 of the 198 rows from my definitions. I reviewed them and changed 3. I labeled the other 20 rows myself with no tools and no suggestions.
3. **Other help.** Claude helped me write the scripts that collect and clean titles and write labels into the CSV, suggested the numeric targets in `criteria.md` (which I reviewed and edited before training), and helped me debug the notebook environment.

## Repository

| File | What it is |
|---|---|
| `criteria.md` | Five acceptance criteria with targets and reasons, written before training |
| `labels.csv` | 198 labeled titles (`text`, `label`, `note`) |
| `results.json` | Metrics, device, and settings from the final training run |
| `test_split.csv` | The held-out test rows, used by the next unit's baseline |
| `notes/` | Community notes and the label taxonomy as I wrote them |
| `takemeter.ipynb` | Training notebook |
| `extract_titles.py`, `make_csv.py`, `clean_labels.py` | Title collection and cleaning |
| `apply_prelabels.py`, `apply_middle.py`, `apply_cold.py`, `apply_review.py` | Scripts that write labels into `labels.csv` |

Raw collection files (copied page text and intermediate CSVs) are not committed.


<!-- ═══════════════════════ UNIT 6 — THE TEST ═══════════════════════

     Don't fill these in during unit 5.
     ═══════════════════════════════════════════════════════════════════ -->

---
## Stretch Features Declared
- **Confidence check:** I will report whether the model's confident predictions
  are right more often than its unsure ones, with the numbers behind it.

## Baseline vs. Trained

Both models were scored on the same 30 posts in `test_split.csv` (the seed-42 split). The baseline is `facebook/bart-large-mnli` run zero-shot on `mps`, using only the three definitions in `label_definitions.txt`.

| Measure | Baseline | Trained | Difference |
|---|---|---|---|
| Overall accuracy | 0.700 | 0.500 | -0.200 |
| Macro F1 | 0.690 | 0.222 | -0.468 |
| F1 — `discussion` | 0.500 | 0.000 | -0.500 |
| F1 — `routine_review` | 0.800 | 0.000 | -0.800 |
| F1 — `skin_help` | 0.769 | 0.667 | -0.103 |

**What I predicted before I looked:**
I had already seen my unit 5 trained numbers (accuracy 0.500; `discussion` and `routine_review` F1 of 0.000) before running the baseline, so this is not a blind prediction. Given those numbers, I expected the baseline to beat my model on every label, with `skin_help` the closest, since my model predicted that class for everything.

**What the gap actually means:**
The baseline beat my trained model on all five measures, so fine-tuning on 138 titles added nothing over a zero-shot model reading my definitions. The gap is largest on `routine_review` (0.800 vs. 0.000), my thinnest label, where the trained model had only 16 training rows. Caveat: `routine_review` has just 3 test posts, so the baseline's 0.800 could move a lot on a different split, and this comparison covers seed 42 only.


---

## Run Log — Before
**Device:** `mps` (Apple Silicon GPU). Settings: 3 epochs, learning rate 2e-5, batch size 16, `distilbert-base-uncased`.

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1. Overall accuracy | ≥ 0.65 | 0.500 | 0.500 | 0.700 | MISSED |
| 2. F1 `skin_help` / `discussion` | each ≥ 0.60 | 0.667 / 0.000 | 0.667 / 0.000 | 0.788 / 0.667 | MISSED |
| 3. F1 `routine_review` | ≥ 0.50 | 0.000 | 0.000 | 0.000 | MISSED |
| 4. Balance in `labels.csv` | ≤ 60% and ≥ 8% | 50.5 / 38.4 / 11.1% | same | same | MET |
| 5. Labeling consistency | ≥ 13 of 20 | pending | n/a | n/a | pending |

Accuracy ranged from 0.500 to 0.700 across seeds, a 20-point spread, and discussion F1 ranged from 0.000 to 0.667. Because each test split holds only 30 rows, one or two posts move these scores a lot. This is too noisy for a stable measure.


### Confusion matrix (seed 42, device: `mps`)

| true \ predicted | skin_help | routine_review | discussion |
|---|---|---|---|
| **skin_help** | 15 | 0 | 0 |
| **routine_review** | 3 | 0 | 0 |
| **discussion** | 12 | 0 | 0 |

**My biggest off-diagonal number, and what it means:**
12 real `discussion` posts were called `skin_help`, and 0 went the other way. Every `routine_review` post (3 of 3) was also called `skin_help`. This is not a single confused boundary. The model predicted `skin_help` for all 30 posts and never produced another label, so it did not learn any boundary on this seed.



---

## Verdicts and Diagnoses

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Overall accuracy | ≥ 0.65 | MISSED | Seeds 42 and 7 scored 0.500. The target must hold on all three seeds, so seed 2024's 0.700 doesn't rescue it. |
| 2 | F1 `skin_help` / `discussion` | each ≥ 0.60 | MISSED | `skin_help` passed on all seeds, but `discussion` F1 was 0.000 on seeds 42 and 7. |
| 3 | F1 `routine_review` | ≥ 0.50 | MISSED | F1 was 0.000 on all three seeds. |
| 4 | Balance in `labels.csv` | ≤ 60% and ≥ 8% | MET | 50.5% / 38.4% / 11.1%. This measures the data, so it is the same on every seed. |
| 5 | Labeling consistency | ≥ 13 of 20 | pending | Needs the agreement step. See below. |

**Diagnoses**

**Criteria 1, 2 and 3: MISSED. Cause: the model collapsed to the majority class (undertraining).**
Evidence: on seed 42 all 30 test posts were predicted `skin_help` (confusion matrix above),
and seed 7 gave identical scores (accuracy 0.500, `skin_help` F1 0.667, all other F1 0.000).
Training loss only fell from about 1.05 to 0.97 over 27 steps, and validation accuracy sat at
0.500 for all three epochs on both seeds. Seed 2024 reached `discussion` F1 0.667, so the
label is learnable, but `routine_review` stayed at 0.000 on every seed (16 training rows).
The baseline also reached `routine_review` F1 0.800 from definitions alone, which suggests
the labels are usable and the trained model simply did not learn them.



---

## Agreement Report

<!-- Your rate against the staff set, and every disagreement adjudicated.

     Remember you labelled these 30 under the STAFF taxonomy in
     data/staff_taxonomy.md, not your own — so every argument below is made
     from those definitions and those decision rules. -->

**Agreement rate:** ___ / 30 = ___%

<!-- Nobody grades this number. A 60% who argues every disagreement from the
     stated rules beats a 95% who wrote "staff was right" nine times. Several
     of the 30 were chosen because they're genuinely ambiguous — you should be
     winning some of these. -->

**Disagreements**

<!-- Three lines each: the post, both labels, and who you think is right and
     why — grounded in the staff definitions you were both applying.

     Then sort each into one of three piles:
       (a) the rule covered it and I applied it loosely → a consistency problem
       (b) the rule genuinely doesn't say               → a gap in the definitions
       (c) the rule is ambiguous here and my reading is defensible → argue it.
           This is a legitimate win.

     Pile (a) is the one that matters most for your diagnosis: if you applied a
     written rule two different ways on 30 posts, that is direct evidence about
     what you did across your own 200. -->

**1.**
> *The post:*
>
> *Staff said / I said:*
>
> *My call, and why:*
>
> *Which pile:*

**2.**
> *The post:*
>
> *Staff said / I said:*
>
> *My call, and why:*
>
> *Which pile:*

**What the pattern in my disagreements tells me:**



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Run Log — After

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it didn't, say so. Relabelling that didn't help is a genuinely
     interesting result and earns full credit. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped. -->



**The gap between what I meant my labels to capture and what the model
learned:**
<!-- Two sentences. Your confusion matrix is the evidence. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 5

       [ ] criteria.md has five numbered criteria, each naming a NUMBER
       [ ] Each has a reason underneath tied to your data or taxonomy
       [ ] labels.csv: at least 150 rows, text/label/note, ONE file not split
       [ ] No label above 70%
       [ ] All five unit 5 sections have real content
       [ ] Label Taxonomy includes the decision rule for your hardest boundary
       [ ] The Dataset includes three hard cases
       [ ] results.json and test_split.csv committed (the notebook does this)
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 6

       [ ] Baseline vs. Trained table, with your prediction written beforehand
       [ ] Run Log — Before, five criteria across three seeds
       [ ] Confusion matrix TYPED AS A MARKDOWN TABLE
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, using the agreement report as evidence
       [ ] Agreement Report with every disagreement adjudicated
       [ ] One improvement, with Run Log — After
       [ ] What's Still Broken
       [ ] results_three_seeds_before.json, results_three_seeds_after.json,
           baseline_results.json and
           agreement_results.json committed
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
