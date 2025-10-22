import csv
import os
from korean_romanizer.romanizer import Romanizer
# Importamos las funciones de nuestro módulo de base de datos
from .data import database 

def import_csv_to_db():
    """
    Lee el archivo conversations.csv, genera la romanización y lo guarda todo
    en la tabla 'vocabulary' de la base de datos SQLite.
    """
    print("--- Iniciando script de importación de datos ---")

    # 1. Asegurarse de que la base de datos y sus tablas existen
    database.create_tables()

    # 3. Preparar la lista para guardar los datos
    vocabulary_to_add = []
    
    # 4. Construir la ruta al archivo CSV
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'conversations.csv')

    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            # Saltamos la cabecera
            next(csv_reader)

            print("Leyendo archivo CSV y procesando frases...")
            
            current_level = 1
            conversation_count = 0
            
            for row in csv_reader:
                # Extraemos los datos necesarios
                kor_sent = row[2]
                eng_sent = row[3]
                
                # Pasamos el texto coreano directamente al crear el objeto Romanizer
                roman_sent = Romanizer(kor_sent).romanize() # <--- LÍNEA CORREGIDA
                
                # Lógica simple para asignar niveles: cada 20 conversaciones, sube un nivel
                conversation_id = int(row[1])
                if conversation_id == 1:
                    conversation_count += 1
                
                if conversation_count > 20:
                    current_level += 1
                    conversation_count = 1 # Reiniciamos el contador

                # Añadimos la tupla de datos a nuestra lista
                vocabulary_to_add.append((kor_sent, roman_sent, eng_sent, current_level))

        # 5. Insertar todos los datos en la base de datos de una sola vez
        if vocabulary_to_add:
            print(f"Procesadas {len(vocabulary_to_add)} frases. Insertando en la base de datos...")
            database.insert_vocabulary_batch(vocabulary_to_add)
            print("¡Datos importados con éxito a la tabla 'vocabulary'!")
        else:
            print("No se encontraron nuevos datos para añadir.")

    except FileNotFoundError:
        print(f"ERROR: No se encontró 'conversations.csv' en la ruta: {file_path}")
    except Exception as e:
        print(f"Ha ocurrido un error inesperado: {e}")

    print("--- Script de importación finalizado ---")


if __name__ == "__main__":
    import_csv_to_db()