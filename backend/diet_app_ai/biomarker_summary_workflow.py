"""
LANGCHAIN WORKFLOW · BIOMARKER FEEDBACK SUMMARIZATION
Function: `update_biomarker_summary(payload: dict) -> str`
"""
from typing import Dict
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from biomarker_summary_prompt import BIOMARKER_SUMMARIZATION_PROMPT
from initial_meal_generation_workflow import get_llm
import json

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

if __name__ == "__main__":
    payload = dict(
        existing_summary=(
            "User typically feels best after high-fiber, plant-forward dinners "
            "and reports mild bloating when meals are very legume-heavy."
        ),
        biomarker_journal=(
            # strength, skin, energy, bloating scores (10 = great)
            "2025-06-10  strength 6  skin 8  energy 5  bloating 4\n"
            "2025-06-11  strength 7  skin 7  energy 6  bloating 3\n"
            "2025-06-12  strength 5  skin 6  energy 4  bloating 2"
        ),
        meals_last_period=json.dumps([
            "quinoa-black-bean-bowl",
            "greek-salad-with-feta",
            "tofu-stir-fry-with-broccoli"
        ]),
    )

    new_summary = update_biomarker_summary(payload)
    print("\n── Biomarker summary update ──\n")
    print(new_summary)