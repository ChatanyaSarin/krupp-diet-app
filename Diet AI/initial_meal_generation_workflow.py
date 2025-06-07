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
from langchain import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import LlamaCpp  # easy to swap
from initial_meal_generation_prompt import INITIAL_MEAL_GENERATION_PROMPT


def get_llm(model_path: str = "llama-7b.gguf", temperature: float = 0.7):
    """Return a LangChain-compatible Llama model (swap here to change LLM)."""
    return LlamaCpp(
        model_path=model_path,
        temperature=temperature,
        n_ctx=4096,
    )


_PROMPT = PromptTemplate(
    template=INITIAL_MEAL_GENERATION_PROMPT,
    input_variables=["height", "weight", "goals", "dietary_rules"],
)


def generate_initial_meals(user_profile: Dict[str, Any]) -> Dict[str, Any]:
    chain = LLMChain(llm=get_llm(), prompt=_PROMPT)
    raw_json = chain.run(user_profile).strip()
    try:
        return json.loads(raw_json)
    except json.JSONDecodeError as exc:  # surface a helpful error
        raise ValueError(f"LLM returned invalid JSON:\n{raw_json}") from exc


# ── quick CLI test ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    demo = dict(height="175 cm", weight="70 kg",
                goals="maintain energy for marathon training",
                dietary_rules="vegetarian, gluten-free")
    print(generate_initial_meals(demo))
