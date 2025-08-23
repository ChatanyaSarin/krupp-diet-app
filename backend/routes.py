import datetime as dt
import json
from typing import Any
from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt

from models import UserPreferences, UserMealPreference, UserBiomarker, MealIngredientRow, MealStepRow, UserSummarization

from sheets_client import batch_get, append_row, get_values, find_row_by_header_value, update_row, append_rows

bcrypt = Bcrypt()

# ——— import LangChain workflows ———
from diet_app_ai.initial_meal_generation_workflow import generate_initial_meals
from diet_app_ai.daily_meal_generation_workflow   import generate_daily_meals
from diet_app_ai.biomarker_summary_workflow       import update_biomarker_summary
from diet_app_ai.preference_summary_workflow      import update_taste_summary

bp = Blueprint("api", __name__)
TODAY = lambda: dt.datetime.now().strftime("%Y-%m-%d")

# ---------- Summaries: collect + run ----------

from collections import defaultdict

def _parse_date(s: str) -> dt.date | None:
    try:
        return dt.datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        return None

def _collect_recent_biomarkers(username: str, window_days: int = 7) -> list[dict[str, int | str]]:
    rows = get_values("UserBiomarker")
    if not rows:
        return []
    hdr = rows[0]
    try:
        d_i = hdr.index("Date"); u_i = hdr.index("Username")
        b1_i = hdr.index("BIOMARKER 1"); b2_i = hdr.index("BIOMARKER 2"); b3_i = hdr.index("BIOMARKER 3")
    except ValueError:
        return []
    today = dt.date.today()
    out = []
    for r in rows[1:]:
        if len(r) <= max(d_i, u_i, b1_i, b2_i, b3_i): continue
        if r[u_i] != username: continue
        d = _parse_date(r[d_i])
        if not d or (today - d).days > window_days: continue
        try:
            out.append({
                "date": r[d_i],
                "b1": int(r[b1_i]),
                "b2": int(r[b2_i]),
                "b3": int(r[b3_i]),
            })
        except Exception:
            continue
    return out

def _collect_recent_meals_json(username: str, window_days: int = 7) -> dict[str, dict]:
    """Rebuild minimal meal JSON from MealIngredients/MealSteps for the last N days."""
    # Ingredients
    ing_rows = get_values("MealIngredients")
    steps_rows = get_values("MealSteps")
    today = dt.date.today()

    def _by_meal(rows, is_ing=True):
        if not rows: return {}
        hdr = rows[0]
        idx = {name: (hdr.index(name) if name in hdr else None) for name in
               (["Date","Username","MealType","MealCode","Ingredients","Amount"] if is_ing
                else ["Date","Username","MealType","MealCode","Step","Instruction"])}
        m = defaultdict(lambda: {"long_name": "", "ingredients": {}, "instructions": []})
        for r in rows[1:]:
            if any(idx[k] is None or len(r) <= idx[k] for k in idx): continue
            if r[idx["Username"]] != username: continue
            d = _parse_date(r[idx["Date"]]); 
            if not d or (today - d).days > window_days: continue
            code = r[idx["MealCode"]]
            if is_ing:
                ing, amt = r[idx["Ingredients"]], str(r[idx["Amount"]])
                m[code]["ingredients"][ing] = amt
            else:
                step_txt = r[idx["Instruction"]].strip()
                if step_txt:
                    m[code]["instructions"].append(step_txt)
        return m

    m_ing = _by_meal(ing_rows, True)
    m_steps = _by_meal(steps_rows, False)

    # Merge
    all_codes = set(m_ing.keys()) | set(m_steps.keys())
    out = {}
    for code in all_codes:
        ings = dict(m_ing.get(code, {}).get("ingredients", {}))
        steps_list = m_steps.get(code, {}).get("instructions", [])
        out[code] = {
            "long_name": code.replace("-", " ").title(),
            "ingredients": ings,
            "instructions": "\n".join(steps_list),
        }
    return out

