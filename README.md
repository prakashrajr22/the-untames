# AI Food Prep System - Demand Prediction Dashboard & Backend

An AI-assisted food preparation and demand prediction prototype featuring a physical paper-notebook aesthetic frontend, a **Flask REST API**, **SQLite Database**, and a **Scikit-Learn Random Forest Regression** machine learning pipeline.

---

## 🏗️ Architecture & Data Flow

```text
DATE + DAY SELECTION
        ↓
GET /api/attendance?date=YYYY-MM-DD
        ↓
SAMPLE BIOMETRIC DATABASE (SQLite)
        ↓
PRESENT Headcount (e.g. 642)
        ↓
ENTER MENU ITEMS via 🍲 VESSEL (Dosa, Idli, Rice...)
        ↓
POST /api/predict
        ↓
RANDOM FOREST REGRESSION (scikit-learn)
        ↓
SAVED to prediction_history TABLE
        ↓
STOVE OUTPUT DISPLAY & 🔥 FIRE ANIMATION
        ↓
🔔 NOTIFICATION BADGE & DROPDOWN SYNC
```

---

## 🛠️ Technology Requirements

- **Frontend**: HTML5, Vanilla CSS3, Vanilla JavaScript (ES6) — No external UI frameworks.
- **Backend**: Python 3.9+, Flask, Flask-CORS
- **Database**: SQLite3 (`backend/data/food_prep.db`)
- **Machine Learning**: `scikit-learn` (`RandomForestRegressor`), `pandas`, `numpy`

---

## 📁 Repository Structure

```text
AI-Food-Prep-System/
│
├── frontend/
│   ├── index.html          # Semantic HTML5 dashboard container
│   ├── style.css           # Pale Gold & Soft Red paper aesthetic
│   ├── script.js           # ES6 frontend logic & fetch API hooks
│   └── assets/
│       ├── logo.png        # Header logo
│       └── admin.png       # Admin profile picture
│
├── backend/
│   ├── app.py              # Flask API web server & REST endpoints
│   ├── database.py         # SQLite schema initialization & database queries
│   ├── ml_model.py         # Random Forest ML model training & prediction logic
│   ├── sample_data.py      # Sample biometric attendance & history dataset seeder
│   ├── requirements.txt    # Python dependencies
│   └── data/
│       └── food_prep.db    # SQLite database file (auto-generated)
│
└── README.md               # Quickstart setup & architecture documentation
```

---

## ⚡ Quickstart Setup Instructions

### Step 1: Install Python Dependencies
Navigate to the `backend/` directory and install the required packages:

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Initialize Database & Train Random Forest Model
Run `sample_data.py` to create `food_prep.db` and populate realistic sample biometric attendance (800 students across multiple dates) and historical meal prep records:

```bash
python sample_data.py
```

Then train the Random Forest Regression model:

```bash
python ml_model.py
```

### Step 3: Start the Flask Backend Server
Run `app.py` to start the backend API server on `http://localhost:5000`:

```bash
python app.py
```

### Step 4: Open the Frontend Dashboard
1. Open VS Code.
2. Open the `frontend` folder.
3. Right-click `index.html` and select **Open with Live Server** (or open `http://localhost:5000` / open `index.html` directly in your browser).

---

## 📊 Sample Biometric Attendance Database

The biometric attendance is stored in the `attendance` table in `food_prep.db`:
- Stores student check-in records (`PRESENT`/`ABSENT`) for 800 students per date.
- When an admin picks a date (e.g. `2026-02-02`), `GET /api/attendance?date=2026-02-02` queries the database and calculates the present count (e.g. **642**).
- **Production Integration Note**: To connect real biometric hardware (fingerprint/face recognition scanners), replace the SQLite query in `database.py` (`get_attendance_summary`) with your institution's biometric DB connection.

---

## 🤖 Random Forest Regression Pipeline

- **Algorithm**: `sklearn.ensemble.RandomForestRegressor(n_estimators=100, random_state=42)`
- **Training Data**: Historical preparation records stored in `food_history` table.
- **Features Used**:
  1. `attendance`: Present student count
  2. `day_encoded`: Categorical day of week (Monday=0 ... Sunday=6)
  3. `item_encoded`: LabelEncoded food item index (Dosa, Idli, Rice, Chapati, etc.)
  4. `base_quantity`: Admin baseline input
- **Target Variable**: `prepared_quantity`
- **Output Preservation**: Preserves the **exact item order** entered by the admin in the vessel modal.
- **History Tracking**: Automatically saves every generated prediction into the `prediction_history` table.

---

## 📋 Google Form Feedback Connection

The **Feedback** sidebar option opens a dedicated information modal containing a direct link to the feedback collection form:
- **URL**: `https://docs.google.com/forms/d/e/1FAIpQLScVxIq9EXUaPDyEdDQpfR5pVjTLw1XFhqzwmDPebxRvn4ON8g/viewform?usp=publish-editor`
- Opens in a new tab when clicking **📋 SUBMIT GOOGLE FORM FEEDBACK**.

---

## 📡 REST API Documentation

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/attendance` | `GET` | Query string `?date=YYYY-MM-DD`. Returns `{ date, total_students, present, absent }`. |
| `/api/predict` | `POST` | Body: `{ date, day, attendance, items }`. Runs Random Forest Regressor and saves results to `prediction_history`. |
| `/api/history` | `GET` | Returns stored prediction history records for the History sidebar modal. |
| `/api/cooking-items`| `GET` | Returns historical cooking item data for the Cookin Check modal. |
