print("Starting Script")

import gspread
from google.oauth2.service_account import Credentials

print("Libraries Loaded")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_file(
    "kridai-500207-996276752b6b.json",
    scopes=SCOPES
)

print("Credentials Loaded")

client = gspread.authorize(creds)

print("Authorized")

sheet = client.open_by_key(
   #git log --oneline -5
   #  "1iZudgyP1oG_zxnK65Z1Gsu8B189QA95ly--tCQNHIxo"
).sheet1

print("Connected Successfully!")

print(sheet.get_all_records())