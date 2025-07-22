from flask import Flask, request, jsonify, send_from_directory
import pandas as pd # <--- Add this

app = Flask(__name__)

# Google Sheets URLs
PUTAWAYSHEET3_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS8slYmMBaxGfOhQvSIvLPobwcX6OGWTRP8xk0uulGkSD9A_b_8cy-xXV16zbiqZBGkhpycfGAOHYug/pub?output=csv"
PUTAWAYSHEET2_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQKJoXBk7b3ULmRa7s_21tJRahYrSjCIdIIhVeQWy07KllIRPFm8pbd2B43pr9DKnRQBMyZUE_N7W85/pub?output=csv"

# Load functions
def load_putawaysheet3():
return pd.read_csv(PUTAWAYSHEET3_URL).to_dict(orient="records")

def load_putawaysheet2():
return pd.read_csv(PUTAWAYSHEET2_URL).to_dict(orient="records")

@app.route('/')
def home():
return send_from_directory('.', 'index.html')

@app.route('/search')
def search():
query = request.args.get('q', '').lower()
matches = []

# You can switch to sheet 2 or 3 as needed
data = load_putawaysheet3() # or load_putawaysheet2()

for row in data:
if query in str(row.get('barcode', '')).lower() or query in str(row.get('name', '')).lower():
matches.append({
"name": row.get('name', ''),
"location": row.get('location', '')
})

return jsonify(matches)

if __name__ == '__main__':
app.run(host='0.0.0.0', port=81)