def _collect_recent_likes(username: str, window_days: int = 7) -> tuple[list[str], list[str]]:
    rows = get_values("UserMealPreferences")
    if not rows:
        return ([], [])
    hdr = rows[0]
    try:
        d_i = hdr.index("Date"); u_i = hdr.index("Username")
        code_i = hdr.index("MealCode"); like_i = hdr.index("Like")
    except ValueError:
        return ([], [])
    today = dt.date.today()
    likes, dislikes = [], []
    for r in rows[1:]:
        if len(r) <= max(d_i, u_i, code_i, like_i): continue
        if r[u_i] != username: continue
        d = _parse_date(r[d_i])
        if not d or (today - d).days > window_days: continue
        (likes if (r[like_i].upper() == "TRUE") else dislikes).append(r[code_i])
    return (likes, dislikes)

@bp.post("/summaries/run")
def run_summaries():
    """Compute both summaries and store them in UserSummarization."""
    data = request.get_json(silent=True) or {}
    username = (data.get("Username") or "").strip()
    window_days = int(data.get("window_days", 7))
    if not username:
        return {"error": "Username is required"}, 400

    # existing summaries (if any)
    old_bio, old_taste = _latest_summaries(username)

    # fresh windows
    biomarker_window = _collect_recent_biomarkers(username, window_days)
    meals_json = _collect_recent_meals_json(username, window_days)
    liked, disliked = _collect_recent_likes(username, window_days)

    # LLM calls (robust to empty inputs)
    try:
        new_bio = update_biomarker_summary(
            payload = {
                existing_summary=old_bio or "",
                recent_biomarkers=biomarker_window,
                recent_meals=meals_json,
            }
        )
    except Exception as e:
        return {"error": f"update_biomarker_summary failed: {e}"}, 500

    try:
        new_taste = update_taste_summary(
            data = {
                "existing_summary": old_taste or "",
                "liked_meals": liked,
                "disliked_meals": disliked,
            }
        )
    except Exception as e:
        return {"error": f"update_taste_summary failed: {e}"}, 500

    # write a single combined row
    append_row("UserSummarization", [
        TODAY(), username, new_taste, new_bio, "llama", 0.7
    ])
    return {"ok": True}, 201



# POST /auth/login
@bp.post("/auth/login")
def auth_login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    row_idx, row, header = find_row_by_header_value("Users", "Username", username)
    if row is None:
        return jsonify({"error": "user not found"}), 404

    ph_i = header.index("PasswordHash")
    pwd_hash = row[ph_i] if len(row) > ph_i else ""

    if not pwd_hash:
        # user exists but has not set a password yet
        return jsonify({"needsPassword": True}), 409

    if not bcrypt.check_password_hash(pwd_hash, password):
        return jsonify({"error": "bad credentials"}), 401

    # You can mint a JWT here; keeping it simple for the study
    return jsonify({"ok": True}), 200


# POST /auth/register  (first-time password set)
@bp.post("/auth/register")
def auth_register():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    row_idx, row, header = find_row_by_header_value("Users", "Username", username)
    if row is None:
        return jsonify({"error": "user not in roster"}), 404

    ph_i = header.index("PasswordHash")
    ca_i = header.index("CreatedAt")

    pwd_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    # Expand row to header length
    row = (row + [""] * (len(header) - len(row)))[:len(header)]
    row[ph_i] = pwd_hash
    if not row[ca_i]:
        row[ca_i] = TODAY()

    if row_idx is None:
        return jsonify({"error": "user row index not found"}), 500

    update_row("Users", row_idx, row)
    return jsonify({"ok": True}), 201


