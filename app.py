from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import json
import csv
import io
from datetime import datetime

app = Flask(__name__)
DB_NAME = "college_data.db"

def init_db():
    """Initialize SQLite database with proper schema"""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        c.execute("""
            CREATE TABLE IF NOT EXISTS lost_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                roll_no TEXT NOT NULL,
                item_name TEXT NOT NULL,
                room_no TEXT,
                category TEXT DEFAULT 'Other',
                date TEXT,
                status TEXT DEFAULT 'Pending'
            )
        """)
        
        c.execute("""
            CREATE TABLE IF NOT EXISTS found_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                finder_name TEXT,
                item_name TEXT NOT NULL,
                room_no TEXT,
                category TEXT DEFAULT 'Other',
                date TEXT,
                status TEXT DEFAULT 'Available'
            )
        """)
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Database init error: {e}")
        return False

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    """Get dashboard statistics"""
    try:
        conn = sqlite3.connect(DB_NAME)
        
        lost_count = conn.execute("SELECT COUNT(*) FROM lost_items WHERE status='Pending'").fetchone()[0]
        found_count = conn.execute("SELECT COUNT(*) FROM found_items WHERE status='Available'").fetchone()[0]
        
        matches = conn.execute("""
            SELECT l.student_name, l.item_name, l.room_no
            FROM lost_items l 
            JOIN found_items f ON l.room_no = f.room_no
            WHERE l.status='Pending' AND f.status='Available' AND l.room_no != ''
        """).fetchall()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'lost_count': lost_count,
            'found_count': found_count,
            'match_count': len(matches),
            'matches': [{'name': m[0], 'item': m[1], 'room': m[2]} for m in matches]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/lost', methods=['GET', 'POST'])
def lost_items():
    """Handle lost items"""
    try:
        conn = sqlite3.connect(DB_NAME)
        
        if request.method == 'POST':
            data = request.json
            if not data.get('name') or not data.get('item'):
                return jsonify({'success': False, 'error': 'Missing required fields'}), 400
            
            conn.execute("""
                INSERT INTO lost_items (student_name, roll_no, item_name, room_no, category, date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (data['name'], data.get('roll', ''), data['item'], data.get('room', ''), 
                  data.get('category', 'Other'), datetime.now().strftime('%Y-%m-%d')))
            conn.commit()
            conn.close()
            return jsonify({'success': True})
        
        else:
            cursor = conn.execute("SELECT * FROM lost_items ORDER BY id DESC")
            items = [{'id': r[0], 'name': r[1], 'roll': r[2], 'item': r[3], 
                      'room': r[4], 'category': r[5], 'date': r[6], 'status': r[7]} 
                     for r in cursor.fetchall()]
            conn.close()
            return jsonify(items)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/found', methods=['GET', 'POST'])
def found_items():
    """Handle found items"""
    try:
        conn = sqlite3.connect(DB_NAME)
        
        if request.method == 'POST':
            data = request.json
            if not data.get('item'):
                return jsonify({'success': False, 'error': 'Item name is required'}), 400
            
            conn.execute("""
                INSERT INTO found_items (finder_name, item_name, room_no, category, date)
                VALUES (?, ?, ?, ?, ?)
            """, (data.get('finder', ''), data['item'], data.get('room', ''),
                  data.get('category', 'Other'), datetime.now().strftime('%Y-%m-%d')))
            conn.commit()
            conn.close()
            return jsonify({'success': True})
        
        else:
            cursor = conn.execute("SELECT * FROM found_items ORDER BY id DESC")
            items = [{'id': r[0], 'finder': r[1], 'item': r[2], 'room': r[3],
                      'category': r[4], 'date': r[5], 'status': r[6]} 
                     for r in cursor.fetchall()]
            conn.close()
            return jsonify(items)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/item/<item_type>/<int:item_id>', methods=['PUT', 'DELETE'])
def manage_item(item_type, item_id):
    """Update or delete an item"""
    try:
        if item_type not in ['lost', 'found']:
            return jsonify({'success': False, 'error': 'Invalid item type'}), 400
        
        conn = sqlite3.connect(DB_NAME)
        table = f"{item_type}_items"
        
        if request.method == 'DELETE':
            conn.execute(f"DELETE FROM {table} WHERE id=?", (item_id,))
            conn.commit()
            conn.close()
            return jsonify({'success': True})
        
        elif request.method == 'PUT':
            status = 'Resolved' if item_type == 'lost' else 'Claimed'
            conn.execute(f"UPDATE {table} SET status=? WHERE id=?", (status, item_id))
            conn.commit()
            conn.close()
            return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/export')
def export_csv():
    """Export all data to CSV"""
    try:
        conn = sqlite3.connect(DB_NAME)
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(['=== LOST ITEMS ==='])
        writer.writerow(['ID', 'Name', 'Roll', 'Item', 'Room', 'Category', 'Date', 'Status'])
        
        lost = conn.execute("SELECT * FROM lost_items").fetchall()
        writer.writerows(lost)
        
        writer.writerow([])
        writer.writerow(['=== FOUND ITEMS ==='])
        writer.writerow(['ID', 'Finder', 'Item', 'Room', 'Category', 'Date', 'Status'])
        
        found = conn.execute("SELECT * FROM found_items").fetchall()
        writer.writerows(found)
        
        conn.close()
        
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'sbmp_export_{datetime.now().strftime("%Y%m%d")}.csv'
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'success': False, 'error': 'Server error'}), 500

if __name__ == '__main__':
    if init_db():
        print("✅ Database initialized successfully")
        print("🚀 Starting Flask server at http://127.0.0.1:5000")
        print("📝 Press CTRL+C to stop")
        app.run(debug=True, host='127.0.0.1', port=5000)
    else:
        print("❌ Failed to initialize database")
