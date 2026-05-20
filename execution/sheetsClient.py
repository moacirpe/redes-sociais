#!/usr/bin/env python3
"""
Google Sheets client for reading/writing queue data.
Uses OAuth2 refresh token from .env.
"""

import os
import logging
from typing import List, Dict, Optional
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

load_dotenv()

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SHEET_ID_KEYS = {
    "moacir": "GOOGLE_SHEET_ID_MOACIR",
    "moper":  "GOOGLE_SHEET_ID_MOPER",
    "laika":  "GOOGLE_SHEET_ID_LAIKA",
    "namasa": "GOOGLE_SHEET_ID_NAMASA",
}

CSV_COLUMNS = [
    "id", "client", "platform", "scheduled_at", "caption",
    "media_filename", "status", "cloudinary_url", "ig_post_url",
    "generated_at", "published_at", "error",
]


def getCredentials() -> Credentials:
    creds = Credentials(
        token=None,
        refresh_token=os.getenv("GOOGLE_REFRESH_TOKEN"),
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return creds


def getSheetId(client: str) -> str:
    key = SHEET_ID_KEYS.get(client)
    if not key:
        raise ValueError(f"Cliente desconhecido: {client}")
    sheet_id = os.getenv(key)
    if not sheet_id:
        raise EnvironmentError(f"{key} não encontrado no .env. Execute setupGoogleSheets.py primeiro.")
    return sheet_id


def getService():
    return build("sheets", "v4", credentials=getCredentials())


def readRows(client: str) -> List[Dict]:
    """Read all rows from client's sheet. Returns list of dicts."""
    service    = getService()
    sheet_id   = getSheetId(client)
    result     = service.spreadsheets().values().get(
        spreadsheetId=sheet_id, range="queue!A1:L"
    ).execute()
    values = result.get("values", [])
    if len(values) < 2:
        return []
    headers = values[0]
    rows = []
    for row in values[1:]:
        padded = row + [""] * (len(headers) - len(row))
        rows.append(dict(zip(headers, padded)))
    return rows


def appendRows(client: str, rows: List[Dict]):
    """Append rows to client's sheet."""
    service  = getService()
    sheet_id = getSheetId(client)
    values   = [[row.get(col, "") for col in CSV_COLUMNS] for row in rows]
    service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range="queue!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": values},
    ).execute()


def updateRow(client: str, row_index: int, row: Dict):
    """Update a single row by 0-based index (excluding header). row_index=0 → row 2."""
    service    = getService()
    sheet_id   = getSheetId(client)
    sheet_row  = row_index + 2
    values     = [[row.get(col, "") for col in CSV_COLUMNS]]
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=f"queue!A{sheet_row}:L{sheet_row}",
        valueInputOption="RAW",
        body={"values": values},
    ).execute()


def writeAllRows(client: str, rows: List[Dict]):
    """Overwrite all data rows (keeps header)."""
    service  = getService()
    sheet_id = getSheetId(client)
    values   = [[row.get(col, "") for col in CSV_COLUMNS] for row in rows]
    service.spreadsheets().values().clear(
        spreadsheetId=sheet_id, range="queue!A2:L"
    ).execute()
    if values:
        service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range="queue!A2",
            valueInputOption="RAW",
            body={"values": values},
        ).execute()
