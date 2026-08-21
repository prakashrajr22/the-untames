import os
import random
from datetime import datetime, timedelta
from database import get_db_connection, init_db

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

FOOD_ITEMS = ["Dosa", "Idli", "Rice", "Chapati", "Pongal", "Poori", "Vada", "Upma"]

STUDENT_NAMES = [
    f"Student {i:03d}" for i in range(1, 801)
]

def seed_sample_data():
    """Populate database with sample biometric attendance and historical food prep data."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if attendance data already exists
    cursor.execute("SELECT COUNT(*) as count FROM attendance")
    if cursor.fetchone()['count'] > 0:
        print("[SAMPLE DATA] Database already seeded. Skipping initial seed.")
        conn.close()
        return

    print("[SAMPLE DATA] Seeding database with realistic sample records...")

    start_date = datetime(2026, 1, 20)
    end_date = datetime(2026, 2, 5)

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        day_str = DAYS_OF_WEEK[current_date.weekday()]

        # Determine attendance count pattern per day of week
        if day_str in ["Monday", "Wednesday"]:
            present_target = random.randint(630, 670) # e.g. ~642 on Mon
        elif day_str in ["Tuesday", "Thursday"]:
            present_target = random.randint(700, 740) # e.g. ~710 on Tue
        elif day_str == "Friday":
            present_target = random.randint(680, 720) # e.g. ~700 on Fri
        else: # Weekend
            present_target = random.randint(520, 580) # Lower weekend attendance

        # 1. Seed Attendance Table
        present_indices = set(random.sample(range(800), present_target))
        attendance_rows = []
        for idx in range(800):
            stu_id = f"STU{idx+1:03d}"
            stu_name = STUDENT_NAMES[idx]
            if idx in present_indices:
                status = "PRESENT"
                hour = random.randint(7, 8)
                minute = random.randint(10, 59)
                check_in = f"{hour:02d}:{minute:02d}"
            else:
                status = "ABSENT"
                check_in = "-"
            
            attendance_rows.append((date_str, stu_id, stu_name, status, check_in))

        cursor.executemany('''
            INSERT INTO attendance (date, student_id, student_name, status, check_in_time)
            VALUES (?, ?, ?, ?, ?)
        ''', attendance_rows)

        # 2. Seed Historical Food Prep Dataset (for Machine Learning)
        # Relationship: prepared_quantity ~ f(attendance, item_type, day_of_week) + noise
        day_mult = 1.05 if day_str in ["Tuesday", "Thursday"] else 1.0
        
        # Items for this day
        daily_items = random.sample(FOOD_ITEMS, 3)
        for item in daily_items:
            if item in ["Dosa", "Idli"]:
                base_qty = int(present_target * 0.38 * day_mult)
            elif item in ["Rice", "Chapati"]:
                base_qty = int(present_target * 0.22 * day_mult)
            elif item in ["Pongal", "Poori"]:
                base_qty = int(present_target * 0.28 * day_mult)
            else:
                base_qty = int(present_target * 0.15 * day_mult)

            # Add slight realistic kitchen variance
            prepared_qty = max(20, base_qty + random.randint(-15, 15))
            rating = random.randint(3, 5)

            cursor.execute('''
                INSERT INTO food_history (date, day, attendance, item, prepared_quantity, feedback_score)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (date_str, day_str, present_target, item, prepared_qty, rating))

        # 3. Seed Cooking Items Log
        for item in daily_items:
            cursor.execute('''
                INSERT INTO cooking_items (date, day, item, quantity)
                VALUES (?, ?, ?, ?)
            ''', (date_str, day_str, item, random.randint(20, 100)))

        current_date += timedelta(days=1)

    # 4. Seed Initial Sample Prediction History
    sample_preds = [
        ("2026-02-02", "Monday", 642, "Dosa", 250),
        ("2026-02-02", "Monday", 642, "Idli", 380),
        ("2026-02-02", "Monday", 642, "Rice", 140),
        ("2026-02-01", "Sunday", 540, "Dosa", 230),
        ("2026-02-01", "Sunday", 540, "Idli", 350),
        ("2026-02-01", "Sunday", 540, "Rice", 110),
    ]

    cursor.executemany('''
        INSERT INTO prediction_history (date, day, attendance, item, predicted_quantity)
        VALUES (?, ?, ?, ?, ?)
    ''', sample_preds)

    conn.commit()
    conn.close()
    print("[SAMPLE DATA] Successfully seeded database with biometric and historical records!")

if __name__ == "__main__":
    seed_sample_data()
