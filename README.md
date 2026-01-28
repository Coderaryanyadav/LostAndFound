# 🎓 SBMP Lost & Found Management System

A modern web-based lost and found management system for colleges, built with Flask and deployed with a dark-themed responsive UI.

**Developer:** Aryan Yadav  
**Project:** Diploma Computer Science  
**Institution:** SBMP College  
**GitHub:** [@Coderaryanyadav](https://github.com/Coderaryanyadav)

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/Coderaryanyadav/LostAndFound.git
cd LostAndFound

# Install dependencies
pip3 install -r requirements.txt

# Run the application
python3 app.py

# Open browser at: http://127.0.0.1:5000
```

---

## ✨ Features

- 📊 **Real-time Dashboard** - Live statistics and smart room matching
- 📝 **Report Lost Items** - Students can report lost belongings
- 🔍 **Log Found Items** - Easy reporting of found items  
- 🎯 **Smart Matching** - Automatic room-based matching algorithm
- 🔎 **Search & Filter** - Quick item lookup with filters
- ✏️ **CRUD Operations** - Resolve, update, and delete entries
- 💾 **Data Export** - CSV export for backups
- 🎨 **Modern UI** - Dark theme with smooth animations
- 🛡️ **Secure** - Input validation and error handling

---

## 📁 Project Structure

```
LostAndFound/
├── app.py                 # Flask backend (RESTful API)
├── templates/
│   └── index.html        # Frontend UI
├── static/
│   └── style.css         # Dark theme styling
├── main.py               # Optional: Tkinter desktop version
├── heavy_test.py         # Comprehensive testing script
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── .gitignore           # Git ignore rules
```

---

## 🛠️ Tech Stack

**Backend:**
- Python 3.x
- Flask (Web framework)
- SQLite3 (Database)

**Frontend:**
- HTML5 & CSS3
- JavaScript (ES6+)
- Fetch API

**Optional:**
- Tkinter (Desktop GUI)
- Matplotlib (Analytics)

---

## 📊 Database Schema

### lost_items
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| student_name | TEXT | Student name |
| roll_no | TEXT | Roll number |
| item_name | TEXT | Item description |
| room_no | TEXT | Room location |
| category | TEXT | Item category |
| date | TEXT | Date reported |
| status | TEXT | Pending/Resolved |

### found_items
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| finder_name | TEXT | Finder name |
| item_name | TEXT | Item description |
| room_no | TEXT | Room location |
| category | TEXT | Item category |
| date | TEXT | Date found |
| status | TEXT | Available/Claimed |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Homepage |
| GET | `/api/stats` | Dashboard statistics |
| GET | `/api/lost` | Get all lost items |
| POST | `/api/lost` | Report lost item |
| GET | `/api/found` | Get all found items |
| POST | `/api/found` | Log found item |
| PUT | `/api/item/<type>/<id>` | Resolve item |
| DELETE | `/api/item/<type>/<id>` | Delete item |
| GET | `/api/export` | Export to CSV |

---

## 🧪 Testing

Run the comprehensive test suite:

```bash
python3 heavy_test.py
```

**Test Coverage:**
- ✅ 47 total tests
- ✅ API endpoints
- ✅ Form validation
- ✅ CRUD operations
- ✅ Error handling
- ✅ Security (SQL injection, XSS)
- ✅ Stress testing
- ✅ Edge cases

---

## 🎯 Usage

1. **Dashboard**: View statistics and room matches
2. **Report Lost**: Fill in student details and item information
3. **Log Found**: Enter found item details
4. **Inventory**: Search, filter, and manage all items
5. **Export**: Download database as CSV

---

## 🔐 Security Features

- Input validation on all forms
- SQL injection prevention
- XSS protection
- Error handling
- Data sanitization

---

## 📝 License

Student Project - SBMP College © 2026

---

## 👨‍💻 Developer

**Aryan Yadav**  
Diploma Computer Science  
SBMP College

**GitHub:** [github.com/Coderaryanyadav](https://github.com/Coderaryanyadav)  
**Project:** [github.com/Coderaryanyadav/LostAndFound](https://github.com/Coderaryanyadav/LostAndFound)

---

## 🙏 Acknowledgments

- Flask framework
- Python community
- SBMP College faculty

---

**⭐ If you found this project helpful, please give it a star!**
