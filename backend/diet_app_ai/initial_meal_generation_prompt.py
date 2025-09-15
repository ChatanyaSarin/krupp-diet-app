# initial_meal_generation_prompts.py
INITIAL_MEAL_SYSTEM = """You are a diet planning assistant. Generate 10 diverse, realistic meals as JSON only.
Each top-level key is a short, hyphen-seperated slug.
For each meal include:
- long_name: longer descriptive title
- description: one-sentence appetizing blurb
- ingredients: object of {{item: amount_string}}
- instructions: single string with numbered or newline steps
- RESPECT USER DIETARY RESTRICTIONS (e.g., vegetarian means NO MEAT/SEAFOOD).
Return ONLY valid JSON, no markdown fences, no commentary."""

INITIAL_MEAL_USER = """User profile:
- Height (in): {height}
- Weight (lb): {weight}
- Dietary restrictions (comma-separated): {dietary_restrictions}

Output format example:
{{
  "slug1": {{
    "long_name": "...",
    "description": "...,
    "ingredients": {{ "ingredient": "amount", ... }},
    "instructions": "1) ...\\n2) ..."
  }},
  ...
  "slug10": {{ ... }}
}}"""

INITIAL_MEAL_GENERATION_PROMPT = INITIAL_MEAL_SYSTEM + "\n" + INITIAL_MEAL_USER