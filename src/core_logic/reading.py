# src/core_logic/reading.py
import time
import random
from core_logic import stats
from core_logic.timer import Timer

def start_reading_session(level=1):
    """
    Prepara una nueva sesión de lectura.
    1. Obtiene UN item de práctica con todos sus datos.
    2. Genera 3 opciones de respuesta falsas (distractores).
    """
    item = stats.get_practice_item(level)
    
    if not item:
        return {"error": f"No se encontraron frases para el nivel {level}."}

    # ---- LÓGICA SIMPLIFICADA ----
    # Ya tenemos la respuesta correcta directamente.
    correct_answer = item['roman']
    
    # Para los señuelos (decoys), seguimos necesitando otras romanizaciones.
    # La lógica de obtenerlas puede permanecer, pero ahora el punto de partida es más simple.
    decoys = []
    attempts = 0
    max_attempts = 10 
    all_romans = [correct_answer] # Evitar duplicados
    
    while len(decoys) < 3 and attempts < max_attempts:
        decoy_item = stats.get_practice_item(level)
        # Asegurarnos de que el señuelo no sea la respuesta correcta
        if decoy_item and decoy_item['roman'] not in all_romans:
            decoys.append(decoy_item['roman'])
            all_romans.append(decoy_item['roman'])
        attempts += 1

    options = decoys + [correct_answer]
    random.shuffle(options)

    # Devolvemos el item completo, que ahora contiene la traducción también.
    return {
        "practice_item": item,
        "silent_mode_options": options,
        "error": None
    }
    """
    Prepara una nueva sesión de lectura.
    1. Obtiene un item de práctica de la base de datos.
    2. Para el modo silencioso, genera 3 opciones de respuesta falsas.
    Devuelve un diccionario con toda la información necesaria para la UI.
    """
    item = stats.get_practice_item(level)
    
    if not item:
        return {"error": f"No se encontraron frases para el nivel {level}."}

    # Lógica para el "Silent Mode": crear opciones múltiples
    correct_answer = item['roman']
    
    # Tomamos otras 3 frases aleatorias para usar sus romanizaciones como señuelos
    decoys = []
    # Asegurarse de que el bucle no sea infinito si no hay suficientes items para señuelos
    attempts = 0
    max_attempts = 10 # Limite de intentos para evitar bucles infinitos
    all_romans = [item['roman']] # Para evitar duplicados en los señuelos
    
    while len(decoys) < 3 and attempts < max_attempts:
        decoy_item = stats.get_practice_item(level)
        if decoy_item and decoy_item['roman'] not in all_romans:
            decoys.append(decoy_item['roman'])
            all_romans.append(decoy_item['roman'])
        attempts += 1

    # Si no se pudieron generar 3 señuelos, seguimos con los que tengamos
    options = decoys + [correct_answer]
    random.shuffle(options)

    # Devolvemos un paquete de datos listo para que la UI lo muestre
    return {
        "practice_item": item,
        "silent_mode_options": options,
        "error": None
    }

def calculate_reading_accuracy(expected_text: str, recognized_text: str):
    """
    Calcula la precisión de la lectura por voz (modo hablado).
    Compara palabra por palabra y también devuelve la lista de palabras fallidas.
    """
    expected_words = expected_text.strip().lower().split()
    recognized_words = recognized_text.strip().lower().split()
    
    if not expected_words:
        return {"accuracy": 0.0, "correct_count": 0, "total_count": 0, "wrong_words": []}

    correct_count = 0
    wrong_words = []

    for i in range(max(len(expected_words), len(recognized_words))):
        exp_word = expected_words[i] if i < len(expected_words) else ""
        rec_word = recognized_words[i] if i < len(recognized_words) else ""

        if exp_word == rec_word and exp_word != "":
            correct_count += 1
        elif exp_word != "": # Si hay una palabra esperada y no coincide
            wrong_words.append(exp_word)
        elif rec_word != "": # Si hay una palabra reconocida extra
             pass # No la contamos como error de la 'expected_text' per se, pero es un fallo

    total_expected_words = len(expected_words)
    accuracy = (correct_count / total_expected_words) * 100 if total_expected_words > 0 else 0.0
    
    return {
        "accuracy": round(accuracy, 2),
        "correct_count": correct_count,
        "total_count": total_expected_words,
        "wrong_words": list(set(wrong_words)) # Eliminar duplicados
    }

