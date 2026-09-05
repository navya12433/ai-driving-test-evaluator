import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'results.db')


def init_db():
    """Creates the results table if it doesn't already exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            attention_score INTEGER,
            lane_discipline_score INTEGER,
            safety_score INTEGER,
            signal_compliance_score INTEGER,
            unsafe_behavior_score INTEGER,
            total_score INTEGER,
            result TEXT,
            created_at TEXT
        )
    ''')

    conn.commit()
    conn.close()


def save_evaluation(filename, attention_score, lane_score, safety_score,
                     signal_score, unsafe_score, total_score, result):
    """Saves one candidate's evaluation result to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO evaluations (
            filename, attention_score, lane_discipline_score, safety_score,
            signal_compliance_score, unsafe_behavior_score, total_score,
            result, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        filename, attention_score, lane_score, safety_score,
        signal_score, unsafe_score, total_score, result,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def get_all_evaluations():
    """Returns all past evaluation results, most recent first."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM evaluations ORDER BY created_at DESC')
    rows = cursor.fetchall()

    conn.close()
    return [dict(row) for row in rows]


if __name__ == "__main__":
    # Quick manual test: initializes the DB and inserts one sample row
    init_db()
    save_evaluation(
        filename="test_video.mp4",
        attention_score=15, lane_score=11, safety_score=20,
        signal_score=20, unsafe_score=19, total_score=85, result="PASS"
    )
    print(get_all_evaluations())