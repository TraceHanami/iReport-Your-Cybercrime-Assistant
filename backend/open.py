import sqlite3

conn = sqlite3.connect('complaints.db')
c = conn.cursor()
c.execute("SELECT * FROM complaints ORDER BY id DESC LIMIT 5")  # show last 5 complaints
rows = c.fetchall()
for row in rows:
    print(row)
conn.close()
