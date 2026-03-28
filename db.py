import sqlite3
from datetime import datetime

DB_NAME = "scores.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module TEXT,
            score INTEGER,
            total INTEGER,
            time_taken REAL,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_score(module, score, total, time_taken):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO scores (module, score, total, time_taken, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (module, score, total, time_taken, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_scores():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM scores ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows


def clear_scores():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM scores")
    conn.commit()
    conn.close()
