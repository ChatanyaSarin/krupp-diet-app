# initial_meal_generation_prompts.py
INITIAL_MEAL_SYSTEM = """You are a diet planning assistant. Generate 10 diverse, realistic meals as JSON only.
Each top-level key is a short slug (e.g., "chicken-sandwich").
For each meal include:
- long_name: longer descriptive title
- description: one-sentence appetizing blurb
- ingredients: object of {{item: amount_string}}
- instructions: single string with numbered or newline steps
Return ONLY valid JSON, no markdown fences, no commentary."""

INITIAL_MEAL_USER = """User profile:
- Height (in): {height}
- Weight (lb): {weight}
- Goals (comma-separated): {goals}
- Dietary restrictions (comma-separated): {dietary_restrictions}

Output format example:
{{
  "slug1": {{
    "long_name": "Grilled Chicken Sandwich with Chimichurri",
    "description": "A zesty, protein-forward sandwich with bright herbs.",
    "ingredients": {{ "chicken breast": "1", "roll": "1", "chimichurri": "2 tbsp" }},
    "instructions": "1) ...\\n2) ..."
  }},
  ...
  "slug10": {{ ... }}
}}"""

INITIAL_MEAL_GENERATION_PROMPT = INITIAL_MEAL_SYSTEM + "\n" + INITIAL_MEAL_USER