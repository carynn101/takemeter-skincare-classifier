# TakeMeter: Skincare Post Classifier

A fine-tuned text classifier that sorts r/SkincareAddiction post titles by what the poster is doing. This is the build unit of a two-unit project: here I design the labels, label the data, train a model, and write down what "working" means before seeing any results. Unit 6 tests it against a zero-shot baseline and a staff labeling set.

**Status:** Trained and tested. After a 3 to 10 epoch change, accuracy is 0.73 to 0.80 across three seeds, but routine_review is never predicted (see The Improvement).

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
- **Settings:** seed 42, 3 epochs, learning rate 2e-5, batch size 16, 128 tokens per post. I did not change any hyperparameter. (unit 5 run; unit 6 changes epochs, see The Improvement).
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

I wrote `criteria.md` before training and did not edit it afterward. Except the unit 6 revision to criterion 5, kept below the original.

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
4. Unit 6. I labeled the 30 staff posts myself, then got staff_labels.csv from the course Slack channel and ran agreement.py. Claude helped me understand the staff decision rules, drafted the adjudication entries, run logs and write-ups from my real outputs, and suggested the epochs change. I reviewed and edited them. My instructor approved using Claude for this.

## Repository

| File | What it is |
|---|---|
| `criteria.md` | Five acceptance criteria written before training, plus the unit 6 revision to criterion 5 |
| `labels.csv` | 198 labeled titles (`text`, `label`, `note`) |
| `results.json` | Metrics, device, and settings from the unit 5 training run |
| `test_split.csv` | Held-out test rows (seed 42), used by the baseline |
| `notes/` | Community notes and the label taxonomy as I wrote them |
| `takemeter.ipynb` | Training notebook (committed in the after configuration, `EPOCHS = 10`) |
| `label_definitions.txt` | The three label definitions the zero-shot baseline reads |
| `baseline.py`, `baseline_results.json` | Zero-shot baseline script and its results |
| `results_three_seeds_before.json` | Three-seed run at 3 epochs |
| `results_three_seeds_after.json` | Three-seed run at 10 epochs |
| `my_staff_labels.csv` | My labels for the 30 staff posts, under the staff taxonomy |
| `data/staff_labels.csv`, `data/staff_taxonomy.md`, `data/staff_posts.csv` | Staff reference labels, taxonomy and posts |
| `agreement.py`, `agreement_results.json` | Agreement script and my results against the staff set |
| `extract_titles.py`, `make_csv.py`, `clean_labels.py` | Title collection and cleaning |
| `apply_prelabels.py`, `apply_middle.py`, `apply_cold.py`, `apply_review.py` | Scripts that write labels into `labels.csv` |

Raw collection files (copied page text and intermediate CSVs) are not committed.


---
## Stretch Features Declared
- **Confidence check:** I will report whether the model's confident predictions
  are right more often than its unsure ones, with the numbers behind it.

## Baseline vs. Trained

