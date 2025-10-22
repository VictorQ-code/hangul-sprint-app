# src/core_logic/stats.py

from data import database
import random
import datetime

def get_dashboard_summary():
    """
    Recupera y calcula las estadísticas principales para el dashboard.
    Si no hay sesiones previas, devuelve valores por defecto (0.0 y listas vacías).
    """
    conn = database.connect_db()
    cursor = conn.cursor()

    try:
        # Calcular velocidad media (wpm) de todas las sesiones de escritura/lectura (no silenciosas)
        cursor.execute("SELECT AVG(wpm) FROM sessions WHERE wpm IS NOT NULL")
        avg_wpm = cursor.fetchone()[0] or 0.0

        # Calcular precisión media (accuracy) de todas las sesiones
        cursor.execute("SELECT AVG(accuracy) FROM sessions")
        avg_accuracy = cursor.fetchone()[0] or 0.0

        # Obtener los 5 errores de escritura más frecuentes
        cursor.execute("SELECT letter, COUNT(letter) as count FROM letter_errors WHERE mode = 'writing' GROUP BY letter ORDER BY count DESC LIMIT 5")
        frequent_writing_errors_rows = cursor.fetchall()
        frequent_writing_errors = [{"letter": row["letter"], "count": row["count"]} for row in frequent_writing_errors_rows]

        # Obtener los 5 errores de lectura (voz) más frecuentes (frases fallidas)
        cursor.execute("SELECT letter, COUNT(letter) as count FROM letter_errors WHERE mode = 'reading' GROUP BY letter ORDER BY count DESC LIMIT 5")
        frequent_reading_errors_rows = cursor.fetchall()
        frequent_reading_errors = [{"hangul_phrase": row["letter"], "count": row["count"]} for row in frequent_reading_errors_rows]

    finally:
        conn.close()

    summary = {
        "avg_wpm": round(avg_wpm, 2),
        "avg_accuracy": round(avg_accuracy, 2),
        "frequent_writing_errors": frequent_writing_errors,
        "frequent_reading_errors": frequent_reading_errors
    }
    
    return summary

def get_practice_item(level=1):
    """
    Selecciona una frase/palabra aleatoria de la tabla 'vocabulary' para un nivel dado.
    """
    conn = database.connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM vocabulary WHERE level = ? ORDER BY RANDOM() LIMIT 1", (level,))
        item = cursor.fetchone()
    finally:
        conn.close()

    if item:
        return {
            "id": item["id"],
            "hangul": item["hangul"],
            "roman": item["roman"],
            "translation_en": item["translation_en"],
            "level": item["level"]
        }
    else:
        return None

def save_session_results(mode: str, level: int, duration: float, accuracy: float, 
                         total_chars: int, correct_chars: int, wrong_chars: int, 
                         wpm: float = None, letter_errors: list = None):
    """
    Guarda los resultados de una sesión de práctica en la base de datos.
    Relaciona los errores de letras con esta sesión.
    """
    conn = database.connect_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO sessions (mode, level, duration, accuracy, wpm, total_chars, correct_chars, wrong_chars)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (mode, level, duration, accuracy, wpm, total_chars, correct_chars, wrong_chars))
        
        session_id = cursor.lastrowid # Obtiene el ID de la sesión recién insertada
        
        if letter_errors:
            # Prepara los errores para inserción, vinculándolos con el session_id
            errors_to_insert = []
            for error_char_or_phrase in set(letter_errors): # Usamos set para insertar cada error único una vez por sesión
                # Determinamos el modo del error para la tabla letter_errors
                error_mode = 'writing' if mode == 'writing' else 'reading' # 'reading' cubre 'silent_reading' si es un error de frase
                errors_to_insert.append((session_id, error_char_or_phrase, error_mode, 1)) # count starts at 1 for this specific error in this session
            
            # Insertar múltiples errores de una vez
            cursor.executemany('''
                INSERT INTO letter_errors (session_id, letter, mode, count)
                VALUES (?, ?, ?, ?)
            ''', errors_to_insert)

        conn.commit()
        return session_id
    finally:
        conn.close()

