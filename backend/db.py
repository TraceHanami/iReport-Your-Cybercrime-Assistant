from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Create upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
            fir_file TEXT,
            suspect_file TEXT,
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
    data = request.form.to_dict()
    fir_file = request.files.get('fir-file')
    suspect_file = request.files.get('suspect-file')

    # Save files if provided
    fir_filename = None
    suspect_filename = None
    if fir_file:
        fir_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{fir_file.filename}"
        fir_file.save(os.path.join(app.config['UPLOAD_FOLDER'], fir_filename))
    if suspect_file:
        suspect_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{suspect_file.filename}"
        suspect_file.save(os.path.join(app.config['UPLOAD_FOLDER'], suspect_filename))

    # Prepare data
    try:
        money = float(data.get('Money', 0))
        injury = data.get('Injury', 'None')
        missing = data.get('Missing', 'None')

        # Calculate priority same as frontend
        priority_score = 0
        if money > 50000:
            priority_score += 2
        elif money > 10000:
            priority_score += 1

        if injury.lower() == "serious":
            priority_score += 3
        elif injury.lower() == "minor":
            priority_score += 1

        if missing.lower() == "person":
            priority_score += 3
        elif missing.lower() == "property":
            priority_score += 1

        if priority_score >= 5:
            priority = "High"
        elif priority_score >= 2:
            priority = "Medium"
        else:
            priority = "Low"

        conn = sqlite3.connect('complaints.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO complaints (
                name, aadhaar_id, category, state, district, village, landmark,
                imei, sim, date, time, details, suspect_name, suspect_email,
                suspect_phone, police_complaint, fir_file, suspect_file, money,
                injury, missing, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            fir_filename,
            suspect_filename,
            money,
            injury,
            missing,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        complaint_id = c.lastrowid
        conn.close()
        return jsonify({"status": "success", "id": complaint_id, "priority": priority}), 201
    except Exception as e:
        print(e)
        return jsonify({"status": "error", "message": str(e)}), 500

# Get reports with frontend-style priority
@app.route('/api/reports', methods=['GET'])
def get_reports():
    try:
        conn = sqlite3.connect('complaints.db')
        c = conn.cursor()
        c.execute("SELECT id, category, name, date, money, injury, missing FROM complaints ORDER BY created_at DESC")
        rows = c.fetchall()
        conn.close()

        reports = []
        for r in rows:
            case_id, crime_type, reported_by, date, money, injury, missing = r

            # Frontend priority logic
            priority_score = 0
            if money > 50000:
                priority_score += 2
            elif money > 10000:
                priority_score += 1

            if injury.lower() == "serious":
                priority_score += 3
            elif injury.lower() == "minor":
                priority_score += 1

            if missing.lower() == "person":
                priority_score += 3
            elif missing.lower() == "property":
                priority_score += 1

            if priority_score >= 5:
                priority = "High"
            elif priority_score >= 2:
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
