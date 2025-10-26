# src/streamlit_app.py (Versión final completa con los 3 modos funcionales)

import streamlit as st
import time
import pandas as pd
import re
import random
# --- AVISO: Asegúrate de que estos módulos existen en tu proyecto ---
from core_logic import stats
from korean_romanizer.romanizer import Romanizer

# --- CONFIGURACIÓN INICIAL ---
LEVEL_MAP = {
    1: "Principiante", 2: "Intermedio", 3: "Maestro", 4: "Leyenda",
    5: "Nivel 5", 6: "Nivel 6", 7: "Nivel 7", 8: "Nivel 8", 9: "Nivel 9", 10: "Nivel 10"
}
st.set_page_config(page_title="Hangul Sprint", layout="wide")


# --- FUNCIONES HELPER ---
def generar_texto_con_tooltips(datos_texto):
    """Genera una cadena HTML con tooltips para cada palabra/frase."""
    css_string = """
    <style>
        .tooltip {
          position: relative; display: inline-block; border-bottom: 1px dotted #999;
          cursor: help; font-size: 22px; margin: 0 3px; line-height: 2.0;
        }
        .tooltip .tooltiptext {
          visibility: hidden; width: 240px; background-color: #333; color: #fff;
          text-align: left; border-radius: 6px; padding: 10px; position: absolute;
          z-index: 1; bottom: 140%; left: 50%; margin-left: -120px; opacity: 0;
          transition: opacity 0.2s; font-size: 16px;
        }
        .tooltip .tooltiptext b { color: #5DADE2; }
        .tooltip:hover .tooltiptext { visibility: visible; opacity: 1; }
    </style>
    """
    html_body = ""
    for item in datos_texto:
        hangul = item.get('hangul', '')
        roman = item.get('roman', 'N/A')
        translation = item.get('trans', 'Traducción no disponible.')
        tooltip_content = f"<b>{roman}</b><br>{translation}"
        html_body += f'<div class="tooltip">{hangul}<span class="tooltiptext">{tooltip_content}</span></div>'
    return css_string + f"<div style='text-align: justify;'>{html_body}</div>"


# En streamlit_app.py, reemplaza la función get_long_text_data_from_db con esta