Both models were scored on the same 30 posts in `test_split.csv` (the seed-42 split); the "after" column is the same split after the epochs change described in [The Improvement](#the-improvement). The baseline is `facebook/bart-large-mnli` run zero-shot on `mps`, using only the three definitions in `label_definitions.txt`.

| Measure (seed 42) | Baseline | Trained before (3 epochs) | Trained after (10 epochs) |
|---|---|---|---|
| Overall accuracy | 0.700 | 0.500 | 0.800 |
| Macro F1 | 0.690 | 0.222 | 0.558 |
| F1 — `discussion` | 0.500 | 0.000 | 0.800 |
| F1 — `routine_review` | 0.800 | 0.000 | 0.000 |
| F1 — `skin_help` | 0.769 | 0.667 | 0.875 |

**What I predicted before I looked:**
I had already seen my unit 5 trained numbers (accuracy 0.500; `discussion` and `routine_review` F1 of 0.000) before running the baseline, so this is not a blind prediction. Given those numbers, I expected the baseline to beat my model on every label, with `skin_help` the closest, since my model predicted that class for everything.

**What the gap actually means:**
Before the change, the baseline beat my trained model on all five measures, so fine-tuning on 138 titles at 3 epochs added nothing over a zero-shot model reading my definitions. After raising epochs to 10, the trained model beats the baseline on accuracy (0.800 vs. 0.700), `skin_help` F1 (0.875 vs. 0.769) and `discussion` F1 (0.800 vs. 0.500), and loses on `routine_review` F1 (0.000 vs. 0.800) and therefore on macro F1 (0.558 vs. 0.690). The gap is largest on `routine_review`, my thinnest label, where the trained model had only 16 training rows. Caveat: `routine_review` has just 3 test posts, so the baseline's 0.800 could move a lot on a different split, and this comparison covers seed 42 only.


---

## Run Log — Before
**Device:** `mps` (Apple Silicon GPU). Settings: 3 epochs, learning rate 2e-5, batch size 16, `distilbert-base-uncased`.

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1. Overall accuracy | ≥ 0.65 | 0.500 | 0.500 | 0.700 | MISSED |
| 2. F1 `skin_help` / `discussion` | each ≥ 0.60 | 0.667 / 0.000 | 0.667 / 0.000 | 0.788 / 0.667 | MISSED |
| 3. F1 `routine_review` | ≥ 0.50 | 0.000 | 0.000 | 0.000 | MISSED |
| 4. Balance in `labels.csv` | ≤ 60% and ≥ 8% | 50.5 / 38.4 / 11.1% | same | same | MET |
| 5. Labeling consistency | ≥ 13 of 20 | 20 / 30 (staff set) | n/a | n/a | MET |

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

### Verdicts (before the change)

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Overall accuracy | ≥ 0.65 | MISSED | Seeds 42 and 7 scored 0.500. The target must hold on all three seeds, so seed 2024's 0.700 doesn't rescue it. |
| 2 | F1 `skin_help` / `discussion` | each ≥ 0.60 | MISSED | `skin_help` passed on all seeds, but `discussion` F1 was 0.000 on seeds 42 and 7. |
| 3 | F1 `routine_review` | ≥ 0.50 | MISSED | F1 was 0.000 on all three seeds. |
| 4 | Balance in `labels.csv` | ≤ 60% and ≥ 8% | MET | 50.5% / 38.4% / 11.1%. This measures the data, so it is the same on every seed. |
| 5 | Labeling consistency | ≥ 13 of 20 (revised: ≥ 20 of 30 staff posts) | MET | 20 of 30 = 67% against the staff set. The original instrument (a second labeler on my 20 `cold` rows) was never available, so I used the revision recorded in `criteria.md`. |

These verdicts are from the three-seed run at 3 epochs. After the epochs change, criteria 1 and 2 flipped to MET, criterion 3 stayed MISSED, and criteria 4 and 5 stayed MET. The post-change verdicts are in the [Run Log — After](#run-log--after) table under The Improvement.

**Diagnoses**

**Criteria 1, 2 and 3: MISSED. Cause: the model collapsed to the majority class (undertraining).**
Evidence: on seed 42 all 30 test posts were predicted `skin_help` (confusion matrix above),
and seed 7 gave identical scores (accuracy 0.500, `skin_help` F1 0.667, all other F1 0.000).
Training loss only fell from about 1.05 to 0.97 over 27 steps, and validation accuracy sat at
0.500 for all three epochs on both seeds. Seed 2024 reached `discussion` F1 0.667, so the
label is learnable, but `routine_review` stayed at 0.000 on every seed (16 training rows).
The baseline also reached `routine_review` F1 0.800 from definitions alone, which suggests
the labels are usable and the trained model simply did not learn them.
My agreement report (20/30; 8 of 10 disagreements were rules I applied loosely) shows I can apply written boundaries inconsistently, but it was scored under the staff taxonomy, so it can’t explain this collapse. The collapse is explained by the flat training loss.

**Criterion 3 (`routine_review` F1): MISSED. Cause: too few examples, with a possible boundary problem.**
Evidence: `routine_review` F1 was 0.000 on all three seeds before the change and still 0.000 after training ten epochs, while `skin_help` and `discussion` rose above 0.70. It had 16 of 138 training rows (about 12%) and 3 test rows. After the change the matrix shows it was never predicted on any seed, and 8 of its 9 test posts across the three seeds were called `discussion` (the other went to `skin_help`). That points at the `routine_review` / `discussion` edge, not just the `skin_help` edge I expected. One suspect is my relabeled "A brief overview of acne types & treatments" row, which reads like `discussion`, though I haven't tested that. The agreement report can't confirm a labeling problem for this label, because it was scored under the staff taxonomy. It shows I applied a written rule loosely in 8 of 10 disagreements, so inconsistency is possible but unproven. The baseline reached `routine_review` F1 0.800 on the same 3 test posts, so the label is usable from definitions alone.


---

## Agreement Report

I labeled the 30 staff posts under `data/staff_taxonomy.md` before opening the staff key, and committed `my_staff_labels.csv` before running `agreement.py`.

**Agreement rate:** 20 / 30 = 67%

Ten posts disagreed. Six were posts where staff said `analysis` and I called `reaction` or `hot_take` (3, 5, 6, 7, 8, 10). Four were posts where staff said `hot_take` and I said `reaction` (13, 14, 18, 20). (numbers below are my disagreement list, 1 to 10; the numbers above are post positions in staff_posts.csv).

| # | Post (short) | Staff | Me | Pile |
|---|---|---|---|---|
| 1 | Club championship scoring change, 2019 | `analysis` | `reaction` | (a) |
| 2 | Carbon plates, 2% + 2% | `analysis` | `reaction` | (b) |
| 3 | 41% first-timers vs. 26% | `analysis` | `hot_take` | (a) |
| 4 | Same loop in 4C and 24C | `analysis` | `reaction` | (b) |
| 5 | Entry no-starts since 2012 | `analysis` | `hot_take` | (a) |
| 6 | Three runners, different shoes | `analysis` | `hot_take` | (a) |
| 7 | Tuesday session for everyone | `hot_take` | `reaction` | (a) |
| 8 | Times down 3% since shoe rules | `hot_take` | `reaction` | (a) |
| 9 | Track sessions wasted under 8-min miles | `hot_take` | `reaction` | (a) |
| 10 | Every injury thread is the same | `hot_take` | `reaction` | (a) |

**Disagreements**

**1. Club championship scoring change**
> *The post:* "The club championship scoring changed in 2019 from top-6 to top-10. Since then our B team has finished above the A team twice. That's not depth improving, it's the scoring rewarding turnout."
>
> *Staff said `analysis` / I said `reaction`.*
>
> *My call, and why:* Staff is right. I hesitated between `analysis` and `reaction` (rule 3). The post contains a date, a rule change and a count of results, and the conclusion rests on them. Delete them and no argument is left. Rule 3 says recency does not outrank evidence, and the dismissive last sentence sits on top of an argument. I let the tone decide.
>
> *Which pile:* (a)

**2. Carbon plates**
> *The post:* "Carbon plates aren't the whole story. My times dropped 2% in the shoes and another 2% the following year in the same pair, when the only thing that changed was going from 35 to 50 miles a week."
>
> *Staff said `analysis` / I said `reaction`.*
>
> *My call, and why:* Staff is right on the label, though the taxonomy has a gap. It lists "a stat, a date, a time, a quote, a named comparison" as checkable facts, but doesn't say whether the writer's own training data counts. I read it as personal experience. The post compares two years of times and mileage, and the comparison carries the argument against "carbon plates are the whole story." It spans a year, so it is not "in the last few hours" as rule 2 describes `reaction`. I also labeled staff post 2 `analysis`, which is also self-measured, so my reading was inconsistent.
>
> *Which pile:* (b)

**3. First-timers in the entry lists**
> *The post:* "Checked the entry lists. 41% of this year's field have never run the distance before, against 26% five years ago. That's why the finish-line photos look different, not because standards dropped."
>
> *Staff said `analysis` / I said `hot_take`.*
>
> *My call, and why:* Staff is right. Rule 1 asks whether the fact carries the argument. The 41%-versus-26% comparison is the reason given for the conclusion, so deleting it leaves nothing. I took the confident last sentence as an unsupported claim, but support is offered in the sentences before it.
>
> *Which pile:* (a)

**4. Same loop in 4C and 24C**
> *The post:* "Ran the same loop in 4C and in 24C within a fortnight, same effort by heart rate. 90 seconds slower in the heat over six miles. People keep saying heat costs you 'abit' and it's more than that."
>
> *Staff said `analysis` / I said `reaction`.*
>
> *My call, and why:* Staff is right. The post is a controlled comparison (same loop, same effort, 90 seconds over six miles) used to argue against a common claim. It was run over a fortnight, so it isn't a reaction to something that just happened. Disagreement 2, the taxonomy doesn't say whether self-collected measurements count as checkable, but the comparison does the work in the argument.
>
> *Which pile:* (b)

**5. No-starts since 2012**
> *The post:* "Went back through the club results going back to 2012. Every single year the number of people who enter the spring marathon and don't start it sits between 18 and 23 percent. It's not a bad-luck year, it's the base rate."
>
> *Staff said `analysis` / I said `hot_take`.*
>
> *My call, and why:* Staff is right. The 18 to 23 percent range across every year since 2012 is the evidence for "it's the base rate." I read "it's the base rate" as a restatement of the data, but the sentence before it shows the data is what supports it.
>
> *Which pile:* (a)

**6. Three runners, different shoes**
> *The post:* "Three of us ran the same session on the same day, different shoes, within 10 seconds of each other over 5 miles. I'm not saying shoes do nothing, but whatever they do was smaller than the noise between three people."
>
> *Staff said `analysis` / I said `hot_take`.*
>
> *My call, and why:* Staff is right. The hedge made it read like opinion to me, but the 10-second spread over 5 miles is the reason for "smaller than the noise between three people." Rule 1's delete test leaves no conclusion without it.
>
> *Which pile:* (a)

**7. Tuesday session**
> *The post:* "The club needs to stop pretending the Tuesday session is for everyone. It isn't and it never has been."
>
> *Staff said `hot_take` / I said `reaction`.*
>
> *My call, and why:* Staff is right. Rule 2 separates a post about the writer's experience from a general claim about the world, and this one makes a claim about the club with no event and no account of how the writer felt. Rule 2 says a post can be heated and still be `hot_take`. I weighed the frustrated tone and didn't apply the rule.
>
> *Which pile:* (a)

**8. Times down 3%**
> *The post:* "Times are down about 3% since the shoe rules changed, so obviously the shoes are the whole story and the sport has a problem."
>
> *Staff said `hot_take` / I said `reaction`.*
>
> *My call, and why:* Staff is right. I weighed `reaction` because the second half sounded like feeling. But "the sport has a problem" is a claim about the world, and the 3% is a flourish on a conclusion already reached ("obviously"). It matches rule 1's own `hot_take` example almost exactly.
>
> *Which pile:* (a)

**9. Track sessions**
> *The post:* "Track sessions are wasted on anyone running slower than 8 minute miles. You'd get more out of just running more."
>
> *Staff said `hot_take` / I said `reaction`.*
>
> *My call, and why:* Staff is right. I hesitated between `hot_take` and `reaction` (rule 2) and went with `reaction` because re-reading it felt like a response to something. The post doesn't say what it is responding to, and nothing in it describes the writer's own experience. The 8-minute-mile figure is a cutoff, not a fact supporting the claim, so rule 1 doesn't make it `analysis` either.
>
> *Which pile:* (a)

**10. Injury threads**
> *The post:* "Every injury thread on this forum is the same injury and the same three replies."
>
> *Staff said `hot_take` / I said `reaction`.*
>
> *My call, and why:* Staff is right. The weary tone is the case for `reaction`, but the post describes the forum in general and not a recent event happening to the writer. Rule 2 puts a general assertion about the world under `hot_take`.
>
> *Which pile:* (a)

**What the pattern in my disagreements tells me:**
Eight of ten disagreements are pile (a): the rule covered the case and I applied it loosely. The two pile (b) cases (carbon plates, same loop at 4C and 24C) share a real gap, because the taxonomy never says whether self-collected measurements count as a checkable fact. In the six `analysis` misses, a conclusion sentence with attitude followed the data, and I let that tone decide the label. In the four `hot_take` misses, I let a heated or tired tone stand in for rule 2's test of whether the post is about the writer's experience. I labeled posts 1, 2, 4 and 9 of the staff set `analysis`, and those have the same structure as the six I missed, so I applied one rule two ways. This suggests I may apply written rules inconsistently, but it can’t tell me whether my own skin_help and routine_review labels were inconsistent, because the staff taxonomy uses different labels.


---

## The Improvement

**What I changed:** Epochs from 3 to 10. Learning rate (2e-5), batch size (16), labels, taxonomy and criteria are unchanged.

**Which diagnosis pointed at it:** Seeds 42 and 7 collapsed to predicting `skin_help` for every post. Training loss only fell from about 1.05 to 0.97 over 27 steps, and validation accuracy stayed at 0.500 for all three epochs. That points to undertraining, not mislabeling.

### Confidence check

Yes, on all three seeds the model's most confident predictions were right more often than its least confident ones (10 posts per third).

| Seed | Accuracy, most confident third | Accuracy, least confident third | Mean confidence when right | Mean confidence when wrong |
|---|---|---|---|---|
| 42 | 1.0 | 0.5 | 0.776 | 0.581 |
| 7 | 1.0 | 0.6 | 0.687 | 0.563 |
| 2024 | 0.9 | 0.6 | 0.785 | 0.690 |

Before the change, the collapsed seed-42 model scored 0.9 vs. 0.0 on the two thirds, but its mean confidence was nearly flat (0.502 when right, 0.457 when wrong), so that gap came from a model leaning on one label. After training, the gap is smaller but the confidence itself separates right from wrong. Caveat: each third is 10 posts, so one post moves a third by 10 points.

### Run Log — After

Device: `mps`. Only change: epochs 3 → 10. Same seeds, labels, taxonomy and criteria. The committed notebook holds the after configuration (`EPOCHS = 10`); the before run used `EPOCHS = 3`.

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1. Overall accuracy | ≥ 0.65 | 0.800 | 0.733 | 0.767 | MET |
| 2. F1 `skin_help` / `discussion` | each ≥ 0.60 | 0.875 / 0.800 | 0.828 / 0.714 | 0.857 / 0.759 | MET |
| 3. F1 `routine_review` | ≥ 0.50 | 0.000 | 0.000 | 0.000 | MISSED |
| 4. Balance in `labels.csv` | ≤ 60% and ≥ 8% | 50.5 / 38.4 / 11.1% | same | same | MET |
| 5. Labeling consistency | ≥ 13 of 20 (revised: ≥ 20 of 30 staff posts) | 20 / 30 | n/a | n/a | MET |

Confusion matrix after the change (seed 42):

| true \ predicted | skin_help | routine_review | discussion |
|---|---|---|---|
| **skin_help** | 14 | 0 | 1 |
| **routine_review** | 1 | 0 | 2 |
| **discussion** | 2 | 0 | 10 |

**Did it help, and how do I know:**
Yes, on accuracy and on two of three labels. Accuracy went from 0.500 / 0.500 / 0.700 to 0.800 / 0.733 / 0.767, and the spread across seeds fell from 0.200 to 0.067, under the ten-point instability threshold. `discussion` F1 went from 0.000 / 0.000 / 0.667 to 0.800 / 0.714 / 0.759, and `skin_help` F1 from 0.667 / 0.667 / 0.788 to 0.875 / 0.828 / 0.857. Criteria 1 and 2 flipped from MISSED to MET. Criterion 3 did not move: `routine_review` F1 is 0.000 on all three seeds, and the model never predicted that label at all. So the collapse was undertraining for the two larger labels, but not the whole story for `routine_review`. On the seed-42 split the trained model now beats the baseline on accuracy (0.800 vs. 0.700) but still trails it on macro F1 (0.558 vs. 0.690), because the baseline scored 0.800 on `routine_review`. Caveat: each test split has only 30 posts, and `routine_review` has 3.


---

## What's Still Broken

**Criterion 3 (`routine_review` F1 ≥ 0.50), still MISSED.** I would add about 30 more `routine_review` posts, labeled with the same care as the first batch, and re-check the rows I relabeled near the `discussion` boundary. I stopped because the brief allows one change and the diagnosis pointed first at undertraining. Validation loss had flattened by epochs 8 to 10, so more epochs are unlikely to fix this label.

**Criterion 5 (labeling consistency), met only on a revised instrument.** It passes on staff-set agreement (20 of 30), not on my own 20 `cold` rows. I would have a second person label those 20 rows using only my taxonomy. I stopped because this unit supplied no second labeler for my own taxonomy.

**The gap between what I meant my labels to capture and what the model learned:**
I meant `routine_review` to capture posts centered on the poster's own products or regimen, but the model never predicted it on any seed, and 8 of its 9 test posts were called `discussion`. What it actually learned is a two-way split between `skin_help` and `discussion`, which is the only distinction the confusion matrix shows it making.

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
