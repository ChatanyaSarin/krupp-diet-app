"""
Prompt for MEAL-PREFERENCE SUMMARIZATION.

Variables
---------
{existing_summary} – str (may be empty the first time)
{liked_meals}      – JSON string or bullet list
{disliked_meals}   – JSON string or bullet list

Output
------
A concise paragraph (≤120 words) describing patterns in likes & dislikes.
"""
PREFERENCE_SUMMARIZATION_PROMPT = """\
You are updating a user taste profile summarizing meal preferences.

EXISTING SUMMARY
{existing_summary}

NEW DATA
Liked  : {liked_meals}
Disliked: {disliked_meals}

TASK
1. Detect themes (cuisine styles, ingredients, textures, cooking methods).
2. Update the summary in ≤120 words, written as third-person notes.
3. Keep positive & negative preferences balanced and specific.

Return ONLY the revised summary text, no JSON needed.
"""
