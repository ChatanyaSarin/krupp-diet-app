"""
LANGCHAIN WORKFLOW · DAILY MEAL GENERATION
Function: `generate_daily_meals(context: dict) -> dict`
"""
from typing import Dict, Any
import json
from langchain import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import LlamaCpp
from daily_meal_generation_prompt import DAILY_MEAL_GENERATION_PROMPT
from initial_meal_generation_workflow import get_llm  # reuse helper
from langchain_core.output_parsers.json import JsonOutputParser

_PROMPT = PromptTemplate(
    template=DAILY_MEAL_GENERATION_PROMPT,
    input_variables=["biomarker_summary", "taste_summary", "day_macro_goals"],
)


def generate_daily_meals(context: Dict[str, Any]) -> Dict[str, Any]:
    parser = JsonOutputParser()
    chain = LLMChain(llm=get_llm(), 
                     prompt=_PROMPT,
                     output_parser = parser,
                     verbose = True # For testing
                    )
    
    return chain.invoke(context)["text"]

if __name__ == "__main__":
    demo_ctx = {
        # Four biomarkers on a 1‑10 scale (10 = best)
        "biomarker_summary": "strength:8, skin:6, energy:7, bloating:9",
        # Random taste profile
        "taste_summary": "Enjoys Mediterranean flavors and legumes; dislikes very spicy food; pescatarian.",
        # User’s current nutrition objective
        "user_goals": "Cut 200 kcal/day while keeping protein high for strength training."
    }

    meals = generate_daily_meals(demo_ctx)

    print(json.dumps(meals, indent=2, ensure_ascii=False))
    print("Top‑level keys →", meals.keys())
