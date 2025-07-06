"""
LANGCHAIN WORKFLOW · MEAL-PREFERENCE SUMMARIZATION
Function: `update_taste_summary(data: dict) -> str`
"""
from typing import Dict
from langchain import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import LlamaCpp
from diet_app_ai.preference_summary_prompt import PREFERENCE_SUMMARIZATION_PROMPT
from diet_app_ai.initial_meal_generation_workflow import get_llm

_PROMPT = PromptTemplate(
    template=PREFERENCE_SUMMARIZATION_PROMPT,
    input_variables=["existing_summary", "liked_meals", "disliked_meals"],
)


def update_taste_summary(data: Dict[str, str]) -> str:
    chain = LLMChain(llm=get_llm(), prompt=_PROMPT)
    return chain.run(data).strip()
