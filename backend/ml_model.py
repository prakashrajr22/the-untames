import sqlite3
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from database import get_db_connection

# Global Model & Encoder Singleton Instances
rf_model = None
item_encoder = LabelEncoder()
is_trained = False

DAYS_MAP = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6
}

def train_model():
    """Fetch historical food prep dataset from database and train Random Forest Regressor model."""
    global rf_model, item_encoder, is_trained

    print("[ML MODEL] Querying historical food prep training dataset from database...")
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT date, day, attendance, item, prepared_quantity FROM food_history", conn)
    conn.close()

    if df.empty:
        print("[ML MODEL WARNING] Food history table is empty. Unable to train model.")
        return False

    # Feature Engineering & Encoding
    # 1. Day of Week Encoding
    df['day_encoded'] = df['day'].map(lambda d: DAYS_MAP.get(d, 0))

    # 2. Item Encoding
    df['item_clean'] = df['item'].str.strip().str.title()
    item_encoder.fit(df['item_clean'])
    df['item_encoded'] = item_encoder.transform(df['item_clean'])

    # 3. Features matrix X and Target vector y
    # Features: [attendance, day_encoded, item_encoded]
    X = df[['attendance', 'day_encoded', 'item_encoded']]
    y = df['prepared_quantity']

    # Train Random Forest Regressor
    rf_model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    rf_model.fit(X, y)

    is_trained = True
    print(f"[ML MODEL] RandomForestRegressor trained successfully on {len(df)} historical records!")
    return True

def predict_food_quantity(date_str, day_str, attendance_cnt, items_list):
    """
    Generate AI food demand predictions for a list of input menu items.
    
    :param date_str: String date (YYYY-MM-DD)
    :param day_str: String day of week (e.g. "Monday")
    :param attendance_cnt: Present biometric headcount (e.g. 642)
    :param items_list: List of dicts [{'name': 'Dosa', 'quantity': 200}, ...]
    :return: Dict containing results array in exact input order and total count.
    """
    global rf_model, is_trained

    if not is_trained or rf_model is None:
        train_model()

    day_encoded = DAYS_MAP.get(day_str, 0)
    results = []
    total_predicted = 0

    for item_entry in items_list:
        raw_name = item_entry.get('name', 'Item').strip()
        base_qty = int(item_entry.get('quantity', 50))
        clean_name = raw_name.title()

        # Handle item categorical encoding safely
        if hasattr(item_encoder, 'classes_') and clean_name in item_encoder.classes_:
            item_encoded_val = item_encoder.transform([clean_name])[0]
        else:
            # Fallback for unseen food items
            item_encoded_val = 0

        # Predict using Random Forest
        feature_vector = np.array([[attendance_cnt, day_encoded, item_encoded_val]])
        
        if rf_model is not None and is_trained:
            raw_prediction = rf_model.predict(feature_vector)[0]
            # Blend ML model baseline prediction with user entered baseline ratio for realistic scaling
            # ratio multiplier based on biometric attendance vs standard (700)
            scaling_factor = max(0.5, attendance_cnt / 700.0)
            
            # Combine ML pattern with user's base ratio
            predicted_qty = int(round(0.6 * raw_prediction + 0.4 * (base_qty * scaling_factor)))
        else:
            # Fallback estimation if model is uninitialized
            predicted_qty = int(round(base_qty * (attendance_cnt / 700.0)))

        # Ensure sensible lower bound
        predicted_qty = max(10, predicted_qty)

        results.append({
            "item": raw_name,
            "predicted_quantity": predicted_qty
        })
        total_predicted += predicted_qty

    return {
        "date": date_str,
        "day": day_str,
        "attendance": attendance_cnt,
        "results": results,
        "total": total_predicted
    }

if __name__ == "__main__":
    from sample_data import seed_sample_data
    seed_sample_data()
    train_model()
