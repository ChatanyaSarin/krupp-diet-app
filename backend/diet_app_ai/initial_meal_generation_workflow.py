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

def generate_initial_meals(user_profile: dict) -> dict:
    """
    user_profile = {
      "height": int, "weight": int,
      "dietary_restrictions": [..], "goals": [..]
    }
    Returns: dict keyed by slug -> {
      long_name, description, ingredients:{..}, instructions
    }
    """

    parser = JsonOutputParser()
    prompt = PromptTemplate.from_template(INITIAL_MEAL_GENERATION_PROMPT)
    chain = LLMChain(llm=get_llm(), prompt=prompt, verbose=True, output_parser = parser)

    return chain.invoke(user_profile)["text"]

