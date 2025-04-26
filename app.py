import os

from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__)

# where your workbooks live
SHEETS_DIR = os.path.join(os.path.dirname(__file__), 'Sheets')

# fixed job‐sheet names
JOBS = ['ALC', 'ARM', 'BSM', 'CRP', 'CUL', 'GSM', 'LTW', 'WVR']


def list_worlds():
    """Scan Sheets/ for all * _Profits.xlsx and return world names."""
    files = [
        f for f in os.listdir(SHEETS_DIR)
        if f.endswith('_Profits.xlsx')
    ]
    # strip "_Profits.xlsx"
    return [f[:-len('_Profits.xlsx')] for f in sorted(files)]


@app.route('/')
def index():
    worlds = list_worlds()
    return render_template('index.html', worlds=worlds, jobs=JOBS)


@app.route('/data')
def data():
    world = request.args.get('world')
    job   = request.args.get('job')
    if not world or not job or job not in JOBS:
        return jsonify({'error': 'invalid parameters'}), 400

    path = os.path.join(SHEETS_DIR, f"{world}_Profits.xlsx")
    if not os.path.isfile(path):
        return jsonify({'error': 'world not found'}), 404

    # read just that sheet into a list of dicts
    try:
        df = pd.read_excel(path, sheet_name=job)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    records = df.fillna('').to_dict(orient='records')
    return jsonify(records)


if __name__ == '__main__':
    # for local dev; remove debug=True in production
    app.run(debug=True, port=5000)