def get_long_text_data_from_db(level):
    st.info(f"Cargando un texto para el Nivel {level}...")
    item_largo = stats.get_practice_item(level=level)

    if not item_largo or 'hangul' not in item_largo:
        st.error(f"No se encontraron textos para el Nivel {level}.")
        st.session_state.deep_read_full_translation = "No disponible."
        return []

    long_text_string = item_largo['hangul']
    st.session_state.deep_read_full_translation = item_largo.get('translation_en', 'Traducción no disponible.')
    
    words = long_text_string.split()
    processed_text_data = []

    for word in words:
        clean_word = re.sub(r'[^\w\s]', '', word)
        romanized_word = Romanizer(clean_word).romanize()
        
        # --- ¡ESTE ES EL CAMBIO CLAVE! ---
        # Ahora llamamos a la función que busca la traducción de cada palabra.
        word_translation = stats.get_word_translation(clean_word) # <-- USAMOS LA NUEVA FUNCIÓN

        processed_text_data.append({
            'hangul': word,
            'roman': romanized_word,
            'trans': word_translation # <-- AHORA TENDRÁ LA TRADUCCIÓN REAL
        })
            
    return processed_text_data
    """
    Esta es la nueva versión que reutiliza la lógica existente.
    1. Obtiene UN item (una frase larga) del nivel especificado.
    2. Procesa esa frase palabra por palabra para los tooltips.
    """
    
    # 1. OBTENER UNA FRASE LARGA USANDO TU FUNCIÓN EXISTENTE
    #    Asegúrate de que el nombre 'stats.get_practice_item' es correcto.
    #    Este item debería contener al menos la clave 'hangul'.
    
    st.info(f"Cargando un texto para el Nivel {level}...")
    item_largo = stats.get_practice_item(level=level)

    if not item_largo or 'hangul' not in item_largo:
        st.error(f"No se encontraron textos para el Nivel {level} en la base de datos.")
        # Guardamos None para que la interfaz sepa que no hay texto
        st.session_state.deep_read_full_translation = "No disponible."
        return []

    long_text_string = item_largo['hangul']
    # Guardamos la traducción completa de la frase para mostrarla después
    st.session_state.deep_read_full_translation = item_largo.get('translation_en', 'Traducción no disponible.')

    # 2. DIVIDIR LA FRASE EN PALABRAS
    words = long_text_string.split()

    # 3. PROCESAR CADA PALABRA PARA CREAR LA LISTA PARA LOS TOOLTIPS
    processed_text_data = []
    for word in words:
        # Limpiamos la palabra de puntuación para una mejor romanización
        clean_word = re.sub(r'[^\w\s]', '', word)
        
        # Usamos la librería Romanizer sobre la marcha
        romanized_word = Romanizer(clean_word).romanize()
        
        # Como no tenemos una función para buscar traducciones de palabras sueltas,
        # lo dejamos como no disponible por ahora. ¡Esto se puede mejorar en el futuro!
        word_translation = "Traducción de palabra no disponible."

        processed_text_data.append({
            'hangul': word,  # Usamos la palabra original con puntuación para mostrarla
            'roman': romanized_word,
            'trans': word_translation
        })
            
    # 4. DEVOLVER LA LISTA FINAL CON EL TEXTO LARGO PROCESADO
    return processed_text_data
    """
    Esta es la nueva versión que se conecta a tu base de datos real.
    Obtiene un texto largo y lo procesa para el modo de lectura profunda.
    """
    
    # 1. Obtener un texto largo de la base de datos para el nivel seleccionado
    #    Asumo que tienes una función para esto. El resultado es un string.
    #    Ejemplo: "한국어를 공부하는 것은 아주 재미있습니다."
    long_text_string = stats.get_random_long_text_by_level(level) # <-- ¡Adapta este nombre de función!

    if not long_text_string:
        st.error(f"No se encontraron textos largos para el Nivel {level} en la base de datos.")
        return []

    # 2. Dividir el texto largo en palabras individuales
    words = long_text_string.split() # -> ['한국어를', '공부하는', '것은', ...]

    # 3. Crear la lista de diccionarios que necesita la interfaz
    processed_text_data = []
    for word in words:
        # Para cada palabra, obtén su romanización y traducción desde la DB
        # Asumo que tienes una función que puede buscar una palabra.
        word_details = stats.get_word_details(word) # <-- ¡Adapta este nombre de función!

        if word_details:
            processed_text_data.append({
                'hangul': word,
                'roman': word_details.get('roman', 'N/A'),
                'trans': word_details.get('translation_en', 'No disponible')
            })
        else:
            # Si una palabra no se encuentra en tu diccionario, la añadimos igualmente
            # para no romper el texto, pero con datos por defecto.
            processed_text_data.append({
                'hangul': word,
                'roman': '?',
                'trans': 'Palabra no encontrada en el diccionario.'
            })
            
    # 4. Devolver la lista final, que ahora contiene tu texto largo real
    return processed_text_data
    """
    FUNCIÓN DE EJEMPLO - REEMPLAZAR CON TU LÓGICA DE BASE DE DATOS.
    Simula la obtención de un texto largo y sus datos palabra por palabra.
    """
    st.info(f"Cargando un texto aleatorio para el Nivel {level}...")
    time.sleep(0.5)

    ejemplo_lvl_4 = [
        {'hangul': '한국어를', 'roman': 'hangugeo-reul', 'trans': 'El idioma coreano (objeto)'},
        {'hangul': '공부하는', 'roman': 'gongbuhaneun', 'trans': 'Estudiar (forma adjetival)'},
        {'hangul': '것은', 'roman': 'geoseun', 'trans': 'El acto de (sujeto)'},
        {'hangul': '아주', 'roman': 'aju', 'trans': 'Muy'},
        {'hangul': '재미있습니다.', 'roman': 'jaemi-isseumnida.', 'trans': 'es divertido (formal).'}
    ]
    ejemplo_lvl_8 = [
        {'hangul': '오늘', 'roman': 'oneul', 'trans': 'Hoy'},
        {'hangul': '저녁에', 'roman': 'jeonyeoge', 'trans': 'en la tarde/noche'},
        {'hangul': '친구와', 'roman': 'chinguwa', 'trans': 'con un amigo'},
        {'hangul': '함께', 'roman': 'hamkke', 'trans': 'juntos'},
        {'hangul': '영화를', 'roman': 'yeonghwareul', 'trans': 'una película (objeto)'},
        {'hangul': '보러', 'roman': 'boreo', 'trans': 'para ver'},
        {'hangul': '갈', 'roman': 'gal', 'trans': 'ir (futuro)'},
        {'hangul': '계획입니다.', 'roman': 'gyehwegimnida.', 'trans': 'es el plan.'}
    ]
    # Elige un texto aleatorio para hacerlo más dinámico
    if random.choice([True, False]):
        return ejemplo_lvl_4 if level <= 7 else ejemplo_lvl_8
    else:
        return ejemplo_lvl_8 if level > 5 else ejemplo_lvl_4


