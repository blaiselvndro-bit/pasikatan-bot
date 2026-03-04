import sqlite3

conn = sqlite3.connect("pasikatan.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS players(
user_id INTEGER,
username TEXT,
photo TEXT,
topic INTEGER,
votes INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS games(
topic INTEGER,
start_time INTEGER,
end_time INTEGER,
status TEXT
)
""")

conn.commit()
