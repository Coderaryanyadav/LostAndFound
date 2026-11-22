# 🎓 SBMP Lost & Found Management System

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Web%20App-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Tkinter](https://img.shields.io/badge/Tkinter-Desktop%20GUI-blue)](https://docs.python.org/3/library/tkinter.html)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Platform](https://img.shields.io/badge/Platform-Cross--Platform-lightgrey)](#)
[![Tests](https://img.shields.io/badge/Tests-Passing-success)](#)

A complete campus lost and found item recovery platform for colleges, offering both an interactive **Web Application** with a RESTful API and an administrative **Desktop GUI Application** with student self-registration and smart match verification.

**Developer:** Aryan Yadav  
**Institution:** SBMP College  
**Repository:** [Coderaryanyadav/LostAndFound](https://github.com/Coderaryanyadav/LostAndFound)

---

## 🚀 Quick Start

### 1. Installation

```bash
git clone https://github.com/Coderaryanyadav/LostAndFound.git
cd LostAndFound
pip install -r requirements.txt
```

### 2. Launch the Web Application

```bash
python app.py
```
Open your browser at `http://127.0.0.1:5000` to access the dashboard.

### 3. Launch the Desktop Application

```bash
python main.py
```
Launches the desktop GUI for student self-registration, watchman logging, and admin match verification.

---

## 🔑 Default Credentials

- **Admin Username:** `admin`
- **Admin Password:** `admin`

Students can register their own accounts directly through the "New Student? Register Here" portal in the desktop app.

---

## ✨ Features

- 📊 **Real-time Web Dashboard** - Live metrics for reported items, recoveries, and active matches.
- 🎓 **Student Self-Registration & Portal** - Students can create personal accounts, report lost belongings, and view status.
- 📦 **Campus Security / Found Logging** - Dedicated reporting workflow for found items across classrooms and labs.
- 🎯 **Smart Match Engine** - Multi-attribute matching with keyword tolerance, location proximity, and color filtering.
- 🔗 **Admin Verification Flow** - One-click resolution and item return verification.
- 💾 **Data Export** - Instant CSV export of registry records.
- 🛡️ **Audit Logging** - Timestamped record of logins, submissions, and resolutions (`log.txt`).
- 🎨 **Unified Dark UI** - Modern interface for both web and desktop versions.

---

## 📁 Repository Structure

```
LostAndFound/
├── app.py              # Flask Web Application & REST API
├── main.py             # Desktop GUI Application (Tkinter & SQLite)
├── templates/
│   └── index.html      # Responsive Web UI
├── static/
│   └── style.css       # Dark-themed modern CSS stylesheet
├── heavy_test.py       # Comprehensive API & functional test suite
├── test_app.py         # In-memory web route tests
├── test_main.py        # Desktop logic & database tests
├── requirements.txt    # Project dependencies
└── README.md           # Documentation
```

---

## 🧪 Testing

Run all automated test suites:

```bash
# Run web route unit tests
python -m unittest test_app.py

# Run desktop logic & matching tests
python -m unittest test_main.py

# Run comprehensive end-to-end API test (with app.py running)
python heavy_test.py
```
