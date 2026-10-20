# Label Taxonomy

Community: r/SkincareAddiction. Each label describes what the post is *doing*, based on the title and body together.

## skin_help
**Definition:** The poster centers their own skin concern or appearance, or asks what works for a skin problem, and wants advice or opinions.
**Example 1:** "I need some product recommendations for my skin"
**Example 2:** "It's been five years and I'm tired. Has anyone else had Skin like this and been able to clear it?"

## routine_review
**Definition:** The poster centers their own products or regimen, either asking for feedback on it or sharing it as something that works for them.
**Example 1:** "[Routine Help] Is my routine too much?"
**Example 2:** "[B&A] I've spent $10000 on Skincare and this is my skincare routine"

## discussion
**Definition:** The post starts a general conversation or shares information (trends, ingredients, marketing, news, community meta) rather than centering the poster's own skin or routine.
**Example 1:** "'over 700,000 people have died': face masks, skincare and insensitivity towards a global pandemic in r/skincareaddiction"
**Example 2:** "The first new sunscreen in 25 years is finally arriving in stores in the U.S."

## Hardest boundary: skin_help vs. routine_review
**A post that sits between them:** "I think I've found a good routine for my decades-persistent acne!"
**Why it's hard:** It names a skin problem (acne) and a routine (the solution), and it isn't a question.
**Decision rule:** Ask what the post is centered on. If the poster's own routine or products are the subject, label it `routine_review`, even if a skin concern is mentioned as context. If the poster's own skin concern or appearance is the subject and products are background or a request, label it `skin_help`. For the borderline post above, the routine is the headline, so it is `routine_review`.

**Order of rules:** Apply Tie-break A first, then the main decision rule, then Tie-break B only if still unresolved.

**Tie-break A (personal detail + general question):** Ask whether the question would still make sense without the poster's personal details. If yes ("is double cleansing a marketing thing?", "has anyone else stopped using fragrance?"), label it `discussion`. If the answer depends on the poster's own skin or routine, use `skin_help` or `routine_review`.

**Tie-break B (post asks about both skin and routine):** Label by the first ask in the title. If the title doesn't settle it, label by the ask in the first sentence of the body.

## Dropped or merged
`news` was folded into `discussion`. In the ~40 posts I read, 5 were news or regulation posts (about 12%), which would give roughly 25 examples in a 200-post dataset. That is too few to train on and too few to measure reliably on a 15% test split, where it would leave only about 4 examples.

## Changes made after the boundary stress test
I labeled eight invented boundary posts cold. I hesitated on three, and posts that mixed a personal detail with a general question exposed a gap in my first rule. I added Tie-break A and Tie-break B in response.