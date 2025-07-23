from flask import Flask, request, jsonify, send_from_directory
from googleapiclient.discovery import build
from google.oauth2 import service_account
import os, json

app = Flask(__name__)

# Load service account from Render environment
creds_dict = json.loads(os.environ['GOOGLE_APPLICATION_CREDENTIALS_JSON'])
creds = service_account.Credentials.from_service_account_info(
    creds_dict,
    scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
)
service = build('sheets', 'v4', credentials=creds)

# Google Sheets IDs & Ranges
PUTAWAYSHEET3_ID = "YOUR_SHEET3_ID"
PUTAWAYSHEET2_ID = "YOUR_SHEET2_ID"
RANGE3 = "Sheet1!A:B"  # UPC + Item Number
RANGE2 = "Sheet1!A:B"  # SKU + Putaway Location

def fetch_sheet(spreadsheet_id, range_name):
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])
    if not values:
        return []
    headers = values[0]
    data = [dict(zip(headers, row)) for row in values[1:]]
    return data

def load_and_merge():
    sheet3 = fetch_sheet(PUTAWAYSHEET3_ID, RANGE3)
    sheet2 = fetch_sheet(PUTAWAYSHEET2_ID, RANGE2)
    # Build lookup for putaway location by SKU
    location_lookup = {str(row.get('SKU', '')).strip().lower(): row.get('Putaway Location', '') for row in sheet2}
    merged = []
    for row in sheet3:
        sku = str(row.get('Item Number', '')).strip().lower()
        merged.append({
            "UPC": row.get('UPC', ''),
            "Item Number": row.get('Item Number', ''),
            "Putaway Location": location_lookup.get(sku, 'Not Found')
        })
    return merged

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '').lower().strip()
    data = load_and_merge()
    matches = []
    for row in data:
        upc = str(row.get('UPC', '')).lower()
        sku = str(row.get('Item Number', '')).lower()
        location = str(row.get('Putaway Location', '')).lower()
        if query in upc or query in sku or query in location:
            matches.append(row)
    return jsonify(matches)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)



