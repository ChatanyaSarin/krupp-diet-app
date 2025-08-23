# backend/sheets_client.py
from __future__ import annotations
from typing import Any, List, Tuple, Optional, Dict
import os
import gspread
from google.oauth2.service_account import Credentials
from gspread.utils import rowcol_to_a1

# ---- CONFIG ----
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID", "16XTW3RelaEbkubvk7OXP8_EcKx05Pmd8LdHEM5Gs-Cc")
CREDS_FILE = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "backend/credentials.json")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Authorize once and reuse
_creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
_gc = gspread.authorize(_creds)
_sheet = _gc.open_by_key(SPREADSHEET_ID)

def _ws(tab: str):
    """Get worksheet by exact title."""
    return _sheet.worksheet(tab)

# -------- Basic ops (API compatible with your existing code) --------
def get_values(tab: str) -> List[List[str]]:
    """Return all values, including header row. Empty cells come back as ''."""
    return _ws(tab).get_all_values()

def append_row(tab: str, values: List[Any]) -> None:
    _ws(tab).append_row(values, value_input_option="USER_ENTERED")

def append_rows(tab: str, rows: List[List[Any]]) -> None:
    if not rows:
        return
    _ws(tab).append_rows(rows, value_input_option="USER_ENTERED")

def update_row(tab: str, row_index: int, values: List[Any]) -> None:
    """row_index is 1-based including header (same as Google Sheets)."""
    ws = _ws(tab)
    # Update the exact range width of 'values'
    end_a1 = rowcol_to_a1(row_index, len(values)).split(":")[0]
    rng = f"A{row_index}:{end_a1[1:]}" if ":" in end_a1 else f"A{row_index}:{end_a1}"
    ws.update(rng, [values], value_input_option="USER_ENTERED")

def batch_get(tabs: List[str]) -> Dict[str, List[List[str]]]:
    """Fetch multiple tabs' values as a dict {tab: values}."""
    # gspread batch_get takes A1 ranges; map titles to "'Tab'!A1:Z"
    ranges = [f"'{t}'!A1:Z" for t in tabs]
    results = _sheet.values_batch_get(ranges=ranges)["valueRanges"]
    out: Dict[str, List[List[str]]] = {}
    for r in results:
        # r["range"] looks like 'Users'!A1:Z
        tab = r["range"].split("!")[0].strip("'")
        out[tab] = r.get("values", [])
    return out

def find_row_by_header_value(tab: str, header_name: str, value: str) -> Tuple[Optional[int], Optional[List[str]], List[str]]:
    """Return (row_index, row_values, header_row). row_index is 1-based."""
    rows = get_values(tab)
    if not rows:
        return None, None, []
    header = rows[0]
    if header_name not in header:
        return None, None, header
    idx = header.index(header_name)
    for i, row in enumerate(rows[1:], start=2):
        if len(row) > idx and row[idx] == value:
            return i, row, header
    return None, None, header

def append_rows(tab: str, rows: List[List[Any]]) -> None:
    """Append multiple rows in one API call.
    Each inner list is a row aligned to your header order."""
    if not rows:
        return
    _ws(tab).append_rows(rows, value_input_option="USER_ENTERED")