# --- Bloque de prueba (ampliado) ---
if __name__ == '__main__':
    print("--- Probando el módulo de estadísticas ('stats.py') ---")
    
    # Asegúrate de que las tablas estén creadas y la base de datos poblada
    database.create_tables()
    # Si acabas de borrar la DB, ejecuta src/import_data.py para poblar 'vocabulary'

    print("\n1. Obteniendo resumen del Dashboard (valores iniciales/vacíos):")
    summary = get_dashboard_summary()
    print(f"   - Velocidad Media (WPM): {summary['avg_wpm']}")
    print(f"   - Precisión Media: {summary['avg_accuracy']}%")
    print(f"   - Errores Frecuentes de Escritura: {summary['frequent_writing_errors']}")
    print(f"   - Errores Frecuentes de Lectura (frases): {summary['frequent_reading_errors']}")

    print("\n2. Solicitando un item de práctica del Nivel 1:")
    item1 = get_practice_item(level=1)
    if item1:
        print(f"   - Éxito. Hangul: {item1['hangul']}")
    else:
        print("   - Fallo: No se encontraron items para el Nivel 1.")
    
    # --- PRUEBA NUEVA: Guardar una sesión de escritura ---
    print("\n3. Guardando una sesión de escritura de prueba:")
    # Simular una sesión de 30 segundos, 80% precisión, 50 WPM
    # Total 100 caracteres, 80 correctos, 20 incorrectos, con errores en 'ㅏ' y 'ㅐ'
    test_session_id_writing = save_session_results(
        mode='writing', 
        level=1, 
        duration=30.5, 
        accuracy=80.0, 
        wpm=50.2,
        total_chars=100,
        correct_chars=80,
        wrong_chars=20,
        letter_errors=['ㅏ', 'ㅐ', 'ㅓ', 'ㅏ'] # 'ㅏ' dos veces
    )
    print(f"   - Sesión de escritura guardada con ID: {test_session_id_writing}")

    # --- PRUEBA NUEVA: Guardar una sesión de lectura silenciosa (sin WPM) ---
    print("\n4. Guardando una sesión de lectura silenciosa de prueba:")
    # Simular una sesión de 15 segundos, 75% precisión, sin WPM
    test_session_id_silent = save_session_results(
        mode='silent_reading', 
        level=2, 
        duration=15.0, 
        accuracy=75.0,
        total_chars=50, # Puedes usar el número de palabras como total_chars para este modo si lo prefieres
        correct_chars=38,
        wrong_chars=12
    )
    print(f"   - Sesión de lectura silenciosa guardada con ID: {test_session_id_silent}")

    # --- PRUEBA NUEVA: Guardar una sesión de lectura (voz) con errores de frase ---
    print("\n5. Guardando una sesión de lectura (voz) con errores de frase:")
    # Simular una sesión de 25 segundos, 60% precisión, 40 WPM, con una frase fallida
    test_session_id_reading_voice = save_session_results(
        mode='reading', 
        level=1, 
        duration=25.0, 
        accuracy=60.0, 
        wpm=40.5,
        total_chars=70,
        correct_chars=42,
        wrong_chars=28,
        letter_errors=['안녕하세요?', '사랑해요'] # Frases que el usuario "falló" en voz
    )
    print(f"   - Sesión de lectura (voz) guardada con ID: {test_session_id_reading_voice}")


    print("\n6. Obteniendo resumen del Dashboard DESPUÉS de guardar sesiones:")
    summary_after_sessions = get_dashboard_summary()
    print(f"   - Velocidad Media (WPM) Actualizada: {summary_after_sessions['avg_wpm']}")
    print(f"   - Precisión Media Actualizada: {summary_after_sessions['avg_accuracy']}%")
    print(f"   - Errores Frecuentes de Escritura Actualizados: {summary_after_sessions['frequent_writing_errors']}")
    print(f"   - Errores Frecuentes de Lectura (frases) Actualizados: {summary_after_sessions['frequent_reading_errors']}")
    
    print("\n--- Pruebas de 'stats.py' completadas ---")