import pandas as pd
import os
from .data import database # Importamos desde el mismo directorio

def import_csv_to_db():
    """
    Lee el archivo korean_webtext_FINAL_clean.csv usando pandas y lo guarda
    en la tabla 'vocabulary' de la base de datos.
    Esta versión es más rápida y simple, ya que el CSV contiene todos los datos necesarios.
    """
    print("--- Iniciando nuevo script de importación de datos ---")

    # 1. Asegurarse de que la base de datos y sus tablas existen (con la nueva estructura)
    database.create_tables()

    # 2. Define el nombre de tu nuevo archivo CSV
    csv_filename = 'korean_webtext_FINAL_clean.csv'
    
    # 3. Construir la ruta al archivo CSV (asumiendo que está en una carpeta 'data' al mismo nivel que 'core_logic')
    # Ajusta la ruta si tu estructura de carpetas es diferente.
    # Por ejemplo, si está en '../data/' o en el mismo directorio.
    # CÓDIGO NUEVO Y CORREGIDO
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', csv_filename)

    try:
        print(f"Leyendo el archivo CSV desde: {file_path}")
        # Usamos pandas para leer el CSV, es muy eficiente
        df = pd.read_csv(file_path)

        # 4. Verificar que las columnas necesarias existen
        required_columns = ['kor_sent', 'roman', 'translation_en', 'level']
        if not all(col in df.columns for col in required_columns):
            print(f"Error: El CSV debe contener las columnas: {required_columns}")
            return
            
        # 5. Seleccionar solo las columnas que queremos insertar en la base de datos
        df_to_insert = df[required_columns]

        # 6. Convertir el DataFrame a una lista de tuplas, que es lo que espera nuestra función de base de datos
        vocabulary_to_add = df_to_insert.to_records(index=False).tolist()

        # 7. Insertar todos los datos en la base de datos de una sola vez
        if vocabulary_to_add:
            print(f"Procesadas {len(vocabulary_to_add)} frases. Insertando en la base de datos (esto puede tardar un poco)...")
            database.insert_vocabulary_batch(vocabulary_to_add)
            print("¡Datos importados con éxito a la tabla 'vocabulary'!")
        else:
            print("El CSV estaba vacío o no se encontraron datos para añadir.")

    except FileNotFoundError:
        print(f"ERROR: No se encontró el archivo '{csv_filename}' en la ruta: {file_path}")
        print("Asegúrate de que la ruta y el nombre del archivo son correctos.")
    except Exception as e:
        print(f"Ha ocurrido un error inesperado: {e}")

    print("--- Script de importación finalizado ---")

if __name__ == "__main__":
    import_csv_to_db()