import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from database import init_db, get_attendance_summary, save_prediction_records, get_prediction_history, get_cooking_items_history
from sample_data import seed_sample_data
from ml_model import train_model, predict_food_quantity

# Point Flask to serve static files from frontend/ directory
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)

def initialize_backend():
    print("[BACKEND INIT] Initializing SQLite database and sample dataset...")
    seed_sample_data()
    print("[BACKEND INIT] Training Random Forest Regressor ML Model...")
    train_model()
    print("[BACKEND INIT] Flask backend ready!")

initialize_backend()

# ============================================================
# FRONTEND STATIC ROUTES
# ============================================================

@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    if os.path.exists(os.path.join(FRONTEND_DIR, path)):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, 'index.html')

# ============================================================
# API ENDPOINTS
# ============================================================

@app.route('/api/attendance', methods=['GET'])
def api_get_attendance():
    date_param = request.args.get('date', '2026-02-02')
    summary = get_attendance_summary(date_param)
    return jsonify(summary), 200

@app.route('/api/predict', methods=['POST'])
def api_predict():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid request payload. Expected JSON."}), 400

    date_str = data.get('date', '2026-02-02')
    day_str = data.get('day', 'Monday')
    attendance_cnt = int(data.get('attendance', 642))
    items_list = data.get('items', [])

    if not items_list:
        return jsonify({"error": "Please provide at least one food item."}), 400

    prediction_output = predict_food_quantity(date_str, day_str, attendance_cnt, items_list)
    save_prediction_records(date_str, day_str, attendance_cnt, prediction_output['results'])

    return jsonify(prediction_output), 200

@app.route('/api/history', methods=['GET'])
def api_get_history():
    history_records = get_prediction_history()
    return jsonify({"history": history_records}), 200

@app.route('/api/cooking-items', methods=['GET'])
def api_get_cooking_items():
    items_data = get_cooking_items_history()
    return jsonify(items_data), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Serving AI Food Prep System Web App on http://127.0.0.1:{port}")
    app.run(host='127.0.0.1', port=port, debug=False)
