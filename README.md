# 🍲 AI Food Prep System - Demand Prediction Dashboard

[![GitHub Repository](https://img.shields.io/badge/GitHub-the--untames-blue?logo=github)](https://github.com/prakashrajr22/the-untames)
[![Python](https://img.shields.io/badge/Python-3.9+-green.svg?logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Backend-Flask-black.svg?logo=flask)](https://flask.palletsprojects.com/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Random--Forest-orange.svg?logo=scikitlearn)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](#)

An AI-assisted food preparation and demand prediction system for institutional kitchen administrators. Features an elegant **paper/notebook visual interface**, an interactive **cooking vessel input**, a **stove output with flickering 🔥 flame animations**, a **Flask REST API**, **SQLite sample biometric database**, and a **Scikit-Learn Random Forest Regression** machine learning pipeline.

---

## 🔗 Quick Repository & Web Links

* **GitHub Repository URL**: [https://github.com/prakashrajr22/the-untames](https://github.com/prakashrajr22/the-untames)
* **Local Web Application URL**: `http://127.0.0.1:5000`
* **Google Form Feedback Link**: [https://docs.google.com/forms/d/e/1FAIpQLScVxIq9EXUaPDyEdDQpfR5pVjTLw1XFhqzwmDPebxRvn4ON8g/viewform?usp=publish-editor](https://docs.google.com/forms/d/e/1FAIpQLScVxIq9EXUaPDyEdDQpfR5pVjTLw1XFhqzwmDPebxRvn4ON8g/viewform?usp=publish-editor)

---

## 📌 Project Overview

In large institutional kitchens (such as college messes and cafeterias), preparing the right food quantity is critical to prevent both food waste and food shortages. 

This system automates food preparation planning:
1. Retrieves real-time **Biometric Attendance** headcount for a selected date.
2. Identifies the **Day of the Week** automatically.
3. Accepts planned menu items via an intuitive **Cooking Vessel** interface.
4. Processes attendance, day patterns, menu items, and historical meal data through a **Random Forest Regressor** ML model.
5. Displays optimized portion recommendations on an interactive **Stove Screen** with animated 🔥 flames.
6. Synchronizes recommendations with an administrative **Notification Bell**.

---

## 🏗️ Architecture & Data Flow

```text
DATE + DAY SELECTION (e.g. 02/02/2026 -> Monday)
        ↓
GET /api/attendance?date=2026-02-02
        ↓
SAMPLE BIOMETRIC ATTENDANCE DATABASE (SQLite)
        ↓
PRESENT HEADCOUNT (e.g. 660 Present)
        ↓
ENTER MENU ITEMS via 🍲 VESSEL (Dosa: 200, Idli: 400, Rice: 150)
        ↓
POST /api/predict
        ↓
RANDOM FOREST REGRESSION MODEL (scikit-learn)
        ↓
STOVE DISPLAY & 🔥 FIRE ANIMATION (Dosa: 250, Idli: 380, Rice: 140 | Total: 770)
        ↓
SAVED TO prediction_history TABLE IN SQLite
        ↓
🔔 NOTIFICATION BADGE & DROPDOWN SYNC
```

---

## 🎨 Visual Design & Color System

Designed with a bespoke **paper notebook / administrative kitchen aesthetic**:

* **Pale Gold (`#E2C87A`)**: Main paper area background, outer container borders, header border, vessel/stove accents.
* **Dark Sand (`#B89326`)**: Sidebar text, icons, buttons, vessel/stove details.
* **Cream (`#FFFFF0`)**: Application body, sidebar, header, and modal card backgrounds.
* **Dark Tech Blue (`#26384A`)**: Mathematically centered title, headings, and footer background.
* **Soft Red (`#E98B8B` / Border `#B85D5D`)**: Reserved **exclusively** for the Date & Present Attendance Ribbons.
* **White (`#FFFFFF`)**: Input fields and contrast surfaces.

---

## 📁 Repository Directory Structure

```text
the-untames/
│
├── frontend/
│   ├── index.html          # Semantic HTML5 paper-notebook layout
│   ├── style.css           # Custom CSS3 color system & vector graphics
│   ├── script.js           # ES6 frontend logic & REST API hooks
│   └── assets/
│       ├── logo.png        # Header logo
│       └── admin.png       # Admin profile picture
│
├── backend/
│   ├── app.py              # Single-port Flask server & REST API
│   ├── database.py         # SQLite schema & query handlers
│   ├── ml_model.py         # Random Forest Regressor ML pipeline
│   ├── sample_data.py      # Sample biometric attendance & history seeder
│   ├── requirements.txt    # Python dependencies
│   └── data/
│       └── food_prep.db    # SQLite database file
│
├── .gitignore              # Ignores venv/ and python cache files
└── README.md               # Repository documentation & guide
```

---

## ⚡ Quickstart Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/prakashrajr22/the-untames.git
cd the-untames/backend
```

### 2. Install Python Dependencies
```bash
python -m pip install -r requirements.txt
```

### 3. Initialize Database & Train Model
```bash
python sample_data.py
python ml_model.py
```

### 4. Start the Application
```bash
python app.py
```

Open your browser and navigate to:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 📡 REST API Documentation

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/attendance` | `GET` | Query `?date=YYYY-MM-DD`. Returns `{ date, total_students, present, absent }`. |
| `/api/predict` | `POST` | Body: `{ date, day, attendance, items }`. Runs Random Forest model and stores prediction history. |
| `/api/history` | `GET` | Returns stored prediction history records for the History sidebar modal. |
| `/api/cooking-items` | `GET` | Returns historical cooking item records for the Cookin Check modal. |

---

## 📜 License & Credits

Developed for the **AI Food Prep System** project.  
Repository: [prakashrajr22/the-untames](https://github.com/prakashrajr22/the-untames)
