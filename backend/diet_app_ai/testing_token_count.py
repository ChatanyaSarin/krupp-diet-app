'''
Tests the number of tokens used for a single user profile.
We test across NUM_TEST runs and print the average.
This can be used to estimate per user API costs.

The variables in the prompts follow naturally from each other.

The current workflow for this test is as follows:
1. Create an example user profile and generate initial meals.
2. Choose random likes and dislikes for the initial meals.
Over the course of NUM_DAYS days:
    3. Select random biomarkers.
    4. Generate daily meals.
    5. Update biomarker and taste summaries.

'''

import json
from langchain_community.callbacks import get_openai_callback

from initial_meal_generation_workflow import generate_initial_meals
from daily_meal_generation_workflow import generate_daily_meals
from preference_summary_workflow import update_taste_summary
from biomarker_summary_workflow import update_biomarker_summary

import numpy as np
import random

def repeat_daily_generation (user_profile: dict, NUM_DAYS: int, 
                             LIKED_MEALS_SAMPLE_SIZE = 5) -> [int, int]:
    user_setup_tokens = 0
    daily_meals_tokens = []

    user_setup_input_tokens = 0
    daily_meal_input_tokens = []
    user_setup_output_tokens = 0
    daily_meal_output_tokens = []

    biomarker_summary = None
    taste_summary = None
    dietary_restrictions = user_profile.get("dietary_restrictions", [])
    meals_last_period = []
    biomarker_journal = ""

    # Step 1: Generate initial meals
    with get_openai_callback() as cb:
        initial_meals = generate_initial_meals(user_profile)
        print("Initial Meals:", json.dumps(initial_meals, indent=2))
        print(f"Initial Meals Tokens: {cb.total_tokens}")
        user_setup_tokens += cb.total_tokens
        user_setup_input_tokens += cb.prompt_tokens
        user_setup_output_tokens += cb.completion_tokens

        meals = list(initial_meals.keys())

    # Step 2: Choose random likes and dislikes
    liked_initial_meals = random.sample(meals, min(LIKED_MEALS_SAMPLE_SIZE, len(meals)))
    disliked_initial_meals = [meal for meal in meals if meal not in liked_initial_meals]

    for day in range(NUM_DAYS):
        meal_tokens_for_day = 0
        input_tokens_for_day = 0
        output_tokens_for_day = 0
        # Step 3: Select random biomarkers
        biomarkers = {
            "Mood": random.randint(1, 10),
            "Energy": random.randint(1, 10),
            "Fullness": random.randint(1, 10),
        }

        # Step 4: Generate daily meals

        payload_context = {
            "biomarker_summary":    biomarker_summary or "No recent biomarker data.",
            "taste_summary":        taste_summary or "No strong preferences recorded.",
            "dietary_restrictions": dietary_restrictions,
        }

        with get_openai_callback() as cb:
            try:
                daily_meals = generate_daily_meals(payload_context)
            except:
                print(generate_daily_meals(payload_context))
            
            meal_tokens_for_day += cb.total_tokens
            input_tokens_for_day += cb.prompt_tokens
            output_tokens_for_day += cb.completion_tokens

            try:
                breakfast_meals = list(daily_meals.get("breakfast", []).keys())
                lunch_meals = list(daily_meals.get("lunch", []).keys())
                dinner_meals = list(daily_meals.get("dinner", []).keys())
            except:
                print(json.dumps(daily_meals, indent=2))

            print(breakfast_meals, lunch_meals, dinner_meals)

            liked_meals = [random.choice(breakfast_meals), random.choice(lunch_meals), random.choice(dinner_meals)]
            disliked_meals = [meal for meal in breakfast_meals + lunch_meals + dinner_meals if meal not in liked_meals]
            liked_meals = [" ".join(meal.split("-")) for meal in liked_meals]

        with get_openai_callback() as cb:
            # Step 5: Update biomarker summary
            existing_summary = biomarker_summary or "No prior biomarker summary."
            
            biomarker_payload = {
                "existing_summary": existing_summary,
                "biomarker_journal": biomarker_journal if len(biomarker_journal) == 0 else "No biomarker data yet.",
                "meals_last_period": json.dumps(meals_last_period) if len(meals_last_period) == 0 else "No meals eaten yet.",
            }

            biomarker_summary = update_biomarker_summary(biomarker_payload)
            meal_tokens_for_day += cb.total_tokens
            input_tokens_for_day += cb.prompt_tokens
            output_tokens_for_day += cb.completion_tokens

        with get_openai_callback() as cb:
            # Step 5: Update taste summary
            taste_payload = {
                "existing_summary": taste_summary or "No prior taste summary.",
                "liked_meals": json.dumps(liked_initial_meals + liked_meals),
                "disliked_meals": json.dumps(disliked_initial_meals + disliked_meals),
            }

            taste_summary = update_taste_summary(taste_payload)
            meal_tokens_for_day += cb.total_tokens
            input_tokens_for_day += cb.prompt_tokens
            output_tokens_for_day += cb.completion_tokens
        
        daily_meals_tokens.append(meal_tokens_for_day)
        daily_meal_input_tokens.append(input_tokens_for_day)
        daily_meal_output_tokens.append(output_tokens_for_day)

        meals_last_period = [liked_meals] if meals_last_period else list(meals_last_period) + [liked_meals]
        biomarkers_as_string = f"Day {day + 1} " + "  ".join([f"{k} {v}" for k, v in biomarkers.items()])
        biomarker_journal = biomarker_journal + "\n" + biomarkers_as_string

    daily_meals_tokens = np.mean(np.array(daily_meals_tokens)) # Average over NUM_DAYS days
    daily_meal_input_tokens = np.mean(np.array(daily_meal_input_tokens))
    daily_meal_output_tokens = np.mean(np.array(daily_meal_output_tokens))

    return [user_setup_tokens, daily_meals_tokens, user_setup_input_tokens, user_setup_output_tokens, daily_meal_input_tokens, daily_meal_output_tokens]

