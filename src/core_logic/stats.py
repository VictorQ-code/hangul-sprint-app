# src/core_logic/stats.py (Versión Completa y Corregida)

# EN src/core_logic/stats.py
import sqlite3
import re
import os # Usaremos 'os' para construir la ruta a la DB de forma segura
from data import database # Asegúrate de que la importación sea relativa
import streamlit as st
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



@st.cache_data
def get_word_translation(word):
    """
    Busca la traducción de una palabra en la NUEVA tabla 'word_dictionary'.
    Esta es la versión final y correcta.
    """
    # Limpia la palabra de cualquier signo de puntuación
    clean_word = re.sub(r'[^\w\s]', '', word)
    if not clean_word:
        return ""

    # --- CAMPOS FINALES APUNTANDO A LA NUEVA TABLA ---
    
    # Construye la ruta a la base de datos
    DB_FILE = os.path.join("src", "data", "hangul_sprint.db")
    
    # Nombres de la nueva tabla y sus columnas
    TABLE_NAME = "word_dictionary"      # <-- ¡APUNTANDO A LA TABLA CORRECTA!
    HANGUL_COLUMN = "hangul_word"       # <-- La columna de palabras en la nueva tabla
    TRANS_COLUMN = "translation_en"     # <-- La columna de traducciones en la nueva tabla
    # ----------------------------------------------------

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Prepara la consulta para buscar la palabra en la nueva tabla
        query = f"SELECT {TRANS_COLUMN} FROM {TABLE_NAME} WHERE {HANGUL_COLUMN} = ?"
        
        cursor.execute(query, (clean_word,))
        
        result = cursor.fetchone()
        conn.close()

        if result:
            # Devuelve la traducción encontrada
            return result[0]
        else:
            # Este caso ya casi no debería ocurrir, pero es una buena salvaguarda
            return "Palabra no encontrada"

    except sqlite3.Error as e:
        print(f"Error de base de datos al buscar '{clean_word}': {e}")
        return "Error DB"
    """
    Busca la traducción de una palabra en la base de datos SQLite.
    Usa la tabla 'vocabulary' y las columnas correctas.
    """
    # Limpia la palabra de cualquier signo de puntuación común
    clean_word = re.sub(r'[^\w\s]', '', word)
    if not clean_word:
        return "" # Si la palabra solo era un signo de puntuación, no busques nada.

    # --- CAMPOS RELLENADOS SEGÚN TU IMAGEN ---
    
    # Construir la ruta al archivo de la base de datos de forma relativa y segura
    # Esto asume que el script se ejecuta desde la raíz del proyecto (APP_COREANO)
    DB_FILE = os.path.join("src", "data", "hangul_sprint.db")
    
    TABLE_NAME = "vocabulary"            # <-- Corregido de 'words' a 'vocabulary'
    HANGUL_COLUMN = "kor_sent"           # <-- Corregido de 'hangul' a 'kor_sent'
    TRANS_COLUMN = "translation_en"      # <-- Confirmado
    # ----------------------------------------------

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Prepara la consulta para buscar la palabra limpia
        # IMPORTANTE: Esto buscará una fila donde la columna 'kor_sent' sea EXACTAMENTE la palabra.
        # Es posible que no encuentre muchas coincidencias si 'kor_sent' siempre contiene frases largas.
        query = f"SELECT {TRANS_COLUMN} FROM {TABLE_NAME} WHERE {HANGUL_COLUMN} = ?"
        
        # Ejecuta la consulta
        cursor.execute(query, (clean_word,))
        
        result = cursor.fetchone()
        conn.close()

        if result:
            # Devuelve la traducción encontrada
            return result[0]
        else:
            # Si no se encuentra, devuelve este mensaje
            return "Traducción no disponible"

    except sqlite3.Error as e:
        print(f"Error de base de datos al buscar '{clean_word}': {e}")
        return "Error DB"
    """
    Busca la traducción de una palabra en la base de datos SQLite.
    Primero limpia la palabra de signos de puntuación.
    """
    # Limpia la palabra de cualquier signo de puntuación común
    clean_word = re.sub(r'[^\w\s]', '', word)
    if not clean_word:
        return "" # Si la palabra solo era un signo de puntuación, no busques nada.

    # --- ¡ADAPTA ESTOS NOMBRES A TU PROYECTO! ---
    DB_FILE = "hangul_db.sqlite"      # <-- Nombre de tu archivo de base de datos
    TABLE_NAME = "words"              # <-- Nombre de tu tabla de vocabulario
    HANGUL_COLUMN = "hangul"          # <-- Columna con las palabras en Hangul
    TRANS_COLUMN = "translation_en"   # <-- Columna con las traducciones
    # ----------------------------------------------

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Prepara la consulta para buscar la palabra limpia
        query = f"SELECT {TRANS_COLUMN} FROM {TABLE_NAME} WHERE {HANGUL_COLUMN} = ?"
        
        # Ejecuta la consulta
        cursor.execute(query, (clean_word,))
        
        result = cursor.fetchone()
        conn.close()

        if result:
            # Devuelve la traducción encontrada
            return result[0]
        else:
            # Si no se encuentra, devuelve este mensaje
            return "Traducción no disponible"

    except sqlite3.Error as e:
        print(f"Error de base de datos al buscar '{clean_word}': {e}")
        return "Error DB"
    """
    Busca la traducción de una sola palabra en la base de datos.
    Devuelve la traducción o un texto por defecto si no la encuentra.
    """
    # --- Lógica de ejemplo ---
    # Deberás adaptarla a cómo accedes a tu base de datos.
    # Por ejemplo, si usas un diccionario o una consulta SQL.
    
    # Ejemplo con un diccionario pre-cargado:
    # word_dictionary = load_word_dictionary_from_db()
    # return word_dictionary.get(word, "Traducción no encontrada.")

    # Ejemplo con una consulta directa (pseudocódigo):
    # result = database.query("SELECT translation_en FROM words WHERE hangul = ?", (word,))
    # if result:
    #     return result[0]['translation_en']
    # else:
    #     return "Traducción no encontrada."
    
    # --- Si no puedes implementarlo ahora, puedes dejarla así temporalmente ---
    return "Función de búsqueda no implementada."
