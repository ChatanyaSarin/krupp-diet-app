"""
LANGCHAIN WORKFLOW · INITIAL MEAL GENERATION
Creates a function `generate_initial_meals(user_profile: dict) -> dict`.

The caller passes:
    user_profile = {
        "height": "180 cm",
        "weight": "75 kg",
        "goals":  "cut",
        "dietary_rules": "no pork, lactose-free"
    }
The function returns a Python dict parsed from the JSON produced by the LLM.
"""

from typing import Dict, Any
import json
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from diet_app_ai.initial_meal_generation_prompt import INITIAL_MEAL_GENERATION_PROMPT
from langchain_core.output_parsers.json import JsonOutputParser

GENAI_STUDIO_API_KEY = "sk-e7245ee0e151441f90bf24714fca6905" # Don't share

def get_llm(
    api_key: str = GENAI_STUDIO_API_KEY,
    base_url: str = "https://genai.rcac.purdue.edu/api",
    model_name: str = "llama3.1:latest",
    temperature: float = 0.7
    ):
    return ChatOpenAI(
        api_key=api_key,
        base_url=f"{base_url}",
        model=model_name,
        temperature=temperature,
    )


_PROMPT = PromptTemplate(
    template=INITIAL_MEAL_GENERATION_PROMPT,
    input_variables=["height", "weight", "goals", "dietary_rules"],
)


def generate_initial_meals(user_profile: Dict[str, Any]) -> Dict[str, Any]:
    parser = JsonOutputParser()
    print(user_profile)  # Debugging: print the formatted prompt
    chain = LLMChain(llm=get_llm(), 
                     prompt=_PROMPT,
                     output_parser = parser,
                     verbose = True # For testing
                    )
    return chain.invoke(user_profile)["text"]



# ── quick CLI test ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    demo = dict(height="175 cm", weight="70 kg",
                goals="maintain energy for marathon training",
                dietary_rules="vegetarian, gluten-free")
    
    json_meals = generate_initial_meals(demo)
    print(json.dumps(json_meals, indent = 4))
    print(json_meals.keys())
