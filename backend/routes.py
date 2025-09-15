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

def _safe_json() -> dict:
    """
    Parse JSON from the request body *very* defensively:
    - try Flask's parser (force=True to ignore mimetype)
    - fall back to raw body
    - always return a dict
    """
    data = request.get_json(force=True, silent=True)
    if isinstance(data, dict):
        return data
    raw = request.get_data(cache=False, as_text=True) or ""
    if raw:
        try:
            j = json.loads(raw)
            if isinstance(j, dict):
                return j
        except Exception:
            pass
    return {}

def _extract_username(data: dict) -> str:
    # Try body first
    for k in ("Username", "username", "user", "name"):
        v = data.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    # Then querystring as a backup
    v = request.args.get("Username") or request.args.get("username") or ""
    return v.strip()

# ---------- Summaries: collect + run ----------

from collections import defaultdict

# POST /auth/login
@bp.route("/auth/login", methods=["POST"], strict_slashes=False)
def auth_login():
    data = request.get_json(silent=True) or {}

    def as_str(x):
        if x is None: return ""
        if isinstance(x, dict) and "value" in x: return str(x["value"])
        return str(x)

    username = as_str(data.get("username")).strip()
    password = as_str(data.get("password"))

    if not username:
        return {"error": "username required"}, 400

    row_idx, row, header = find_row_by_header_value("Users", "Username", username)
    if row is None:
        return jsonify({"error": "user not found"}), 404

    ph_i = header.index("PasswordHash")
    pwd_hash = row[ph_i] if len(row) > ph_i else ""

    if not pwd_hash:
        return jsonify({"needsPassword": True}), 409

    if not bcrypt.check_password_hash(pwd_hash, password):
        return jsonify({"error": "bad credentials"}), 401

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
    req = _safe_json()
    username = _extract_username(req)
    if not username:
        return {"error": "Username is required"}, 400

    # ----- read UserPreferences safely -----
    vals = get_values("UserPreferences")  # [['Username','Height','Weight','DietaryRestrictions', ...], [..], ...]
    if not vals:
        return jsonify({"error": "UserPreferences tab is empty or missing"}), 400

    header = vals[0]
    def idx(col): 
        try: return header.index(col)
        except ValueError: return None

    u_i = idx("Username"); h_i = idx("Height"); w_i = idx("Weight")
    dr_i = idx("DietaryRestrictions")

    if None in (u_i, h_i, w_i, dr_i):
        return jsonify({"error": f"UserPreferences header must include "
                                 f"[Username, Height, Weight, DietaryRestrictions, CreatedAt]. "
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

    restrictions = [s.strip() for s in (row[dr_i] if dr_i is not None and len(row) > dr_i else "").split(",") if s.strip()]

    # ----- call LLM -----
    meals = generate_initial_meals(
        user_profile={
            "height": height,
            "weight": weight,
            "dietary_restrictions": restrictions,
        }
    )

    # ----- persist ingredients & steps in batches -----
    rows_ing, rows_steps = [], []
    for slug, meta in meals.items():
        desc = (meta.get("description") or "").strip()
        for ing, amt in meta["ingredients"].items():
            rows_ing.append([
                TODAY(), username, "Initial", slug,
                desc, ing, amt, "llama", 0.7  # DESCRIPTION inserted
            ])
        raw = meta["instructions"].replace("\r", "").split("\n")
        parts = [p for p in raw if p.strip()] or [s for s in meta["instructions"].split(".") if s.strip()]
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
        b1 = _geti("Mood", "Mood", "b1")
        b2 = _geti("Energy", "Energy", "b2")
        b3 = _geti("Fullness", "Fullness", "b3")
    except (KeyError, ValueError):
        return {"error": f"Biomarkers must be provided as integers, {data}"}, 400

    # Range check (0–10)
    for v in (b1, b2, b3):
        if v < 0 or v > 10:
            return {"error": "Each biomarker must be between 0 and 10"}, 400

    # Save to sheet
    row = UserBiomarker(
        Date=TODAY(),
        Username=username,
        Mood=b1,
        Energy=b2,
        Fullness=b3,
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

@bp.post("/meals/ingredients")
def meals_ingredients():
    """
    Body: {
      "Username": "alice",
      "MealCodes": ["burrito-bowl", "tofu-scramble", "pasta-primavera"]
    }

    Returns grouped details for the latest entry per code:
    {
      "breakfast": {
        "tofu-scramble": {
          "description": "...",
          "ingredients": { "tofu": "200g", "spinach": "1 cup", ... },
          "steps": ["...", "..."]  # optional
        }
      },
      "lunch": { ... },
      "dinner": { ... }
    }
    """
    data = request.get_json(silent=True) or {}
    username = (data.get("Username") or data.get("username") or "").strip()
    meal_codes = data.get("MealCodes") or []
    if not username:
        return {"error": "Username is required"}, 400
    if not isinstance(meal_codes, list) or not meal_codes:
        return {"error": "MealCodes must be a non-empty list"}, 400

    from datetime import datetime
    def parse_date(s):
        try: return datetime.strptime(s, "%Y-%m-%d").date()
        except Exception: return None

    # ---------- INGREDIENTS ----------
    rows = get_values("MealIngredients")
    out = {"breakfast": {}, "lunch": {}, "dinner": {}}
    if not rows:
        return jsonify(out), 200

    hdr = rows[0]
    def col(name):
        try: return hdr.index(name)
        except ValueError: return None

    d_i  = col("Date")
    u_i  = col("Username")
    t_i  = col("MealType")
    c_i  = col("MealCode")
    desc_i = col("Description")
    ing_i  = col("Ingredients")
    amt_i  = col("Amount")

    target_codes = set(map(str, meal_codes))

    # Track latest date per code
    latest_date_per_code = {}  # code -> date
    # Aggregate by (code, date)
    by_code_date = {}  # (code, date_iso) -> { meal_type, description, ingredients{} }

    for r in rows[1:]:
        if any(x is None for x in (d_i,u_i,t_i,c_i,ing_i,amt_i,desc_i)): 
            continue
        if len(r) <= max(d_i,u_i,t_i,c_i,ing_i,amt_i,desc_i): 
            continue
        if r[u_i] != username: 
            continue
        code = r[c_i]
        if code not in target_codes: 
            continue
        d = parse_date(r[d_i])
        if not d: 
            continue

        # keep only latest date per code
        if (code not in latest_date_per_code) or (d > latest_date_per_code[code]):
            latest_date_per_code[code] = d

        key = (code, d.isoformat())
        if key not in by_code_date:
            by_code_date[key] = {
                "meal_type": (r[t_i] or "").strip().lower(),
                "description": (r[desc_i] or "").strip(),
                "ingredients": {}
            }
        ing = str(r[ing_i]).strip()
        amt = str(r[amt_i]).strip()
        if ing:
            by_code_date[key]["ingredients"][ing] = amt

    # ---------- STEPS (optional but recommended) ----------
    steps_rows = get_values("MealSteps")
    steps_by_key = {}  # (code, date_iso) -> [steps...]

    if steps_rows:
        sh = steps_rows[0]
        def scol(name):
            try: return sh.index(name)
            except ValueError: return None

        sd_i = scol("Date")
        su_i = scol("Username")
        st_i = scol("MealType")
        sc_i = scol("MealCode")
        step_i = scol("Step")
        instr_i = scol("Instruction")

        for r in steps_rows[1:]:
            if any(x is None for x in (sd_i, su_i, st_i, sc_i, step_i, instr_i)):
                continue
            if len(r) <= max(sd_i, su_i, st_i, sc_i, step_i, instr_i):
                continue
            if r[su_i] != username:
                continue
            code = r[sc_i]
            if code not in target_codes:
                continue
            d = parse_date(r[sd_i])
            if not d:
                continue

            # we only care about steps on the latest date for that code
            if code not in latest_date_per_code or d != latest_date_per_code[code]:
                continue

            key = (code, d.isoformat())
            steps_by_key.setdefault(key, [])
            txt = str(r[instr_i]).strip()
            if txt:
                steps_by_key[key].append((int(r[step_i]) if str(r[step_i]).isdigit() else 9999, txt))

    # ---------- Build final output ----------
    for code, latest in latest_date_per_code.items():
        key = (code, latest.isoformat())
        agg = by_code_date.get(key)
        if not agg:
            continue
        sec = agg["meal_type"] if agg["meal_type"] in out else "lunch"
        item = {
            "description": agg["description"],
            "ingredients": agg["ingredients"],
        }
        # attach steps if we found any
        if key in steps_by_key:
            # sort by step number if present
            steps_sorted = [txt for _, txt in sorted(steps_by_key[key], key=lambda x: x[0])]
            item["steps"] = steps_sorted
        out[sec][code] = item

    return jsonify(out), 200


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

TODAY = lambda: dt.datetime.now().strftime("%Y-%m-%d")

@bp.post("/meals/daily")
def meals_daily():
    data = _safe_json()
    username = _extract_username(data)
    if not username:
        return {"error": "Username is required"}, 400

    # 1) Try to use existing summaries
    biomarker_summary, taste_profile = _latest_summaries(username)

    # 2) If either is missing, compute now and write to sheet
    computed_any = False
    if not biomarker_summary or not taste_profile:
        window_days = int(data.get("window_days", 7) or 7)
        biomarker_window = _collect_recent_biomarkers(username, window_days)
        meals_json       = _collect_recent_meals_json(username, window_days)
        liked, disliked  = _collect_recent_likes(username, window_days)

        # Compute biomarker summary if missing
        if not biomarker_summary:
            try:
                biomarker_summary = update_biomarker_summary(payload={
                    "existing_summary":  "",
                    "biomarker_journal": json.dumps(biomarker_window or []),
                    "meals_last_period": json.dumps(meals_json or {}),
                })
                if not isinstance(biomarker_summary, str):
                    biomarker_summary = str(biomarker_summary)
                computed_any = True
            except Exception:
                biomarker_summary = "No recent biomarker data; default to balanced meals, steady energy, and moderate sodium."

        # Compute taste/Preference summary if missing
        if not taste_profile:
            try:
                taste_profile = update_taste_summary(data={
                    "existing_summary": "",
                    "liked_meals":     ", ".join(liked) if liked else "",
                    "disliked_meals":  ", ".join(disliked) if disliked else "",
                })
                if not isinstance(taste_profile, str):
                    taste_profile = str(taste_profile)
                computed_any = True
            except Exception:
                taste_profile = "No strong preferences recorded; include variety, moderate spice, and familiar flavors."

        # If we computed anything, persist a row so future calls are warm
        if computed_any:
            append_row("UserSummarization", [TODAY(), username, taste_profile, biomarker_summary, "llama", 0.7])

    # 3) Profile fields
    restrictions = _user_restrictions(username) or []

    # 4) Build LLM context with ALL keys your prompt expects
    payload_context = {
        "biomarker_summary":    biomarker_summary or "No recent biomarker data.",
        "taste_summary":        taste_profile or "No strong preferences recorded.",
        "dietary_restrictions": restrictions,
    }

    # 5) Generate meals
    meals_json_str = generate_daily_meals(context=payload_context)
    try:
        meals = json.loads(meals_json_str) if isinstance(meals_json_str, str) else meals_json_str
    except Exception as e:
        return {"error": f"Model did not return valid JSON: {e}", "raw": meals_json_str}, 500

    # 6) Persist to MealIngredients & MealSteps (with Description)
    rows_ing, rows_steps = [], []
    for meal_type in ("breakfast", "lunch", "dinner"):
        section = meals.get(meal_type, {}) or {}
        for slug, meta in section.items():
            desc = (meta.get("description") or "").strip()
            # ingredients
            for ing, amt in (meta.get("ingredients") or {}).items():
                rows_ing.append([
                    TODAY(), username, meal_type.capitalize(), slug,
                    desc, ing, str(amt), "llama", 0.7
                ])
            # steps
            instr = (meta.get("instructions") or "").replace("\r", "")
            parts = [p.strip() for p in instr.split("\n") if p.strip()] or \
                    [p.strip() for p in instr.split(".") if p.strip()]
            for i, step in enumerate(parts, 1):
                rows_steps.append([
                    TODAY(), username, meal_type.capitalize(), slug,
                    i, step, "llama", 0.7
                ])

    if rows_ing:   append_rows("MealIngredients", rows_ing)
    if rows_steps: append_rows("MealSteps", rows_steps)

    return jsonify(meals), 200

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
        m = defaultdict(lambda: {"long_name": "", "ingredients": defaultdict(str), "instructions": []})
        for r in rows[1:]:
            if any(idx[k] is None or len(r) <= idx[k] for k in idx): continue
            if r[idx["Username"]] != username: continue
            d = _parse_date(r[idx["Date"]]); 
            if not d or (today - d).days > window_days: continue
            code = r[idx["MealCode"]]
            if is_ing:
                ing, amt = r[idx["Ingredients"]], str(r[idx["Amount"]])
                if not isinstance(m[code]["ingredients"], dict):
                    m[code]["ingredients"] = {}
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
        ingredients_obj = m_ing.get(code, {}).get("ingredients", {})
        ings = dict(ingredients_obj) if isinstance(ingredients_obj, (dict, defaultdict)) else {}
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
    username = (data.get("Username") or data.get("username") or "").strip()
    window_days = int(data.get("window_days", 7) or 7)
    if not username:
        return {"error": "Username is required"}, 400

    # prior summaries (if any)
    old_bio, old_taste = _latest_summaries(username)

    # fresh windowed data
    biomarker_window = _collect_recent_biomarkers(username, window_days)  # list[dict]
    meals_json       = _collect_recent_meals_json(username, window_days)  # dict[code]->obj
    liked, disliked  = _collect_recent_likes(username, window_days)

    # NOTE: use the arg names your workflow expects
    try:
        new_bio = update_biomarker_summary(payload={
            "existing_summary":   old_bio or "",
            "biomarker_journal":  json.dumps(biomarker_window or []),
            "meals_last_period":  json.dumps(meals_json or {}),
        })
        if not isinstance(new_bio, str):
            new_bio = str(new_bio)
    except Exception as e:
        return {"error": f"update_biomarker_summary failed: {e}"}, 500

    try:
        new_taste = update_taste_summary(data={
            "existing_summary": old_taste or "",
            "liked_meals":     ", ".join(liked) if liked else "",
            "disliked_meals":  ", ".join(disliked) if disliked else "",
        })
        if not isinstance(new_taste, str):
            new_taste = str(new_taste)
    except Exception as e:
        return {"error": f"update_taste_summary failed: {e}"}, 500

    append_row("UserSummarization", [TODAY(), username, new_taste, new_bio, "llama", 0.7])
    return {"ok": True}, 201

def _user_restrictions(username: str):
    vals = get_values("UserPreferences")
    if not vals:
        return []
    header = vals[0]
    try:
        u_i = header.index("Username")
        r_i = header.index("DietaryRestrictions")
    except ValueError:
        return []
    row = next((r for r in vals[1:] if len(r) > u_i and r[u_i] == username), None)
    raw = (row[r_i] if row and len(row) > r_i else "") or ""
    # return as list
    return [s.strip() for s in raw.split(",") if s.strip()]
