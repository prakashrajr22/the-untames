import sqlite3
import os

# DB File Path inside backend/data/
DB_DIR = os.path.join(os.path.dirname(__file__), 'data')
DB_PATH = os.path.join(DB_DIR, 'food_prep.db')

def get_db_connection():
    """Establish and return SQLite database connection with dictionary row access."""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database schema with required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Sample Biometric Attendance Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            student_id TEXT NOT NULL,
            student_name TEXT NOT NULL,
            status TEXT NOT NULL,
            check_in_time TEXT
        );
    ''')

    # 2. Student / Admin Feedback Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            rating INTEGER NOT NULL,
            category TEXT,
            comment TEXT
        );
    ''')

    # 3. Historical Food Preparation Dataset Table (for ML Training)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS food_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            day TEXT NOT NULL,
            attendance INTEGER NOT NULL,
            item TEXT NOT NULL,
            prepared_quantity INTEGER NOT NULL,
            feedback_score INTEGER DEFAULT 4
        );
    ''')

    # 4. AI Prediction History Output Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prediction_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            day TEXT NOT NULL,
            attendance INTEGER NOT NULL,
            item TEXT NOT NULL,
            predicted_quantity INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    # 5. Cooking Items Log Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cooking_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            day TEXT NOT NULL,
            item TEXT NOT NULL,
            quantity INTEGER NOT NULL
        );
    ''')

    conn.commit()
    conn.close()
    print("[DATABASE] Database schema initialized successfully.")

def get_attendance_summary(date_str):
    """Query biometric attendance database for given date."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total FROM attendance WHERE date = ?", (date_str,))
    total_row = cursor.fetchone()
    total_students = total_row['total'] if total_row else 0

    cursor.execute("SELECT COUNT(*) as present FROM attendance WHERE date = ? AND status = 'PRESENT'", (date_str,))
    present_row = cursor.fetchone()
    present_count = present_row['present'] if present_row else 0

    conn.close()

    # Fallback to sample logic if date not found in DB
    if total_students == 0:
        total_students = 800
        present_count = 642

    absent_count = total_students - present_count

    return {
        "date": date_str,
        "total_students": total_students,
        "present": present_count,
        "absent": absent_count
    }

def save_prediction_records(date_str, day_str, attendance_cnt, results):
    """Save generated AI predictions into prediction_history table."""
    conn = get_db_connection()
    cursor = conn.cursor()

    for item_res in results:
        cursor.execute('''
            INSERT INTO prediction_history (date, day, attendance, item, predicted_quantity)
            VALUES (?, ?, ?, ?, ?)
        ''', (date_str, day_str, attendance_cnt, item_res['item'], item_res['predicted_quantity']))

    conn.commit()
    conn.close()
    print(f"[DATABASE] Saved {len(results)} prediction records for date {date_str}.")

def get_prediction_history():
    """Retrieve formatted previous prediction records grouped by date."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT date, day, attendance, item, predicted_quantity, created_at 
        FROM prediction_history 
        ORDER BY id DESC
    ''')
    rows = cursor.fetchall()
    conn.close()

    # Group by date
    grouped = {}
    for r in rows:
        key = f"{r['date']} - {r['day']}"
        if key not in grouped:
            grouped[key] = {
                "date": r['date'],
                "day": r['day'],
                "attendance": r['attendance'],
                "items": []
            }
        grouped[key]["items"].append({
            "name": r['item'],
            "quantity": r['predicted_quantity']
        })

    result_list = []
    for k, v in grouped.items():
        total = sum(i['quantity'] for i in v['items'])
        result_list.append({
            "date": v['date'],
            "day": v['day'],
            "attendance": v['attendance'],
            "items": v['items'],
            "total": total
        })

    return result_list

def get_cooking_items_history():
    """Retrieve cooking items for Cookin Check modal."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT date, day FROM cooking_items ORDER BY date DESC LIMIT 2")
    date_rows = cursor.fetchall()

    todays_items = ["Rice", "Dal", "Vegetables", "Oil"]
    previous_items = ["Rice", "Idli batter", "Dosa batter", "Vegetables"]

    if len(date_rows) > 0:
        cursor.execute("SELECT item FROM cooking_items WHERE date = ?", (date_rows[0]['date'],))
        t_items = [r['item'] for r in cursor.fetchall()]
        if t_items: todays_items = t_items

    if len(date_rows) > 1:
        cursor.execute("SELECT item FROM cooking_items WHERE date = ?", (date_rows[1]['date'],))
        p_items = [r['item'] for r in cursor.fetchall()]
        if p_items: previous_items = p_items

    conn.close()

    return {
        "todays_items": todays_items,
        "previous_items": previous_items
    }
