from typing import Dict, Any
import json
from langchain import LLMChain
from langchain.prompts import PromptTemplate
from daily_meal_generation_prompt import DAILY_MEAL_GENERATION_PROMPT
from initial_meal_generation_workflow import get_llm

_PROMPT = PromptTemplate(
    template=DAILY_MEAL_GENERATION_PROMPT,
    input_variables=["biomarker_summary", "taste_summary", "day_macro_goals"],
)

def generate_daily_meals(context: Dict[str, Any]) -> Dict[str, Any]:
    chain = LLMChain(llm=get_llm(), prompt=_PROMPT)
    raw_json = chain.run(context).strip()
    try:
        return json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM returned invalid JSON:\n{raw_json}") from exc
