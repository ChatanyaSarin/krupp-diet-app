import datetime as dt
from flask import Blueprint, request, jsonify

from models import (
    UserPreferences, UserMealPreference, UserBiomarker,
    MealIngredientRow, MealStepRow, UserSummarization
)
from sheets_client import batch_get

# ——— import LangChain workflows ———
from diet_app_ai.initial_meal_generation_workflow import generate_initial_meals
from diet_app_ai.daily_meal_generation_workflow   import generate_daily_meals
from diet_app_ai.biomarker_summary_workflow       import update_biomarker_summary
from diet_app_ai.preference_summary_workflow      import update_taste_summary

bp = Blueprint("api", __name__)
TODAY = lambda: dt.datetime.now().strftime("%Y-%m-%d")


# ---------- 1. Initial preference intake ----------
@bp.post("/setup_user")
def setup_user():
    data = request.get_json()
    prefs = UserPreferences(**data)
    prefs.save()
    return {"status": "ok"}, 201


# ---------- 2. Initial meal generation ----------
@bp.post("/meals/initial")
def meals_initial():
    req = request.get_json()
    username = req["Username"]

    prefs_row = batch_get(["UserPreferences"])["UserPreferences"]
    prefs = next(r for r in prefs_row[1:] if r[0] == username)  # brutish lookup
    height, weight, goals, restrictions = prefs[1:5]

    meals = generate_initial_meals(
        dict(
            user_height=height,
            user_weight=weight,
            dietary_restrictions=restrictions.split(","),
            goals=goals.split(",")
        )
    )

    # flatten ingredients & steps into rows
    for slug, meta in meals.items():
        for ing, amt in meta["ingredients"].items():
            MealIngredientRow(
                Date=TODAY(), Username=username, MealType="Initial",
                MealCode=slug, Ingredient=ing, Amount=amt,
                Model="llama", Temperature=0.7
            ).save()
        for i, step in enumerate(meta["instructions"].split("."), 1):
            if step.strip():
                MealStepRow(
                    Date=TODAY(), Username=username, MealType="Initial",
                    MealCode=slug, Step=i, Instruction=step.strip(),
                    Model="llama", Temperature=0.7
                ).save()

    return meals, 200


# ---------- 3. Like / dislike feedback ----------
@bp.post("/meals/feedback")
def meal_feedback():
    data = request.get_json()
    entry = UserMealPreference(Date=TODAY(), **data)
    entry.save()
    return {"status": "ok"}, 201


# ---------- 4. Biomarker submission ----------
@bp.post("/biomarkers")
def biomarkers():
    data = request.get_json()
    row = UserBiomarker(Date=TODAY(), **data)
    row.save()
    return {"status": "ok"}, 201


# ---------- 5. Daily meal generation ----------
@bp.post("/meals/daily")
def meals_daily():
    req = request.get_json()
    username = req["Username"]

    # --- gather summaries from sheets ---
    tabs = batch_get(["UserSummarization", "UserPreferences"])
    pref_summary = next((r[2] for r in tabs["UserSummarization"][1:]
                         if r[1] == username), "")
    biom_summary = next((r[3] for r in tabs["UserSummarization"][1:]
                         if r[1] == username), "")
    goals = next((r[3] for r in tabs["UserPreferences"][1:]
                  if r[0] == username), "")

    meals = generate_daily_meals(
        dict(
            biomarker_feedback=biom_summary,
            user_preferences=pref_summary,
            regenerate_meals=None
        )
    )

    # persist
    for meal_type, suggestions in meals.items():
        for slug, meta in suggestions.items():
            for ing, amt in meta["ingredients"].items():
                MealIngredientRow(
                    Date=TODAY(), Username=username, MealType=meal_type,
                    MealCode=slug, Ingredient=ing, Amount=amt,
                    Model="llama", Temperature=0.7
                ).save()
            for i, step in enumerate(meta["instructions"].split("."), 1):
                if step.strip():
                    MealStepRow(
                        Date=TODAY(), Username=username, MealType=meal_type,
                        MealCode=slug, Step=i, Instruction=step.strip(),
                        Model="llama", Temperature=0.7
                    ).save()

    return meals, 200


# ---------- 6. Save daily summaries ----------
@bp.post("/summaries")
def summaries():
    data = request.get_json()
    row = UserSummarization(Date=TODAY(), **data)
    row.save()
    return {"status": "ok"}, 201
