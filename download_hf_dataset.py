# download_hf_dataset.py

# 1. Importar las librerías necesarias
from datasets import load_dataset
import pandas as pd
import os

# 2. Configuración
DATASET_NAME = "HAERAE-HUB/KOREAN-WEBTEXT"
CSV_OUTPUT_PATH = "src/data/korean_webtext_sample.csv"
NUM_SAMPLES = 5000  # ¡Vamos a descargar solo las primeras 5000 filas!

print(f"Preparando para descargar una muestra de '{DATASET_NAME}'...")

try:
    # 3. Descargar el dataset en modo 'streaming' para no bajar los 10GB.
    # Esto nos permite tomar solo una pequeña parte del principio.
    dataset = load_dataset(DATASET_NAME, split='train', streaming=True)
    
    # 4. Tomar las primeras NUM_SAMPLES filas del dataset
    sample = dataset.take(NUM_SAMPLES)
    
    # Convertir la muestra a una lista de diccionarios
    sample_list = list(sample)
    
    print(f"Muestra de {len(sample_list)} filas descargada con éxito.")
    
    # 5. Convertir la muestra a un DataFrame de Pandas
    df = pd.DataFrame(sample_list)
    
    print("\nConversión a DataFrame de Pandas exitosa.")
    print("Estas son las 5 primeras filas de la muestra:")
    print(df.head())
    
    print("\nColumnas disponibles en el dataset:")
    print(df.columns)
    
    # 6. Seleccionar y renombrar las columnas que nos interesan
    # En este caso, la columna 'text' parece ser la más útil.
    # Vamos a crear un CSV limpio solo con esa columna para empezar.
    if 'text' in df.columns:
        # La columna 'text' contiene textos largos, vamos a dividirlos en frases (oraciones)
        all_sentences = []
        for text_block in df['text']:
            # Dividir por punto y limpiar espacios. Filtramos las frases cortas.
            sentences = [s.strip() for s in text_block.split('.') if len(s.strip()) > 3]
            all_sentences.extend(sentences)

        print(f"\nSe extrajeron {len(all_sentences)} frases de los {len(df)} bloques de texto.")

        # Crear un nuevo DataFrame solo con las frases
        final_df = pd.DataFrame(all_sentences, columns=['kor_sent'])

        # 7. Guardar el DataFrame final como un archivo CSV
        final_df.to_csv(CSV_OUTPUT_PATH, index=False, encoding='utf-8-sig')
        
        print(f"\n¡Éxito! Se ha guardado un CSV con {len(final_df)} frases en: {CSV_OUTPUT_PATH}")
    else:
        print("\nError: No se encontró la columna 'text' en el dataset.")

except Exception as e:
    print(f"\nHa ocurrido un error: {e}")
    print("Asegúrate de tener conexión a internet y de que las librerías 'datasets' y 'pandas' están instaladas.")