# --- INICIALIZACIÓN COMPLETA DEL ESTADO DE SESIÓN ---
# General
if 'page' not in st.session_state: st.session_state.page = "Leer"
# Modo Leer
if 'reading_level' not in st.session_state: st.session_state.reading_level = 1
if 'practice_in_progress' not in st.session_state: st.session_state.practice_in_progress = False
if 'practice_text_info' not in st.session_state: st.session_state.practice_text_info = None
if 'timer_running' not in st.session_state: st.session_state.timer_running = False
if 'start_time' not in st.session_state: st.session_state.start_time = 0
if 'elapsed_time' not in st.session_state: st.session_state.elapsed_time = 0
if 'selected_word' not in st.session_state: st.session_state.selected_word = None
if 'session_history' not in st.session_state: st.session_state.session_history = []
# Modo Romanización
if 'romanization_level' not in st.session_state: st.session_state.romanization_level = 1
if 'romanization_practice_in_progress' not in st.session_state: st.session_state.romanization_practice_in_progress = False
if 'romanization_questions' not in st.session_state: st.session_state.romanization_questions = []
if 'current_question_index' not in st.session_state: st.session_state.current_question_index = 0
if 'user_answers' not in st.session_state: st.session_state.user_answers = []
# Modo Lectura Profunda
if 'deep_read_in_progress' not in st.session_state: st.session_state.deep_read_in_progress = False
if 'deep_read_level' not in st.session_state: st.session_state.deep_read_level = 4
if 'deep_read_text_data' not in st.session_state: st.session_state.deep_read_text_data = None
if 'deep_read_start_time' not in st.session_state: st.session_state.deep_read_start_time = 0
if 'deep_read_elapsed_time' not in st.session_state: st.session_state.deep_read_elapsed_time = 0


# --- FUNCIONES LÓGICAS PRINCIPALES ---
def load_new_reading_item(attempt_count=0):
    MAX_WORDS_FOR_READING, MAX_ATTEMPTS = 10, 10
    if attempt_count >= MAX_ATTEMPTS:
        st.error("No se pudo encontrar una frase adecuada."); st.session_state.practice_text_info = None; return
    item = stats.get_practice_item(level=st.session_state.reading_level)
    if item:
        if len(item['hangul'].split()) > MAX_WORDS_FOR_READING:
            stats.update_phrase_level(item['id'], 5); load_new_reading_item(attempt_count + 1)
        else:
            st.session_state.practice_text_info = item; st.session_state.timer_running = False; st.session_state.start_time = 0; st.session_state.elapsed_time = 0; st.session_state.selected_word = None
    else:
        st.session_state.practice_text_info = None; st.error(f"No se encontraron textos para el nivel {st.session_state.reading_level}.")

def generate_distractors(correct_romanization):
    distractors = set(); swaps = {'eo': 'o', 'o': 'eo', 'eu': 'u', 'u': 'eu', 'ae': 'e', 'e': 'ae', 'g': 'k', 'k': 'g', 'd': 't', 't': 'd', 'b': 'p', 'p': 'b', 'j': 'ch', 'ch': 'j', 'r': 'l', 'l': 'r'}
    attempts = 0
    while len(distractors) < 3 and attempts < 50:
        new_roman = list(correct_romanization); attempts += 1
        if not new_roman: break
        idx = random.randint(0, len(new_roman) - 1)
        if idx > 0 and (new_roman[idx-1] + new_roman[idx]) in swaps:
            pair = new_roman[idx-1] + new_roman[idx]; distractor = correct_romanization[:idx-1] + swaps[pair] + correct_romanization[idx+1:]
        elif new_roman[idx] in swaps:
            distractor = correct_romanization[:idx] + swaps[new_roman[idx]] + correct_romanization[idx+1:]
        else: continue
        if distractor != correct_romanization: distractors.add(distractor)
    while len(distractors) < 3: distractors.add(correct_romanization + random.choice([' annyeong', ' sarang']))
    return list(distractors)

