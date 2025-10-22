# src/core_logic/writing.py
import time
from core_logic import stats
from core_logic.timer import Timer

def start_writing_session(level=1):
    """
    Prepara una nueva sesión de escritura.
    Solo necesita obtener un item.
    """
    item = stats.get_practice_item(level)
    
    if not item:
        return {"error": f"No se encontraron frases para el nivel {level}."}
        
    return {
        "practice_item": item,
        "error": None
    }

def calculate_writing_accuracy(expected_hangul: str, user_hangul: str):
    """
    Calcula la precisión de la escritura y devuelve los caracteres erróneos.
    Compara carácter por carácter.
    """
    expected = expected_hangul.strip()
    user = user_hangul.strip()
    
    correct_chars = 0
    wrong_chars = 0
    error_chars_list = [] # Lista de caracteres que fueron fallados en la entrada del usuario
    
    # Recorremos hasta el final del texto esperado o del texto de usuario, el que sea más largo.
    # Esto ayuda a detectar caracteres omitidos o caracteres extra.
    for i in range(max(len(expected), len(user))):
        expected_char = expected[i] if i < len(expected) else ''
        user_char = user[i] if i < len(user) else ''
        
        if expected_char == user_char and expected_char != '':
            correct_chars += 1
        else:
            wrong_chars += 1
            if expected_char != '': # Si había un carácter esperado que se falló
                error_chars_list.append(expected_char)
            # No agregamos caracteres extra del usuario a error_chars_list aquí,
            # ya que la lista es para "qué caracteres se espera que escriba y falló".
            # La cuenta de wrong_chars sí los incluye.

    total_expected_chars = len(expected)
    accuracy = (correct_chars / total_expected_chars) * 100 if total_expected_chars > 0 else 0.0
    
    return {
        "accuracy": round(accuracy, 2),
        "correct_chars": correct_chars,
        "wrong_chars": wrong_chars,
        "total_chars": total_expected_chars,
        "error_chars": list(set(error_chars_list)) # Devolver caracteres únicos fallados
    }

def end_writing_session_and_save(level: int, timer: Timer, 
                                  total_phrases: int, correct_phrases: int, 
                                  total_chars_in_session: int, correct_chars_in_session: int,
                                  wrong_chars_in_session: int,
                                  all_failed_chars_in_session: list):
    """
    Finaliza una sesión de escritura y guarda los resultados.
    Calcula la duración, precisión global y WPM.
    """
    duration = timer.stop()
    accuracy = (correct_chars_in_session / total_chars_in_session) * 100 if total_chars_in_session > 0 else 0.0
    
    # Calcular WPM (palabras por minuto). Asumimos 5 caracteres por palabra en Hangul como estándar
    # Puedes ajustar este factor si tienes una métrica mejor
    words_written = correct_chars_in_session / 5 
    wpm = (words_written / duration) * 60 if duration > 0 else 0.0

    session_id = stats.save_session_results(
        mode='writing',
        level=level,
        duration=duration,
        accuracy=accuracy,
        wpm=round(wpm, 2),
        total_chars=total_chars_in_session,
        correct_chars=correct_chars_in_session,
        wrong_chars=wrong_chars_in_session,
        letter_errors=all_failed_chars_in_session # Aquí pasamos todos los caracteres fallidos
    )
    return {"session_id": session_id, "duration": duration, "accuracy": accuracy, "wpm": round(wpm, 2)}


# --- Bloque de prueba (ampliado) ---
if __name__ == '__main__':
    print("--- Probando el módulo de escritura ('writing.py') ---")
    
    # 1. Simular el inicio de una sesión de escritura
    print("\n1. Iniciando y finalizando una mini-sesión de escritura (Nivel 1):")
    session_timer = Timer()
    session_timer.start()
    
    total_writing_phrases = 0
    correct_writing_phrases = 0
    
    # Acumuladores para la sesión
    total_chars_accumulated = 0
    correct_chars_accumulated = 0
    wrong_chars_accumulated = 0
    all_failed_chars_for_session = []

    # Simular 3 rondas
    for i in range(3):
        item_data = start_writing_session(level=1)
        if not item_data.get("error"):
            item = item_data['practice_item']
            total_writing_phrases += 1
            
            # Simular respuesta del usuario
            expected_hangul = item['hangul']
            user_input = expected_hangul
            
            if i == 0: # Ronda correcta
                pass
            elif i == 1: # Ronda con un error específico
                user_input = expected_hangul.replace('세', '새', 1) if '세' in expected_hangul else expected_hangul + 'x'
            else: # Ronda con múltiples errores
                user_input = expected_hangul.replace('다', '따', 1).replace('가', '카', 1) if '다' in expected_hangul and '가' in expected_hangul else '엉터리'

            result = calculate_writing_accuracy(expected_hangul, user_input)
            
            total_chars_accumulated += result['total_chars']
            correct_chars_accumulated += result['correct_chars']
            wrong_chars_accumulated += result['wrong_chars']
            all_failed_chars_for_session.extend(result['error_chars']) # Acumular los caracteres fallados

            if result['accuracy'] == 100.0:
                correct_writing_phrases += 1
                print(f"   - Ronda {i+1} Correcta. Frase: '{expected_hangul}'")
            else:
                print(f"   - Ronda {i+1} Incorrecta. Frase: '{expected_hangul}', Precisión: {result['accuracy']}%, Errores: {result['error_chars']}")
        else:
            print(f"   - Error en ronda {i+1}: {item_data['error']}")
    
    time.sleep(1.5) # Simular algo de tiempo

    # Finalizar y guardar la sesión de escritura
    session_results = end_writing_session_and_save(
        level=1,
        timer=session_timer,
        total_phrases=total_writing_phrases,
        correct_phrases=correct_writing_phrases,
        total_chars_in_session=total_chars_accumulated,
        correct_chars_in_session=correct_chars_accumulated,
        wrong_chars_in_session=wrong_chars_accumulated,
        all_failed_chars_in_session=all_failed_chars_for_session
    )
    print(f"   - Sesión de escritura finalizada. ID: {session_results['session_id']}, Duración: {session_results['duration']}s, Precisión: {session_results['accuracy']}%, WPM: {session_results['wpm']}")
        
    print("\n--- Pruebas de 'writing.py' completadas ---")