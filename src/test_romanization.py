import csv  # Librería estándar para leer CSV
import os   # Para manejar rutas
from korean_romanizer.romanizer import Romanizer  # ✅ Librería correcta para romanizar Hangul

def run_test():
    """
    Lee las primeras 5 líneas del CSV, romaniza las frases en coreano
    y muestra los resultados junto con la traducción en inglés.
    """
    print("--- Iniciando prueba de romanización ---")

    # Construye la ruta al archivo CSV
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'conversations.csv')

    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)

            # Lee la cabecera
            header = next(csv_reader)
            print(f"Cabecera del CSV: {header}")
            print("-" * 30)

            # Procesa solo las primeras 5 líneas
            for count, row in enumerate(csv_reader, start=1):
                if count > 5:
                    break

                # Ajusta índices según tu CSV (aquí se asume que kor_sent es la 3ª columna)
                kor_sent = row[2]
                eng_sent = row[3]

                # Romaniza la frase en coreano
                roman_sent = Romanizer(kor_sent).romanize()

                # Muestra los resultados
                print(f"Línea {count}:")
                print(f"  Coreano: {kor_sent}")
                print(f"  Romanizado: {roman_sent}")
                print(f"  Inglés: {eng_sent}\n")

    except FileNotFoundError:
        print(f"❌ ERROR: No se encontró el archivo en la ruta: {file_path}")
        print("Asegúrate de que 'conversations.csv' está guardado en la carpeta 'src/data/'.")

    print("--- Prueba completada ---")


if __name__ == "__main__":
    run_test()
