"""
Prompt used for the INITIAL MEAL GENERATION step.

Inputs expected from the calling workflow
-----------------------------------------
{height}           – str | int | float   – e.g. "180 cm"
{weight}           – str | int | float   – e.g. "75 kg"
{goals}            – str                 – free-text goal description
{dietary_rules}    – str                 – comma-separated restrictions

Outputs (JSON)
--------------
Ten top-level keys (meal slugs).  Each key → {
    "long_name"      : str,
    "ingredients"    : {<item>: <amount>, ...},
    "instructions"   : str
}
"""
INITIAL_MEAL_GENERATION_PROMPT = """\
You are a performance-nutrition expert designing meals for a new user.

USER PROFILE
︙ Height: {height}
︙ Weight: {weight}
︙ Goals : {goals}
︙ Dietary restrictions: {dietary_rules}

TASK
1. Produce exactly **10** distinct meal ideas suitable for one serving each.
2. Respect every dietary restriction.
3. Bias choices toward the user’s goals (cut, bulk, extra energy …).
4. Return **only** valid JSON that follows this schema:

{
  "slug1": {
    "long_name": "...",
    "ingredients": { "item": "amount", ... },
    "instructions": "Step-by-step text ..."
  },
  …
  "slug10": { … }
}

Make the outer keys URL-safe slugs (lowercase, words separated by hyphens).  
Never wrap the JSON in triple back-ticks or any extra text.
"""