user_profile = {
    "height": 70,  # inches
    "weight": 150, # lbs
    "dietary_restrictions": ["vegetarian", "lactose-free"]
}

run_outputs = repeat_daily_generation(user_profile, NUM_DAYS = 5)

print(f"Total User Setup Tokens: {run_outputs[0]}")
print(f"Average Daily Meal Tokens (over {5} days): {run_outputs[1]}")
print(f"Total User Setup Input Tokens: {run_outputs[2]}")
print(f"Total User Setup Output Tokens: {run_outputs[3]}")
print(f"Average Daily Meal Input Tokens (over {5} days): {run_outputs[4]}")
print(f"Average Daily Meal Output Tokens (over {5} days): {run_outputs[5]}")


def run_initial_many_times (user_profile: dict, NUM_TESTS: int):
    initial_meal_tokens = []
    input_tokens = []
    output_tokens = []

    for _ in range(NUM_TESTS):
        with get_openai_callback() as cb:
            generate_initial_meals(user_profile)
            initial_meal_tokens.append(cb.total_tokens)
            input_tokens.append(cb.prompt_tokens)
            output_tokens.append(cb.completion_tokens)
    
    total_tokens = np.mean(np.array(initial_meal_tokens))
    avg_input_tokens = np.mean(np.array(input_tokens))
    avg_output_tokens = np.mean(np.array(output_tokens))

    return [total_tokens, avg_input_tokens, avg_output_tokens]

NUM_TESTS = 3

total_initial_tokens, avg_initial_input_tokens, avg_initial_output_tokens = run_initial_many_times(user_profile, NUM_TESTS)
print(f"Average Initial Meal Tokens (over {NUM_TESTS} tests): {total_initial_tokens}")
print(f"Average Initial Meal Input Tokens (over {NUM_TESTS} tests): {avg_initial_input_tokens}")
print(f"Average Initial Meal Output Tokens (over {NUM_TESTS} tests): {avg_initial_output_tokens}")
