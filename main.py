from flask import Flask, request, jsonify, send_from_directory
import pandas as pd

app = Flask(__name__)

# Google Sheets URLs
PUTAWAYSHEET3_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS8slYmMBaxGfOhQvSIvLPobwcX6OGWTRP8xk0uulGkSD9A_b_8cy-xXV16zbiqZBGkhpycfGAOHYug/pub?output=csv"
PUTAWAYSHEET2_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQKJoXBk7b3ULmRa7s_21tJRahYrSjCIdIIhVeQWy07KllIRPFm8pbd2B43pr9DKnRQBMyZUE_N7W85/pub?output=csv"

def load_putawaysheet3():
    return pd.read_csv(PUTAWAYSHEET3_URL).to_dict(orient="records")

def load_putawaysheet2():
    return pd.read_csv(PUTAWAYSHEET2_URL).to_dict(orient="records")

def find_putaway_location(upc, sheet2_data):
    for row in sheet2_data:
        if upc in str(row.get('SKU', '')).lower():
            return row.get('Putaway Location', 'Not Found')
    return "Not Found"

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '').lower().strip()
    matches = []

    data3 = load_putawaysheet3()
    data2 = load_putawaysheet2()

    # Search Sheet 3 (UPC + Item Number)
    for row in data3:
        upc = str(row.get('UPC', '')).strip().lower()
        item_number = str(row.get('Item Number', '')).strip().lower()
        if query in upc or query in item_number:
            matches.append({
                "sheet": "Putaway Sheet 3",
                "name": row.get('Item Number', ''),
                "upc": row.get('UPC', ''),
                "location": find_putaway_location(upc, data2)
            })

    # Search Sheet 2 (SKU + Putaway Location)
    for row in data2:
        sku = str(row.get('SKU', '')).strip().lower()
        if query in sku:
            matches.append({
                "sheet": "Putaway Sheet 2",
                "name": row.get('SKU', ''),
                "upc": row.get('SKU', ''),
                "location": row.get('Putaway Location', '')
            })

    return jsonify(matches)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)


