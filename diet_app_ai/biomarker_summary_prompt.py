"""
Prompt for BIOMARKER FEEDBACK SUMMARIZATION.

Variables
---------
{existing_summary}    – str (may be empty)
{biomarker_journal}   – str  ← raw text of user logs (mood, bloating, etc.)
{meals_last_period}   – JSON or bullet list of meals eaten in that same window

Output
------
A short evidence-style narrative linking ingredients → possible biomarker effects.
Keep it ≤150 words.
"""
BIOMARKER_SUMMARIZATION_PROMPT = """\
You are an AI nutrition analyst relating meals to biomarker feedback.

PREVIOUS FINDINGS
{existing_summary}

LATEST DATA
• Biomarker journal:
{biomarker_journal}

• Meals eaten in this window:
{meals_last_period}

TASK
Write ≤150 words summarizing plausible relationships between recurring
ingredients/nutrients and the user’s biomarkers.  Use hedging language
("may", "could") rather than strong causal claims.  No citations yet.

Return ONLY the output text. DO NOT include any other text.
"""