# GET /user/status?username=alice
@bp.get("/user/status")
def user_status():
    username = request.args.get("username", "").strip()

    # has_profile?
    prefs = get_values("UserPreferences")
    has_profile = any(r and r[0] == username for r in prefs[1:])

    # has_initial_feedback?
    ump = get_values("UserMealPreferences")
    # Expect headers include: Date, Username, MealCode, Like, Initial
    try:
        hdr = ump[0]
        u_i, init_i = hdr.index("Username"), hdr.index("Initial")
        has_initial = any(len(r) > max(u_i, init_i) and r[u_i] == username and r[init_i].upper() == "TRUE"
                          for r in ump[1:])
    except Exception:
        has_initial = False

    return jsonify({"has_profile": has_profile, "has_initial_feedback": has_initial}), 200

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
    req = request.get_json() or {}
    username = req["Username"].strip()

    # ----- read UserPreferences safely -----
    vals = get_values("UserPreferences")  # [['Username','Height','Weight','Goals','DietaryRestrictions', ...], [..], ...]
    if not vals:
        return jsonify({"error": "UserPreferences tab is empty or missing"}), 400

    header = vals[0]
    def idx(col): 
        try: return header.index(col)
        except ValueError: return None

    u_i = idx("Username"); h_i = idx("Height"); w_i = idx("Weight")
    g_i = idx("Goals"); dr_i = idx("DietaryRestrictions")

    if None in (u_i, h_i, w_i, g_i, dr_i):
        return jsonify({"error": f"UserPreferences header must include "
                                 f"[Username, Height, Weight, Goals, DietaryRestrictions]. "
                                 f"Found: {header}"}), 400

    row = None
    if u_i is not None:
        row = next((r for r in vals[1:] if len(r) > u_i and r[u_i] == username), None)
    if not row:
        # Friendly error instead of StopIteration
        return jsonify({"error": f"No profile found for username '{username}' in UserPreferences"}), 404

    # Extract and coerce values
    try:
        if h_i is None or w_i is None:
            raise IndexError("Height or Weight index is None")
        height = int(row[h_i])
        weight = int(row[w_i])
    except (ValueError, IndexError, TypeError):
        return jsonify({"error": "Height/Weight must be integers in UserPreferences"}), 400

    goals = [s.strip() for s in (row[g_i] if g_i is not None and len(row) > g_i else "").split(",") if s.strip()]
    restrictions = [s.strip() for s in (row[dr_i] if dr_i is not None and len(row) > dr_i else "").split(",") if s.strip()]

    # ----- call LLM -----
    meals = generate_initial_meals(
        user_profile={
            "height": height,
            "weight": weight,
            "dietary_restrictions": restrictions,
            "goals": goals,
        }
    )

    # ----- persist ingredients & steps in batches -----
    rows_ing, rows_steps = [], []
    for slug, meta in meals.items():
        for ing, amt in meta["ingredients"].items():
            rows_ing.append([
                TODAY(), username, "Initial", slug,
                ing, amt, "llama", 0.7
            ])
        # split instructions by line OR period; keep non-empty steps
        raw = meta["instructions"].replace("\r", "").split("\n")
        parts = [p for p in raw if p.strip()] if len(raw) > 1 else [s for s in meta["instructions"].split(".") if s.strip()]
        for i, step in enumerate(parts, 1):
            rows_steps.append([
                TODAY(), username, "Initial", slug,
                i, step.strip(), "llama", 0.7
            ])

    if rows_ing:
        append_rows("MealIngredients", rows_ing)
    if rows_steps:
        append_rows("MealSteps", rows_steps)

    return meals, 200

# ---------- 4. Biomarker submission ----------
@bp.post("/biomarkers")
def biomarkers():
    data = request.get_json(silent=True) or {}
    username = (data.get("Username") or "").strip()
    if not username:
        return {"error": "Username is required"}, 400

    # Accept multiple key styles and coerce to ints
    def _geti(*keys):
        for k in keys:
            if k in data and data[k] not in (None, ""):
                return int(data[k])
        raise KeyError(keys[0])

    try:
        b1 = _geti("BIOMARKER 1", "Biomarker1", "b1")
        b2 = _geti("BIOMARKER 2", "Biomarker2", "b2")
        b3 = _geti("BIOMARKER 3", "Biomarker3", "b3")
    except (KeyError, ValueError):
        return {"error": "Biomarkers must be provided as integers"}, 400

    # Range check (0–10)
    for v in (b1, b2, b3):
        if v < 0 or v > 10:
            return {"error": "Each biomarker must be between 0 and 10"}, 400

    # Save to sheet
    row = UserBiomarker(
        Date=TODAY(),
        Username=username,
        Biomarker1=b1,
        Biomarker2=b2,
        Biomarker3=b3,
    )
    row.save()
    return {"ok": True}, 201

