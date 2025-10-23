# import_new_data.py (Versión Corregida)

import pandas as pd
import os
from transformers import pipeline
# --- LÍNEA CORREGIDA ---
# La importación correcta es directamente desde la librería, no desde nuestro 'src'
from korean_romanizer.romanizer import Romanizer
# ---------------------
from src.data import database
import torch

# --- Configuración ---
CSV_FILE_PATH = "src/data/korean_webtext_sample.csv"
STARTING_LEVEL = 3
MAX_PHRASES_TO_PROCESS = 10000
BATCH_SIZE = 32

def import_new_phrases_to_db():
    print(f"Iniciando la importación y traducción desde: {CSV_FILE_PATH}")
    print(f"Se procesarán un máximo de {MAX_PHRASES_TO_PROCESS} frases.")

    # 1. Preparar el modelo de traducción
    try:
        # Forzar el uso de la CPU para evitar problemas con los drivers de la gráfica.
        device = -1
        print("Forzando el uso de la CPU para la traducción.")
        
        translator = pipeline("translation", model="Helsinki-NLP/opus-mt-ko-en", device=device)
        print("Modelo de traducción cargado con éxito.")

    except Exception as e:
        print(f"Error al cargar el modelo de traducción: {e}")
        print("Asegúrate de tener las librerías 'transformers', 'torch' y 'sentencepiece' instaladas.")
        return

    # 2. Asegurarse de que las tablas de la base de datos existen
    database.create_tables()

    # 3. Leer el CSV
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        df = df.head(MAX_PHRASES_TO_PROCESS)
        print(f"Se han leído {len(df)} frases del archivo CSV para procesar.")
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo en la ruta '{CSV_FILE_PATH}'.")
        return

    # 4. Procesar y traducir en lotes
    vocabulary_to_add = []
    korean_phrases = df['kor_sent'].dropna().astype(str).tolist()

    print(f"Iniciando traducción y romanización para {len(korean_phrases)} frases...")

    try:
        translated_results = translator(korean_phrases, batch_size=BATCH_SIZE)
        
        print("Traducción completada. Ahora procesando y romanizando...")
        
        for i in range(len(korean_phrases)):
            kor_sent = korean_phrases[i]
            translation_en = translated_results[i]['translation_text']
            roman_sent = Romanizer(kor_sent).romanize()
            level = STARTING_LEVEL
            
            vocabulary_to_add.append((kor_sent, roman_sent, translation_en, level))
            
            if (i + 1) % 500 == 0:
                print(f"  ... {i + 1} de {len(korean_phrases)} frases procesadas.")

    except Exception as e:
        print(f"Ha ocurrido un error durante el procesamiento por lotes: {e}")
        return

    print("Procesamiento completado.")

    # 5. Insertar los datos en la base de datos
    if vocabulary_to_add:
        print(f"Añadiendo {len(vocabulary_to_add)} nuevas frases a la base de datos...")
        database.insert_vocabulary_batch(vocabulary_to_add)
        print("¡Nuevas frases añadidas con éxito!")
    else:
        print("No se encontraron nuevas frases válidas para añadir.")

if __name__ == "__main__":
    import_new_phrases_to_db()