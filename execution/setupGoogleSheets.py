#!/usr/bin/env python3
"""
Cria as planilhas de fila no Google Drive e salva os IDs no .env.

Uso:
    python execution/setupGoogleSheets.py
"""

import os
import re
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

CLIENTS = ["moacir", "moper", "laika"]

CSV_HEADERS = [
    "id", "client", "platform", "scheduled_at", "caption",
    "media_filename", "status", "cloudinary_url", "ig_post_url",
    "generated_at", "published_at", "error"
]


def getCredentials():
    return Credentials(
        token=None,
        refresh_token=os.getenv("GOOGLE_REFRESH_TOKEN"),
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )


def createSheet(sheets_service, drive_service, client: str) -> str:
    """Cria planilha para o cliente e retorna o spreadsheet ID."""
    spreadsheet = {
        "properties": {"title": f"Fila de Posts — {client}"},
        "sheets": [{"properties": {"title": "queue"}}],
    }
    result = sheets_service.spreadsheets().create(body=spreadsheet).execute()
    spreadsheet_id = result["spreadsheetId"]
    sheet_id = result["sheets"][0]["properties"]["sheetId"]

    # Adicionar cabeçalhos
    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="queue!A1",
        valueInputOption="RAW",
        body={"values": [CSV_HEADERS]},
    ).execute()

    # Formatar cabeçalho (negrito + fundo cinza)
    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": [{
            "repeatCell": {
                "range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 1},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.2, "green": 0.2, "blue": 0.2},
                        "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat)",
            }
        }]},
    ).execute()

    # Tornar pública para leitura (qualquer um com link pode ver)
    drive_service.permissions().create(
        fileId=spreadsheet_id,
        body={"type": "anyone", "role": "reader"},
    ).execute()

    print(f"  ✅ {client}: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
    return spreadsheet_id


def saveSheetIds(sheet_ids: dict):
    """Salva os IDs das planilhas no .env."""
    env_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    with open(env_path, "r", encoding="utf-8") as f:
        content = f.read()

    for client, sheet_id in sheet_ids.items():
        key = f"GOOGLE_SHEET_ID_{client.upper()}"
        if key in content:
            content = re.sub(f"^{key}=.*$", f"{key}={sheet_id}", content, flags=re.MULTILINE)
        else:
            content += f"\n{key}={sheet_id}"

    with open(env_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("\n✅ IDs salvos no .env")


def main():
    creds         = getCredentials()
    sheets_service = build("sheets", "v4", credentials=creds)
    drive_service  = build("drive",  "v3", credentials=creds)

    print("Criando planilhas no Google Drive...\n")
    sheet_ids = {}
    for client in CLIENTS:
        sheet_ids[client] = createSheet(sheets_service, drive_service, client)

    saveSheetIds(sheet_ids)
    print("\nAbra as planilhas no Google Sheets app no celular para aprovar posts.")


if __name__ == "__main__":
    main()