def end_reading_session_and_save(mode: str, level: int, timer: Timer, 
                                  correct_phrases: int, total_phrases: int, 
                                  wpm: float = None, failed_phrases: list = None):
    """
    Finaliza una sesión de lectura (silent_reading o reading) y guarda los resultados.
    Calcula la duración y la precisión global.
    """
    duration = timer.stop()
    accuracy = (correct_phrases / total_phrases) * 100 if total_phrases > 0 else 0.0
    
    total_chars_in_session = 0 # Tendríamos que acumular esto durante la sesión
    correct_chars_in_session = 0 # Tendríamos que acumular esto durante la sesión
    wrong_chars_in_session = 0 # Tendríamos que acumular esto durante la sesión
    
    # Para el propósito de guardar, podemos simplificar total_chars/correct_chars/wrong_chars
    # en base a las frases para lectura, o dejar en 0 si la UI no los proporciona aún.
    # Por ahora, un placeholder simple:
    total_chars_in_session = total_phrases * 10 # Estimado de 10 caracteres/frase
    correct_chars_in_session = int(total_chars_in_session * (accuracy / 100))
    wrong_chars_in_session = total_chars_in_session - correct_chars_in_session

    session_id = stats.save_session_results(
        mode=mode,
        level=level,
        duration=duration,
        accuracy=accuracy,
        wpm=wpm, # Puede ser None para silent_reading
        total_chars=total_chars_in_session,
        correct_chars=correct_chars_in_session,
        wrong_chars=wrong_chars_in_session,
        letter_errors=failed_phrases # Aquí pasamos las frases fallidas (modo voz)
    )
    return {"session_id": session_id, "duration": duration, "accuracy": accuracy}


# --- Bloque de prueba (ampliado) ---
if __name__ == '__main__':
    print("--- Probando el módulo de lectura ('reading.py') ---")

    # 1. Simular el inicio de una sesión de lectura silenciosa
    print("\n1. Iniciando y finalizando una mini-sesión de lectura silenciosa (Nivel 2):")
    session_timer = Timer()
    session_timer.start()
    
    total_silent_phrases = 0
    correct_silent_phrases = 0
    
    # Simular 3 rondas
    for i in range(3):
        item_data = start_reading_session(level=2)
        if not item_data.get("error"):
            item = item_data['practice_item']
            options = item_data['silent_mode_options']
            
            # Simular respuesta del usuario
            user_choice = random.choice(options) # Elegimos al azar
            total_silent_phrases += 1
            if user_choice == item['roman']:
                correct_silent_phrases += 1
                print(f"   - Ronda {i+1} Correcta. Frase: '{item['hangul']}'")
            else:
                print(f"   - Ronda {i+1} Incorrecta. Frase: '{item['hangul']}'")
        else:
            print(f"   - Error en ronda {i+1}: {item_data['error']}")

    time.sleep(1) # Simular algo de tiempo
    
    # Finalizar y guardar la sesión silenciosa
    session_results = end_reading_session_and_save(
        mode='silent_reading',
        level=2,
        timer=session_timer,
        correct_phrases=correct_silent_phrases,
        total_phrases=total_silent_phrases,
        failed_phrases=[] # No hay errores de caracteres/frases específicas para este modo
    )
    print(f"   - Sesión silenciosa finalizada. ID: {session_results['session_id']}, Duración: {session_results['duration']}s, Precisión: {session_results['accuracy']}%")


    # 2. Simular el inicio de una sesión de lectura por voz
    print("\n\n2. Iniciando y finalizando una mini-sesión de lectura por voz (Nivel 1):")
    voice_session_timer = Timer()
    voice_session_timer.start()

    total_voice_phrases = 0
    correct_voice_phrases = 0
    failed_voice_phrases = []

    # Simular 2 rondas de lectura por voz
    for i in range(2):
        item_data = start_reading_session(level=1)
        if not item_data.get("error"):
            item = item_data['practice_item']
            total_voice_phrases += 1
            
            # Simular reconocimiento de voz
            expected_hangul = item['hangul']
            recognized_hangul = expected_hangul
            if i == 0: # Hacer la primera correcta
                pass
            else: # Hacer la segunda incorrecta
                recognized_hangul = recognized_hangul.replace('다', '따', 1) if '다' in recognized_hangul else "잘못된 문장"
            
            accuracy_result = calculate_reading_accuracy(expected_hangul, recognized_hangul)
            
            if accuracy_result['accuracy'] >= 70.0: # Umbral para considerar "correcto"
                correct_voice_phrases += 1
                print(f"   - Ronda {i+1} Correcta. Frase: '{expected_hangul}'")
            else:
                failed_voice_phrases.append(expected_hangul) # Registramos la frase fallida
                print(f"   - Ronda {i+1} Incorrecta. Frase: '{expected_hangul}', Precisión: {accuracy_result['accuracy']}%")
        else:
            print(f"   - Error en ronda {i+1}: {item_data['error']}")
    
    time.sleep(1.5) # Simular algo de tiempo

    # Finalizar y guardar la sesión de lectura por voz
    voice_session_results = end_reading_session_and_save(
        mode='reading',
        level=1,
        timer=voice_session_timer,
        correct_phrases=correct_voice_phrases,
        total_phrases=total_voice_phrases,
        wpm=45.5, # Simular WPM para este modo
        failed_phrases=failed_voice_phrases
    )
    print(f"   - Sesión de lectura por voz finalizada. ID: {voice_session_results['session_id']}, Duración: {voice_session_results['duration']}s, Precisión: {voice_session_results['accuracy']}%")

    print("\n--- Pruebas de 'reading.py' completadas ---")