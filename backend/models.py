from dataclasses import dataclass
import datetime as dt
from typing import List

from sheets_client import append_row, upsert_by_key

# ---------- USER PREFERENCES ----------
@dataclass
class UserPreferences:
    Username: str
    Height: int
    Weight: int
    Goals: str
    DietaryRestrictions: str
    CreatedAt: str = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    HEADER = [
        "Username",
        "Height",
        "Weight",
        "Goals",
        "DietaryRestrictions",
        "CreatedAt",
    ]

    def save(self):
        upsert_by_key(
            "UserPreferences", self.HEADER, 0, self.Username, self.to_row()
        )

    def to_row(self):
        return [
            self.Username,
            self.Height,
            self.Weight,
            self.Goals,
            self.DietaryRestrictions,
            self.CreatedAt,
        ]


# ---------- MEAL FEEDBACK ----------
@dataclass
class UserMealPreference:
    Date: str
    Username: str
    MealCode: str
    Like: bool

    HEADER = ["Date", "Username", "MealCode", "Like"]

    def save(self):
        append_row("UserMealPreferences", self.to_row())

    def to_row(self):
        return [self.Date, self.Username, self.MealCode, str(self.Like).upper()]

@dataclass
class UserBiomarker:
    Date: str
    Username: str
    Biomarker1: int
    Biomarker2: int
    Biomarker3: int

    HEADER = ["Date", "Username", "BIOMARKER 1", "BIOMARKER 2", "BIOMARKER 3"]

    def save(self):
        append_row("UserBiomarker", self.to_row())

    def to_row(self):
        return [self.Date, self.Username, self.Biomarker1,
                self.Biomarker2, self.Biomarker3]


@dataclass
class MealIngredientRow:
    Date: str
    Username: str
    MealType: str       # Breakfast | Lunch | Dinner | Initial
    MealCode: str
    Ingredient: str
    Amount: str
    Model: str
    Temperature: float

    HEADER = ["Date", "Username", "MealType", "MealCode",
              "Ingredients", "Amount", "Model", "Temperature"]

    def save(self):
        append_row("MealIngredients", self.to_row())

    def to_row(self):
        return [self.Date, self.Username, self.MealType, self.MealCode,
                self.Ingredient, self.Amount, self.Model, self.Temperature]


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

    HEADER = ["Date", "Username", "MealType", "MealCode",
              "Step", "Instruction", "Model", "Temperature"]

    def save(self):
        append_row("MealSteps", self.to_row())

    def to_row(self):
        return [self.Date, self.Username, self.MealType, self.MealCode,
                self.Step, self.Instruction, self.Model, self.Temperature]


@dataclass
class UserSummarization:
    Date: str
    Username: str
    PreferenceSummary: str
    BiomarkerSummary: str
    Model: str
    Temperature: float

    HEADER = ["Date", "Username", "PreferenceSummary",
              "BiomarkerSummary", "Model", "Temperature"]

    def save(self):
        append_row("UserSummarization", self.to_row())

    def to_row(self):
        return [self.Date, self.Username, self.PreferenceSummary,
                self.BiomarkerSummary, self.Model, self.Temperature]
