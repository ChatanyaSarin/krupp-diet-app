# backend/models.py
from __future__ import annotations

from dataclasses import dataclass, field
import datetime as dt
from typing import Any, List

from sheets_client import (
    append_row,
    update_row,
    find_row_by_header_value,
)

# ----------------------- helpers -----------------------

def now_ts() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def b2s(b: bool) -> str:
    return "TRUE" if bool(b) else "FALSE"


# -------------------- USER PREFERENCES --------------------

@dataclass
class UserPreferences:
    Username: str
    Height: int
    Weight: int
    DietaryRestrictions: str
    CreatedAt: str = field(default_factory=now_ts)

    # MUST match header row in the 'UserPreferences' tab
    HEADER = [
        "Username",
        "Height",
        "Weight",
        "DietaryRestrictions",
        "CreatedAt",
    ]

    def to_row(self) -> List[Any]:
        return [
            self.Username,
            int(self.Height),
            int(self.Weight),
            self.DietaryRestrictions,
            self.CreatedAt,
        ]

    def save(self) -> None:
        """
        Upsert by Username:
        - If Username exists in UserPreferences, update that row (preserve CreatedAt if already set).
        - Otherwise append a new row.
        """
        row_idx, row, header = find_row_by_header_value("UserPreferences", "Username", self.Username)

        # ensure row aligns to header length
        values = self.to_row()
        if row_idx is None:
            append_row("UserPreferences", values)
            return

        # preserve existing CreatedAt if present
        try:
            ca_i = header.index("CreatedAt")
            if len(row) > ca_i and row[ca_i]:
                values[ca_i] = row[ca_i]
        except ValueError:
            pass

        update_row("UserPreferences", row_idx, values)


# ---------------------- MEAL FEEDBACK ----------------------

@dataclass
class UserMealPreference:
    Date: str
    Username: str
    MealCode: str
    Like: bool
    Initial: bool  # NEW: TRUE if initial suggestion; FALSE if daily

    # MUST match header row in 'UserMealPreferences'
    HEADER = ["Date", "Username", "MealCode", "Like", "Initial"]

    def to_row(self) -> List[Any]:
        return [
            self.Date,
            self.Username,
            self.MealCode,
            b2s(self.Like),
            b2s(self.Initial),
        ]

    def save(self) -> None:
        append_row("UserMealPreferences", self.to_row())


# ---------------------- USER BIOMARKER ----------------------

@dataclass
class UserBiomarker:
    Date: str
    Username: str
    Mood: int
    Energy: int
    Fullness: int

    # MUST match header row in 'UserBiomarker'
    HEADER = [
        "Date", 
        "Username", 
        "Mood", 
        "Energy", 
        "Fullness"
    ]

    def to_row(self) -> List[Any]:
        return [
            self.Date,
            self.Username,
            int(self.Mood),
            int(self.Energy),
            int(self.Fullness),
        ]

    def save(self) -> None:
        append_row("UserBiomarker", self.to_row())


# ---------------------- MEAL INGREDIENTS ----------------------

@dataclass
class MealIngredientRow:
    Date: str
    Username: str
    MealType: str       # Breakfast | Lunch | Dinner | Initial
    MealCode: str
    Ingredient: str
    Amount: str         # keep as string (e.g., "1 cup", "200 g")
    Model: str
    Temperature: float

    # MUST match header row in 'MealIngredients'
    HEADER = [
        "Date",
        "Username",
        "MealType",
        "MealCode",
        "Ingredients",
        "Amount",
        "Model",
        "Temperature",
    ]

    def to_row(self) -> List[Any]:
        return [
            self.Date,
            self.Username,
            self.MealType,
            self.MealCode,
            self.ingredient_cell(),
            self.Amount,
            self.Model,
            self.Temperature,
        ]

    def ingredient_cell(self) -> str:
        # In case you ever normalize naming to singular "Ingredient"
        return self.Ingredient

    def save(self) -> None:
        append_row("MealIngredients", self.to_row())


# ------------------------- MEAL STEPS -------------------------

@dataclass
class MealStepRow:
    Date: str
    Username: str
    MealType: str
    MealCode: str
    Step: int
    Instruction: str
    Model: str
    Temperature: float

    # MUST match header row in 'MealSteps'
    HEADER = [
        "Date",
        "Username",
        "MealType",
        "MealCode",
        "Step",
        "Instruction",
        "Model",
        "Temperature",
    ]

    def to_row(self) -> List[Any]:
        return [
            self.Date,
            self.Username,
            self.MealType,
            self.MealCode,
            int(self.Step),
            self.Instruction,
            self.Model,
            self.Temperature,
        ]

    def save(self) -> None:
        append_row("MealSteps", self.to_row())


# ---------------------- USER SUMMARIZATION ----------------------

@dataclass
class UserSummarization:
    Date: str
    Username: str
    PreferenceSummary: str
    BiomarkerSummary: str
    Model: str
    Temperature: float

    # MUST match header row in 'UserSummarization'
    HEADER = [
        "Date",
        "Username",
        "PreferenceSummary",
        "BiomarkerSummary",
        "Model",
        "Temperature",
    ]

    def to_row(self) -> List[Any]:
        return [
            self.Date,
            self.Username,
            self.PreferenceSummary,
            self.BiomarkerSummary,
            self.Model,
            self.Temperature,
        ]

    def save(self) -> None:
        append_row("UserSummarization", self.to_row())
