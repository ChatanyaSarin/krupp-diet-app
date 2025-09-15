"""
LANGCHAIN WORKFLOW · INITIAL MEAL GENERATION
Creates a function `generate_initial_meals(user_profile: dict) -> dict`.

The caller passes:
    user_profile = {
        "height": "180 cm",
        "weight": "75 kg",
        "dietary_rules": "no pork, lactose-free"
    }
The function returns a Python dict parsed from the JSON produced by the LLM.
"""

from typing import Dict, Any
import json
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from initial_meal_generation_prompt import INITIAL_MEAL_GENERATION_PROMPT
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

def custom_parser (json_string):
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        first_brace = json_string.find('{')
        last_brace = json_string.rfind('}')
        if first_brace != -1 and last_brace != -1 and first_brace < last_brace:
            trimmed_string = json_string[first_brace:last_brace + 1]
            try:
                return json.loads(trimmed_string)
            except json.JSONDecodeError:
                print(json_string)
                raise e
        else:
            print(json_string)
            raise e

def generate_initial_meals(user_profile: dict) -> dict:
    """
    user_profile = {
      "height": int, "weight": int,
      "dietary_restrictions": [..]
    }
    Returns: dict keyed by slug -> {
      long_name, description, ingredients:{..}, instructions
    }
    """
    updated_user_profile = user_profile.copy()
    updated_user_profile["dietary_restrictions"] = ", ".join(updated_user_profile.get("dietary_restrictions", []))

    parser = JsonOutputParser()
    prompt = PromptTemplate.from_template(INITIAL_MEAL_GENERATION_PROMPT)
    chain = LLMChain(llm=get_llm(), prompt=prompt, verbose=True)

    return custom_parser(chain.invoke(updated_user_profile)["text"])