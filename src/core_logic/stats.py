# src/core_logic/stats.py (Versión Completa y Corregida)

from data import database # Asegúrate de que la importación sea relativa

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
            "hangul": item["kor_sent"],
            "roman": item["roman"],
            "translation_en": item["translation_en"],
            "level": item["level"]
        }
    else:
        return None

def get_short_practice_item(level=1, max_words=3):
    """
    Selecciona una frase/palabra aleatoria para un nivel dado, pero SOLO si
    no excede el número máximo de palabras especificado.
    """
    conn = database.connect_db()
    cursor = conn.cursor()
    try:
        # Consulta SQL para filtrar por longitud de palabras.
        query = f"""
            SELECT * FROM vocabulary 
            WHERE level = ? 
            AND (LENGTH(kor_sent) - LENGTH(REPLACE(kor_sent, ' ', '')) + 1) <= ?
            ORDER BY RANDOM() 
            LIMIT 1
        """
        cursor.execute(query, (level, max_words))
        item = cursor.fetchone()
    finally:
        conn.close()
    
    if item:
        return {
            "id": item["id"],
            "hangul": item["kor_sent"],
            "roman": item["roman"],
            "translation_en": item["translation_en"],
            "level": item["level"]
        }
    else:
        return None

def update_phrase_level(phrase_id, new_level):
    """
    Actualiza el nivel de una frase específica en la base de datos.
    """
    conn = database.connect_db()
    cursor = conn.cursor()
    try:
        query = "UPDATE vocabulary SET level = ? WHERE id = ?"
        cursor.execute(query, (new_level, phrase_id))
        conn.commit()
    except Exception as e:
        print(f"Error al actualizar el nivel de la frase: {e}")
    finally:
        conn.close()

# Aquí puedes añadir las otras funciones de stats que tenías, como
# get_dashboard_summary() y save_session_results() si las sigues usando.
# Si no las tienes, no te preocupes, la app principal funcionará sin ellas.