# 🎓 SBMP Lost & Found Management System

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Web%20App-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Tkinter](https://img.shields.io/badge/Tkinter-Desktop%20GUI-blue)](https://docs.python.org/3/library/tkinter.html)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Tests](https://img.shields.io/badge/Tests-47%2F47%20Passing-success)](#testing)

An integrated campus asset recovery platform featuring an administrative Desktop Application (Tkinter) and a responsive Web Portal (Flask REST API) powered by intelligent item-matching algorithms.

**Lead Developer:** Aryan Yadav  
**Institution:** SBMP College  
**Repository:** [Coderaryanyadav/LostAndFound](https://github.com/Coderaryanyadav/LostAndFound)

---

## 🏗️ System Architecture

```mermaid
graph TD
    subgraph ClientLayer["Client Interfaces"]
        W[Web Browser / Mobile]
        D[Desktop GUI / Admin & Security Station]
    end

    subgraph AppLayer["Application Layer"]
        F[Flask Web Server - app.py]
        T[Tkinter Desktop Engine - main.py]
        M[Smart Match Engine]
    end

    subgraph DataLayer["Storage Layer"]
        DB1[(college_data.db)]
        DB2[(lost_found.db)]
        L[Audit Activity Log - log.txt]
    end

    W -->|REST API Requests| F
    D -->|Direct Local Events| T

    F -->|Read / Write| DB1
    T -->|Read / Write| DB2
    T -->|Audit Records| L

    T -->|Invoke Matching| M
    F -->|Query Matching Rooms| DB1
```

---

## 🔄 Match Resolution Workflow

```mermaid
sequenceDiagram
    autonumber
    actor Student as Student
    actor Watchman as Campus Watchman
    participant Engine as Lost & Found Engine
    actor Admin as Administrator

    Student->>Engine: Report Lost Belonging (Item, Color, Location)
    Engine-->>Student: Confirm Report Stored
    Watchman->>Engine: Turn in Found Item (Item, Color, Location)
    Engine->>Engine: Run Smart Match Algorithm
    alt Probable Match Found
        Engine-->>Watchman: Live Alert: Counterpart item detected!
        Admin->>Engine: Inspect Matched Item Pair
        Admin->>Engine: Verify Ownership & Release
        Engine->>Engine: Update Status to "Returned"
        Engine-->>Student: Case Marked Resolved
    else No Immediate Match
        Engine->>Engine: Keep Status as "Searching" / "Available"
    end
```

---

## 🚀 Quick Setup & Execution

### Prerequisites

- Python 3.8+
- SQLite3

### 1. Clone & Install Dependencies

```bash
git clone https://github.com/Coderaryanyadav/LostAndFound.git
cd LostAndFound
pip install -r requirements.txt
```

### 2. Run the Web Application

```bash
python app.py
```
Open your browser to: `http://127.0.0.1:5000`

### 3. Run the Desktop Application

```bash
python main.py
```

---

## 🔑 Default Credentials

- **Admin Account:** `admin` / `admin`
- **Student Accounts:** Self-register via the **"New Student? Register Here"** button on the desktop landing screen.

---

## ⚙️ Features

| Feature | Description | Platform |
| :--- | :--- | :--- |
| **Real-Time Dashboard** | Visual statistics on active reports and matched belongings | Web |
| **Student Self-Service** | Register, login, report personal lost items, and track status | Desktop |
| **Found Registry** | Dedicated intake workflow for campus security and watchmen | Both |
| **Smart Matching** | Keyword token analysis, color checking, and room proximity logic | Both |
| **CSV Data Export** | One-click offline backup generation | Web & Desktop |
| **Audit Trails** | Timestamped action logging saved to `log.txt` | Desktop |

---

## 🧪 Testing & Verification

```bash
# Run web route unit test suite
python -m unittest test_app.py

# Run desktop logic & matching algorithm test suite
python -m unittest test_main.py

# Run complete end-to-end API test suite (start app.py first)
python heavy_test.py
```

---

## 📜 Community & Governance

- [Contributing Guidelines](file:///Users/aryan/Desktop/PROJECTS/NOT%20TESTED/8%20-%20LostAndFoundCollege/CONTRIBUTING.md)
- [Code of Conduct](file:///Users/aryan/Desktop/PROJECTS/NOT%20TESTED/8%20-%20LostAndFoundCollege/CODE_OF_CONDUCT.md)
- [Security Policy](file:///Users/aryan/Desktop/PROJECTS/NOT%20TESTED/8%20-%20LostAndFoundCollege/SECURITY.md)
- [Project License](file:///Users/aryan/Desktop/PROJECTS/NOT%20TESTED/8%20-%20LostAndFoundCollege/LICENSE)
