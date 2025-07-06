import datetime as dt
from typing import Any, List, Dict

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "16XTW3RelaEbkubvk7OXP8_EcKx05Pmd8LdHEM5Gs-Cc"

# ---------- AUTH ----------
creds = Credentials.from_service_account_file(
    "backend/credentials.json", scopes=SCOPES
)
service = build("sheets", "v4", credentials=creds)
sheet_api = service.spreadsheets()


# ---------- UTILS ----------
def append_row(tab: str, values: List[Any]) -> None:
    sheet_api.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{tab}!A1",
        valueInputOption="USER_ENTERED",
        body={"values": [values]},
    ).execute()

def append_rows(tab: str, rows: List[List[Any]]) -> None:
    """Append many rows in ONE request."""
    sheet_api.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{tab}!A1",
        valueInputOption="USER_ENTERED",
        body={"values": rows},
    ).execute()


def batch_get(tabs: List[str]) -> Dict[str, List[List[str]]]:
    res = (
        sheet_api.values()
        .batchGet(spreadsheetId=SPREADSHEET_ID, ranges=[f"{t}!A1:Z" for t in tabs])
        .execute()
    )
    out = {}
    for rng in res["valueRanges"]:
        tab = rng["range"].split("!")[0]
        out[tab] = rng.get("values", [])
    return out


def upsert_by_key(
    tab: str, header: List[str], key_idx: int, key_val: str, row_values: List[Any]
) -> None:
    """Overwrite row where header[key_idx] == key_val, else append."""
    rows = sheet_api.values().get(
        spreadsheetId=SPREADSHEET_ID, range=f"{tab}!A2:Z"
    ).execute().get("values", [])

    for i, row in enumerate(rows, start=2):  # offset 1 for header
        if len(row) > key_idx and row[key_idx] == key_val:
            sheet_api.values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f"{tab}!A{i}",
                valueInputOption="USER_ENTERED",
                body={"values": [row_values]},
            ).execute()
            return
    append_row(tab, row_values)