def setup_romanization_game():
    st.session_state.romanization_questions = []; level = st.session_state.get('romanization_level', 1)
    items_fetched, attempts = 0, 0
    while items_fetched < 10 and attempts < 30:
        item = stats.get_short_practice_item(level=level, max_words=4); attempts += 1
        if item:
            hangul_text, correct_romanization = item['hangul'], item['roman']
            if not hangul_text or not correct_romanization: continue
            distractors = generate_distractors(correct_romanization); options = distractors + [correct_romanization]; random.shuffle(options)
            st.session_state.romanization_questions.append({
                "hangul": hangul_text, "correct": correct_romanization, "options": options,
                "translation_en": item.get('translation_en', 'Traducción no disponible.')
            })
            items_fetched += 1
    st.session_state.user_answers = []; st.session_state.current_question_index = 0


# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.title("🏃 Hangul Sprint")
    pages = ["Leer", "Romanización", "Lectura Profunda", "Estadísticas (próximamente)"]
    if st.session_state.page not in pages: st.session_state.page = "Leer"
    st.session_state.page = st.radio("Modos de Práctica", pages, index=pages.index(st.session_state.page))
    st.info("¡Bienvenido! Selecciona un modo para empezar.")


# --- MODO LECTURA ---
if st.session_state.page == "Leer":
    if not st.session_state.practice_in_progress:
        st.header("📖 Preparar Modo de Lectura")
        st.markdown("Selecciona tu nivel de dificultad y pulsa 'Empezar'. El cronómetro comenzará de inmediato.")
        st.write("**Elige tu nivel:**")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button(LEVEL_MAP[1], use_container_width=True, type="secondary" if st.session_state.reading_level != 1 else "primary", key="read_lvl_1"):
                st.session_state.reading_level = 1; st.rerun()
        with col2:
            if st.button(LEVEL_MAP[2], use_container_width=True, type="secondary" if st.session_state.reading_level != 2 else "primary", key="read_lvl_2"):
                st.session_state.reading_level = 2; st.rerun()
        with col3:
            if st.button(LEVEL_MAP[3], use_container_width=True, type="secondary" if st.session_state.reading_level != 3 else "primary", key="read_lvl_3"):
                st.session_state.reading_level = 3; st.rerun()
        with col4:
            if st.button(LEVEL_MAP[4], use_container_width=True, type="secondary" if st.session_state.reading_level != 4 else "primary", key="read_lvl_4"):
                st.session_state.reading_level = 4; st.rerun()
        st.info(f"Nivel seleccionado: **{LEVEL_MAP.get(st.session_state.reading_level, 'No definido')}**")
        st.divider()
        if st.button("🚀 Empezar a Leer", use_container_width=True, type="primary"):
            st.session_state.session_history = []
            with st.spinner("Cargando texto adecuado..."): load_new_reading_item()
            if st.session_state.practice_text_info:
                st.session_state.session_history.append(st.session_state.practice_text_info)
                st.session_state.practice_in_progress = True; st.rerun()
    else:
        if st.session_state.practice_text_info:
            korean_text = st.session_state.practice_text_info['hangul']
            if not st.session_state.timer_running and st.session_state.elapsed_time == 0:
                st.session_state.start_time, st.session_state.timer_running = time.time(), True; st.rerun()
            if st.session_state.timer_running:
                st.info(" Cronómetro en marcha... ¡Haz clic en una palabra si necesitas ayuda!")
                words = korean_text.split()
                if len(words) > 10: st.text_area("Frase de práctica:", korean_text, height=100)
                else:
                    cols = st.columns([len(word) + 2 for word in words])
                    for i, word in enumerate(words):
                        if cols[i].button(word, key=f"word_{i}_{korean_text}", use_container_width=True):
                            st.session_state.selected_word = word if st.session_state.selected_word != word else None; st.rerun()
            if st.session_state.timer_running and st.session_state.selected_word:
                clean_word = re.sub(r'[^\w\s]', '', st.session_state.selected_word); romanized_word = Romanizer(clean_word).romanize()
                st.markdown(f"<div style='color: #1c2833; text-align:center;font-size:22px;border:1px solid #007bff;padding:10px;border-radius:10px;background-color:#e7f3ff;margin-bottom:20px;'><b>{st.session_state.selected_word}</b> se romaniza como: <b>{romanized_word}</b></div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.session_state.timer_running:
                col1, col2 = st.columns(2)
                if col1.button("⏹️ Finalizar Lectura", use_container_width=True, type="primary"):
                    st.session_state.elapsed_time = time.time() - st.session_state.start_time; st.session_state.timer_running = False; st.rerun()
                if col2.button("Cargar Otro Texto", use_container_width=True):
                    with st.spinner("Buscando otro texto adecuado..."): load_new_reading_item()
                    if st.session_state.practice_text_info and st.session_state.practice_text_info not in st.session_state.session_history:
                        st.session_state.session_history.append(st.session_state.practice_text_info)
                    st.rerun()
            if st.session_state.elapsed_time > 0:
                st.success(f"¡Sesión finalizada! Tiempo total: **{st.session_state.elapsed_time:.2f} segundos**")
                st.markdown(f"#### Frases leídas en esta sesión ({len(st.session_state.session_history)}):")
                for item in st.session_state.session_history:
                    label_text = item['hangul']
                    if len(label_text) > 25: label_text = label_text[:25] + '...'
                    with st.expander(f"Ver Traducción de '{label_text}'"):
                        st.info(f"**{item.get('translation_en', 'Traducción no disponible.')}**")
                st.divider()
                if st.button("↩️ Practicar de Nuevo", use_container_width=True):
                    st.session_state.practice_in_progress = False; st.rerun()

# --- MODO ROMANIZACIÓN ---
elif st.session_state.page == "Romanización":
    if not st.session_state.romanization_practice_in_progress:
        st.header("✍️ Test de Romanización")
        st.markdown("Elige la romanización correcta para cada palabra o frase en coreano.")
        st.write("**Elige tu nivel:**")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button(LEVEL_MAP[1], use_container_width=True, type="secondary" if st.session_state.romanization_level != 1 else "primary", key="roman_lvl_1"):
                st.session_state.romanization_level = 1; st.rerun()
        with col2:
            if st.button(LEVEL_MAP[2], use_container_width=True, type="secondary" if st.session_state.romanization_level != 2 else "primary", key="roman_lvl_2"):
                st.session_state.romanization_level = 2; st.rerun()
        with col3:
            if st.button(LEVEL_MAP[3], use_container_width=True, type="secondary" if st.session_state.romanization_level != 3 else "primary", key="roman_lvl_3"):
                st.session_state.romanization_level = 3; st.rerun()
        with col4:
            if st.button(LEVEL_MAP[4], use_container_width=True, type="secondary" if st.session_state.romanization_level != 4 else "primary", key="roman_lvl_4"):
                st.session_state.romanization_level = 4; st.rerun()
        st.info(f"Nivel seleccionado: **{LEVEL_MAP.get(st.session_state.romanization_level, 'No definido')}**")
        st.divider()
        if st.button("🚀 Empezar Test", use_container_width=True, type="primary"):
            with st.spinner("Generando 10 preguntas..."): setup_romanization_game()
            if st.session_state.romanization_questions:
                st.session_state.romanization_practice_in_progress = True; st.rerun()
            else:
                st.error("No se pudieron cargar preguntas. Por favor, asegúrate de que la base de datos está poblada.")
    else:
        if st.session_state.current_question_index >= len(st.session_state.romanization_questions):
            st.header("🏁 Resultados del Test")
            correct_answers_details, wrong_answers_details = [], []
            for i, q in enumerate(st.session_state.romanization_questions):
                detail = {"hangul": q['hangul'], "chosen": st.session_state.user_answers[i], "correct": q['correct'], "translation_en": q.get('translation_en', 'Traducción no disponible.')}
                if detail["chosen"] == detail["correct"]: correct_answers_details.append(detail)
                else: wrong_answers_details.append(detail)

            st.success(f"**Aciertos: {len(correct_answers_details)} de {len(st.session_state.romanization_questions)}**")
            if wrong_answers_details:
                st.error(f"**Fallos: {len(wrong_answers_details)} de {len(st.session_state.romanization_questions)}**")
                st.divider(); st.subheader("Repaso de tus fallos:")
                for detail in wrong_answers_details:
                    st.markdown(f"Para **{detail['hangul']}**: <span style='color:red;'>Elegiste: `{detail['chosen']}`</span> | <span style='color:green;'>Correcta: `{detail['correct']}`</span>", unsafe_allow_html=True)
                    with st.expander("Ver traducción"):
                        st.info(f"**Traducción:** {detail['translation_en']}")
                    st.markdown("---")
            if correct_answers_details:
                st.divider(); st.subheader("Repaso de tus aciertos:")
                for detail in correct_answers_details:
                    st.markdown(f"**{detail['hangul']}** — Correcto: `{detail['correct']}`")
                    with st.expander("Ver traducción"):
                        st.info(f"**Traducción:** {detail['translation_en']}")
                    st.markdown("---")
            st.divider()
            if st.button("↩️ Volver a Jugar", use_container_width=True):
                st.session_state.romanization_practice_in_progress = False; st.rerun()
        else:
            total_q = len(st.session_state.romanization_questions); current_idx = st.session_state.current_question_index; current_q = st.session_state.romanization_questions[current_idx]
            st.progress((current_idx + 1) / total_q); st.subheader(f"Pregunta {current_idx + 1} de {total_q}")
            st.markdown(f"<div style='font-size:24px;text-align:center;padding:20px;background-color:#333;border-radius:10px;margin-bottom:25px;'>{current_q['hangul']}</div>", unsafe_allow_html=True)
            with st.form(key=f"form_q_{current_idx}"):
                chosen_option = st.radio("Elige la romanización correcta:", options=current_q['options'], index=None)
                submitted = st.form_submit_button("Siguiente", use_container_width=True, type="primary")
                if submitted:
                    if chosen_option is not None:
                        st.session_state.user_answers.append(chosen_option); st.session_state.current_question_index += 1; st.rerun()
                    else: st.warning("Por favor, selecciona una opción.")

# --- MODO LECTURA PROFUNDA ---
elif st.session_state.page == "Lectura Profunda":
    if not st.session_state.deep_read_in_progress:
        st.header("📖 Preparar Lectura Profunda")
        st.markdown("Elige un nivel de dificultad para cargar un texto largo. El cronómetro comenzará automáticamente.")
        st.write("**Elige tu nivel:**")
        cols = st.columns(7)
        levels = range(4, 11)
        for i, level in enumerate(levels):
            with cols[i]:
                if st.button(LEVEL_MAP.get(level, f"Nivel {level}"), use_container_width=True, key=f"deep_lvl_{level}"):
                    with st.spinner(f"Cargando texto de Nivel {level}..."):
                        st.session_state.deep_read_level = level
                        st.session_state.deep_read_text_data = get_long_text_data_from_db(level)
                        st.session_state.deep_read_elapsed_time = 0; st.session_state.deep_read_start_time = 0
                        st.session_state.deep_read_in_progress = True
                        st.rerun()
    else:
        st.header(f"📖 Leyendo Texto de Nivel {st.session_state.deep_read_level}")
        if st.session_state.deep_read_start_time == 0 and st.session_state.deep_read_elapsed_time == 0:
            st.session_state.deep_read_start_time = time.time()
            st.rerun()
        if st.session_state.deep_read_text_data:
            html_interactivo = generar_texto_con_tooltips(st.session_state.deep_read_text_data)
            st.markdown(html_interactivo, unsafe_allow_html=True)
        else:
            st.error("No se pudo cargar el texto. Por favor, vuelve a la selección de nivel.")
        st.divider()
        if st.session_state.deep_read_elapsed_time > 0:
            st.success(f"¡Lectura finalizada! Tiempo total: **{st.session_state.deep_read_elapsed_time:.2f} segundos**")
            if st.button("↩️ Elegir Otro Nivel", use_container_width=True):
                st.session_state.deep_read_in_progress = False
                st.rerun()
        else:
            st.info("Cronómetro en marcha... Cuando termines de leer, pulsa 'Finalizar Lectura'.")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⏹️ Finalizar Lectura", use_container_width=True, type="primary"):
                    if st.session_state.deep_read_start_time > 0:
                        st.session_state.deep_read_elapsed_time = time.time() - st.session_state.deep_read_start_time
                        st.session_state.deep_read_start_time = 0
                        st.rerun()
            with col2:
                if st.button("🔄 Cargar Otro Texto", use_container_width=True):
                    with st.spinner(f"Buscando otro texto de Nivel {st.session_state.deep_read_level}..."):
                        st.session_state.deep_read_text_data = get_long_text_data_from_db(st.session_state.deep_read_level)
                        st.session_state.deep_read_start_time = 0; st.session_state.deep_read_elapsed_time = 0
                        st.rerun()