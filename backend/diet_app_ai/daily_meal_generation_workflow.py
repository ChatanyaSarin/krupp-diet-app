"""
LANGCHAIN WORKFLOW · DAILY MEAL GENERATION
Function: `generate_daily_meals(context: dict) -> dict`
"""
from typing import Dict, Any, List
import json
from langchain import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import LlamaCpp
from daily_meal_generation_prompt import DAILY_MEAL_GENERATION_PROMPT
from initial_meal_generation_workflow import get_llm  # reuse helper
from langchain_core.output_parsers.json import JsonOutputParser


_PROMPT = PromptTemplate.from_template(
    DAILY_MEAL_GENERATION_PROMPT
)

def generate_daily_meals(context: Dict[str, Any]) -> str:
    """Generate daily meals JSON using a prompt that expects both the new and legacy keys."""
    parser = JsonOutputParser()

    context_copy = context.copy()
    context_copy["dietary_restrictions"] = ", ".join(context_copy.get("dietary_restrictions", []))

    chain = LLMChain(llm=get_llm(), prompt=_PROMPT, verbose=True, output_parser = parser)

    return chain.invoke(context_copy)["text"]