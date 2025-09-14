# daily_meal_generation_prompts.py

DAILY_SYSTEM = """You are a meal-planning model.
Generate exactly 3 sections — breakfast, lunch, dinner — each with 5 suggestions.
Return ONLY JSON that matches the schema below. Each suggestion must include:
- long_name  (a human-friendly title)
- description (exactly 1–2 short sentences)
- ingredients (an object mapping {{ingredient: amount_string}})
- instructions (a single string with numbered or newline-separated steps)

Hard requirements:
- Rigorously honor the user's dietary restrictions. Vegetarian means VEGETARIAN MEALS.
- Reflect the user's goals (e.g., bulk, energy) and their taste preferences.
- Vary cuisines and macronutrient balance across suggestions.
- Use concise units (cups, tbsp, g, ml, slices, etc.).
- Do NOT include any text outside the JSON.
"""

# Note: we include BOTH the new and legacy keys so PromptTemplate.from_template()
# will accept either. Your chain should pass values for the union:
#   biomarker_summary, taste_profile, taste_summary, goals, user_goals, dietary_restrictions
DAILY_USER = """Context:
- Biomarker summary: {biomarker_summary}
- Taste preferences (profile/summary): {taste_summary}
- Dietary restrictions: {dietary_restrictions}

Output JSON (example shape):
Output format example:
{{
  "breakfast": {{
    "slug1": {{
      "long_name": "...",
      "description": "...,
      "ingredients": {{ "ingredient": "amount", ... }},
      "instructions": "1) ...\\n2) ..."
    }},
    ...
    "slug5": {{ ... }}
  }},
  "lunch": {{ ... }},
  "dinner": {{ ... }}
}}"""

DAILY_MEAL_GENERATION_PROMPT = DAILY_SYSTEM + "\n" + DAILY_USER