# ---------- 6. Save daily summaries ----------
@bp.post("/summaries")
def summaries():
    data = request.get_json()
    row = UserSummarization(Date=TODAY(), **data)
    row.save()
    return {"status": "ok"}, 201

@bp.post("/meals/feedback")
def meal_feedback():
    data = request.get_json()
    append_row("UserMealPreferences", [
        dt.datetime.now().strftime("%Y-%m-%d"),
        data["Username"],
        data["MealCode"],
        str(bool(data.get("Like", False))).upper(),
        str(bool(data.get("Initial", False))).upper(),   # NEW COLUMN
    ])
    return {"status": "ok"}, 201

def _latest_summaries(username: str) -> tuple[str, str]:
    """Return (biomarker_summary, taste_profile). Empty strings if none."""
    vals = get_values("UserSummarization")
    if not vals:
        return "", ""
    header = vals[0]
    try:
        u_i = header.index("Username")
        bs_i = header.index("BiomarkerSummary")
        ps_i = header.index("PreferenceSummary")
    except ValueError:
        return "", ""

    rows = [r for r in vals[1:] if len(r) > u_i and r[u_i] == username]
    if not rows:
        return "", ""
    last = rows[-1]  # appended order ⇒ last is latest
    biomarker_summary = last[bs_i] if len(last) > bs_i else ""
    taste_profile = last[ps_i] if len(last) > ps_i else ""
    return biomarker_summary, taste_profile

def _user_goals(username: str) -> str:
    vals = get_values("UserPreferences")
    if not vals:
        return ""
    header = vals[0]
    try:
        u_i = header.index("Username")
        g_i = header.index("Goals")
    except ValueError:
        return ""
    row = next((r for r in vals[1:] if len(r) > u_i and r[u_i] == username), None)
    return (row[g_i] if row and len(row) > g_i else "") or ""

TODAY = lambda: dt.datetime.now().strftime("%Y-%m-%d")

@bp.post("/meals/daily")
def meals_daily():
    data = request.get_json(silent=True) or {}
    username = (data.get("Username") or "").strip()
    if not username:
        return {"error": "Username is required"}, 400

    # ---- Gather context for the LLM (with safe fallbacks) ----
    biomarker_summary, taste_profile = _latest_summaries(username)
    goals = _user_goals(username)

    # Even if summaries are empty, pass empty strings so LC has the keys
    try:
        meals_json_str = generate_daily_meals(
            context={
                "biomarker_summary": biomarker_summary or "",
                "taste_summary": taste_profile or "",   # <- expected key
                "user_goals": goals or "",              # <- expected key
            }
        )

    except Exception as e:
        # surface prompt/LLM errors clearly during dev
        return {"error": f"generate_daily_meals failed: {e}"}, 500

    # Parse the JSON the model returns
    try:
        meals = json.loads(meals_json_str) if isinstance(meals_json_str, str) else meals_json_str
    except Exception as e:
        return {"error": f"Model did not return valid JSON: {e}", "raw": meals_json_str}, 500

    # ---- Persist ingredients & steps for each meal type ----
    rows_ing: list[list] = []
    rows_steps: list[list] = []
    for meal_type in ("breakfast", "lunch", "dinner"):
        section = meals.get(meal_type, {}) or {}
        for slug, meta in section.items():
            # ingredients: dict item -> amount
            for ing, amt in (meta.get("ingredients") or {}).items():
                rows_ing.append([
                    TODAY(), username, meal_type.capitalize(), slug,
                    ing, str(amt), "llama", 0.7
                ])
            # steps: split gracefully (newlines preferred, then periods)
            instr = (meta.get("instructions") or "").replace("\r", "")
            raw_parts = [p.strip() for p in instr.split("\n") if p.strip()]
            parts = raw_parts if raw_parts else [p.strip() for p in instr.split(".") if p.strip()]
            for i, step in enumerate(parts, 1):
                rows_steps.append([
                    TODAY(), username, meal_type.capitalize(), slug,
                    i, step, "llama", 0.7
                ])

    if rows_ing:
        append_rows("MealIngredients", rows_ing)
    if rows_steps:
        append_rows("MealSteps", rows_steps)

    # Return structured JSON to the frontend
    return jsonify(meals), 200