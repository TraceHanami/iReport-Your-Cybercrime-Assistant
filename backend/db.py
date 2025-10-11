from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Allow frontend to access API

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('complaints.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            aadhaar_id TEXT,
            category TEXT,
            state TEXT,
            district TEXT,
            village TEXT,
            landmark TEXT,
            imei TEXT,
            sim TEXT,
            date TEXT,
            time TEXT,
            details TEXT,
            suspect_name TEXT,
            suspect_email TEXT,
            suspect_phone TEXT,
            police_complaint TEXT,
            money REAL DEFAULT 0,
            injury TEXT DEFAULT 'None',
            missing TEXT DEFAULT 'None',
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Save complaint
@app.route('/api/complaints', methods=['POST'])
def save_complaint():
    data = request.json
    try:
        conn = sqlite3.connect('complaints.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO complaints (
                name, aadhaar_id, category, state, district, village, landmark,
                imei, sim, date, time, details, suspect_name, suspect_email,
                suspect_phone, police_complaint, money, injury, missing, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('Name'),
            data.get('ID'),
            data.get('Category'),
            data.get('State'),
            data.get('District'),
            data.get('Village'),
            data.get('Landmark'),
            data.get('IMEI'),
            data.get('SIM'),
            data.get('Date'),
            data.get('Time'),
            data.get('Details'),
            data.get('SuspectName'),
            data.get('SuspectEmail'),
            data.get('SuspectPhone'),
            data.get('PoliceComplaint'),
            data.get('Money', 0),
            data.get('Injury', 'None'),
            data.get('Missing', 'None'),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        complaint_id = c.lastrowid
        conn.close()
        return jsonify({"status": "success", "id": complaint_id}), 201
    except Exception as e:
        print(e)
        return jsonify({"status": "error", "message": str(e)}), 500

# Get reports with priority calculation
@app.route('/api/reports', methods=['GET'])
def get_reports():
    try:
        conn = sqlite3.connect('complaints.db')
        c = conn.cursor()
        c.execute("SELECT id, category, name, date, money, injury, missing, details FROM complaints ORDER BY created_at DESC")
        rows = c.fetchall()
        conn.close()

        reports = []
        for r in rows:
            case_id, crime_type, reported_by, date, money, injury, missing, details = r

            # Priority logic
            priority_score = 0

            # Financial loss
            if money > 100000:  # large loss
                priority_score += 3
            elif money > 50000:
                priority_score += 2
            elif money > 0:
                priority_score += 1

            # Physical injury
            if injury.lower() in ['serious', 'major', 'critical']:
                priority_score += 3
            elif injury.lower() in ['minor', 'moderate']:
                priority_score += 2

            # Missing items/person
            if missing.lower() in ['person', 'human']:
                priority_score += 3
            elif missing.lower() in ['valuable', 'expensive', 'property']:
                priority_score += 2

            # Determine priority level
            if priority_score >= 6:
                priority = "High"
            elif priority_score >= 3:
                priority = "Medium"
            else:
                priority = "Low"

            reports.append({
                "case_id": case_id,
                "type": crime_type,
                "reported_by": reported_by,
                "date": date,
                "priority": priority
            })

        return jsonify(reports)

    except Exception as e:
        print(e)
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
