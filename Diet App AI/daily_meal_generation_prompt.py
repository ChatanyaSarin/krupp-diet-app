"""
Prompt for DAILY MEAL GENERATION.

Incoming variables
------------------
{biomarker_summary} – str (can be empty)
{taste_summary}     – str (can be empty)
{user_goals}        – str – high-level macro/goal info (optional)

Outputs (JSON)
--------------
{
  "breakfast": {
      "slug1": { long_name, ingredients, instructions },
      … (5 keys total)
  },
  "lunch":     { … 5 suggestions … },
  "dinner":    { … 5 suggestions … }
}
"""
DAILY_MEAL_GENERATION_PROMPT = """\
You are a personal nutrition AI creating daily meal options.

CONTEXT
⋅ Biomarker summary (last two weeks): {biomarker_summary}
⋅ Taste preferences summary: {taste_summary}
⋅ User goals: {user_goals}

TASK
• Propose 5 candidate meals EACH for breakfast, lunch, and dinner (15 total).
• Respect the user’s dietary restrictions and goals implied by the summaries.
• Keep recipes feasible in < 40 min cook time.
• Return **only** valid JSON that follows this schema:

{
  "breakfast": {
      "slug1": { long_name, ingredients, instructions },
      … (5 keys total)
  },
  "lunch":     { … 5 suggestions … },
  "dinner":    { … 5 suggestions … }
}

Return ONLY JSON in the schema shown above, no commentary, no code-fences.
"""
