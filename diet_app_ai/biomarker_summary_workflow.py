"""
LANGCHAIN WORKFLOW · BIOMARKER FEEDBACK SUMMARIZATION
Function: `update_biomarker_summary(payload: dict) -> str`
"""
from typing import Dict
from langchain import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import LlamaCpp
from biomarker_summary_prompt import BIOMARKER_SUMMARIZATION_PROMPT
from initial_meal_generation_workflow import get_llm

_PROMPT = PromptTemplate(
    template=BIOMARKER_SUMMARIZATION_PROMPT,
    input_variables=[
        "existing_summary",
        "biomarker_journal",
        "meals_last_period",
    ],
)


def update_biomarker_summary(payload: Dict[str, str]) -> str:
    chain = LLMChain(llm=get_llm(), prompt=_PROMPT)
    return chain.run(payload).strip()
