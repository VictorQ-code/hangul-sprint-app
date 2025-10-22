import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(__file__), 'hangul_sprint.db')

def connect_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row # Permite acceder a las columnas por nombre
    return conn

def create_tables():
    """
    Crea las tablas de la base de datos si no existen.
    Incluye vocabulary, sessions y letter_errors.
    """
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vocabulary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hangul TEXT NOT NULL UNIQUE,
            roman TEXT NOT NULL,
            translation_en TEXT,
            level INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            mode TEXT NOT NULL, -- 'reading', 'writing', 'silent_reading'
            level INTEGER,
            duration REAL, -- en segundos
            accuracy REAL, -- porcentaje de aciertos
            wpm REAL,      -- palabras por minuto (solo si aplica)
            total_chars INTEGER, -- caracteres totales procesados
            correct_chars INTEGER, -- caracteres correctos
            wrong_chars INTEGER -- caracteres incorrectos
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS letter_errors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER, -- Relaciona con la tabla sessions
            letter TEXT NOT NULL,
            mode TEXT NOT NULL, -- 'reading' (para voz fallida) o 'writing'
            count INTEGER DEFAULT 0,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    ''')
    conn.commit()
    conn.close()

def insert_vocabulary_batch(vocabulary_list):
    """
    Inserta una lista de tuplas de vocabulario en la tabla 'vocabulary'.
    Usa INSERT OR IGNORE para evitar duplicados.
    """
    conn = connect_db()
    cursor = conn.cursor()
    cursor.executemany('''INSERT OR IGNORE INTO vocabulary (hangul, roman, translation_en, level)
                          VALUES (?, ?, ?, ?)''', vocabulary_list)
    conn.commit()
    conn.close()

# --- Bloque de prueba (opcional para database.py, ya lo probamos con import_data) ---
if __name__ == "__main__":
    print("--- Probando database.py ---")
    create_tables()
    print("Tablas creadas/verificadas.")
    # Puedes añadir más pruebas aquí si lo deseas, pero el import_data.py
    # ya hace una buena prueba de create_tables y insert_vocabulary_batch.