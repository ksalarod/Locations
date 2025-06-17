
from flask import Flask, request, jsonify, send_from_directory
import pandas as pd

app = Flask(__name__, static_url_path='')

df = pd.read_csv('items_merged.csv')
df.fillna('', inplace=True)

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    matches = []

    for _, row in df.iterrows():
        if query in str(row['barcode']).lower() or query in str(row['name']).lower():
            matches.append({
                "name": row['name'],
                "location": row['location']
            })

    return jsonify(matches)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
