from flask import Flask, request, jsonify, send_from_directory
from googleapiclient.discovery import build
from google.oauth2 import service_account
import os, json, sys

app = Flask(__name__)

# Load service account from environment
try:
    creds_dict = json.loads(os.environ['GOOGLE_APPLICATION_CREDENTIALS_JSON'])
    creds = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
    )
    service = build('sheets', 'v4', credentials=creds)
    print("Google Sheets API authenticated successfully.")
except KeyError:
    print("ERROR: GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable not set.")
    sys.exit(1)
except Exception as e:
    print("ERROR: Failed to authenticate with Google Sheets API:", e)
    sys.exit(1)

# Replace with your actual IDs and tab names!
PUTAWAYSHEET3_ID = "1q158TnWdpjpY2fZ_e5TVPADNlLvn37pp5468kI_lbCI"
PUTAWAYSHEET2_ID = "1Q9C-k6cbT7tNtgAd1Hs79tQ4BeE9g775Uxchnuu3t7g"
RANGE3 = "Sheet3!A:B"
RANGE2 = "Sheet2!A:B"

def fetch_sheet(spreadsheet_id, range_name):
    try:
        print(f"Fetching spreadsheet: {spreadsheet_id} | Range: {range_name}")
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        values = result.get('values', [])
        print(f"Fetched {len(values)} rows from {spreadsheet_id}.")
        if not values:
            print("WARNING: No data returned. Check sheet sharing or range name.")
            return []
        headers = values[0]
        data = [dict(zip(headers, row)) for row in values[1:]]
        return data
    except Exception as e:
        print(f"ERROR fetching sheet {spreadsheet_id}: {e}")
        return []

def load_and_merge():
    sheet3 = fetch_sheet(PUTAWAYSHEET3_ID, RANGE3)
    sheet2 = fetch_sheet(PUTAWAYSHEET2_ID, RANGE2)
    location_lookup = {str(row.get('SKU', '')).strip().lower(): row.get('Putaway Location', '') for row in sheet2}
    merged = []
    for row in sheet3:
        sku = str(row.get('Item Number', '')).strip().lower()
        merged.append({
            "UPC": row.get('UPC', ''),
            "Item Number": row.get('Item Number', ''),
            "Putaway Location": location_lookup.get(sku, 'Not Found')
        })
    print(f"Merged dataset: {len(merged)} items.")
    return merged

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/search')
def search():
    try:
        query = request.args.get('q', '').lower().strip()
        print(f"Search query: {query}")
        data = load_and_merge()
        matches = []
        for row in data:
            upc = str(row.get('UPC', '')).lower()
            sku = str(row.get('Item Number', '')).lower()
            location = str(row.get('Putaway Location', '')).lower()
            if query in upc or query in sku or query in location:
                matches.append(row)
        print(f"Matches found: {len(matches)}")
        return jsonify(matches)
    except Exception as e:
        print("ERROR in /search:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)




