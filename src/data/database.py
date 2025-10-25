# src/data/database.py - VERSIÓN FINAL Y LIMPIA

import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(__file__), 'hangul_sprint.db')

def connect_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vocabulary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kor_sent TEXT NOT NULL UNIQUE,
            roman TEXT NOT NULL,
            translation_en TEXT,
            level INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            mode TEXT NOT NULL,
            level INTEGER,
            duration REAL,
            accuracy REAL,
            wpm REAL,
            total_chars INTEGER,
            correct_chars INTEGER,
            wrong_chars INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS letter_errors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            letter TEXT NOT NULL,
            mode TEXT NOT NULL,
            count INTEGER DEFAULT 0,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    ''')

    conn.commit()
    conn.close()

def insert_vocabulary_batch(vocabulary_list):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.executemany('''INSERT OR IGNORE INTO vocabulary (kor_sent, roman, translation_en, level)
                          VALUES (?, ?, ?, ?)''', vocabulary_list)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    print("--- Probando database.py ---")
    create_tables()
    print("Tablas creadas/verificadas con la columna 'kor_sent'.")