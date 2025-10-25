# src/streamlit_app.py (Versión final con niveles renombrados y limitados)

import streamlit as st
import time
import pandas as pd
import re
import random
from core_logic import stats
from korean_romanizer.romanizer import Romanizer

# --- ¡CAMBIO CLAVE 1! Creamos el mapa de niveles ---
LEVEL_MAP = {
    1: "Principiante",
    2: "Intermedio",
    3: "Maestro",
    4: "Leyenda",
    # Dejamos los otros por si se usan en el futuro
    5: "Nivel 5",
    6: "Nivel 6",
    7: "Nivel 7",
    8: "Nivel 8",
    9: "Nivel 9",
    10: "Nivel 10",
}

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Hangul Sprint",
    layout="wide"
)

# --- INICIALIZACIÓN GENERAL DEL ESTADO DE LA SESIÓN ---
if 'page' not in st.session_state:
    st.session_state.page = "Leer"

# --- ESTADOS PARA EL JUEGO DE LECTURA ---
if 'reading_level' not in st.session_state:
    st.session_state.reading_level = 1
if 'practice_in_progress' not in st.session_state:
    st.session_state.practice_in_progress = False
if 'practice_text_info' not in st.session_state:
    st.session_state.practice_text_info = None
if 'timer_running' not in st.session_state:
    st.session_state.timer_running = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = 0
if 'elapsed_time' not in st.session_state:
    st.session_state.elapsed_time = 0
if 'selected_word' not in st.session_state:
    st.session_state.selected_word = None
if 'session_history' not in st.session_state:
    st.session_state.session_history = []

# --- ESTADOS PARA EL JUEGO DE ROMANIZACIÓN ---
if 'romanization_level' not in st.session_state:
    st.session_state.romanization_level = 1
if 'romanization_practice_in_progress' not in st.session_state:
    st.session_state.romanization_practice_in_progress = False
if 'romanization_questions' not in st.session_state:
    st.session_state.romanization_questions = []
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = []

# ==============================================================================
# --- FUNCIONES AUXILIARES ---
# ==============================================================================

def load_new_reading_item(attempt_count=0):
    MAX_WORDS_FOR_READING, MAX_ATTEMPTS = 10, 10
    if attempt_count >= MAX_ATTEMPTS:
        st.error("No se pudo encontrar una frase adecuada. Por favor, intenta con otro nivel."); st.session_state.practice_text_info = None; return
    item = stats.get_practice_item(level=st.session_state.reading_level)
    if item:
        if len(item['hangul'].split()) > MAX_WORDS_FOR_READING:
            st.info(f"Frase demasiado larga encontrada... Moviéndola al nivel 5 y buscando otra."); stats.update_phrase_level(item['id'], 5); load_new_reading_item(attempt_count + 1)
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
            st.session_state.romanization_questions.append({"hangul": hangul_text, "correct": correct_romanization, "options": options})
            items_fetched += 1
    st.session_state.user_answers = []; st.session_state.current_question_index = 0

# ==============================================================================
# --- BARRA LATERAL DE NAVEGACIÓN ---
# ==============================================================================
with st.sidebar:
    st.title("🏃 Hangul Sprint")
    st.session_state.page = st.radio("Modos de Práctica", ["Leer", "Romanización", "Estadísticas (próximamente)"], index=["Leer", "Romanización", "Estadísticas (próximamente)"].index(st.session_state.page))
    st.info("¡Bienvenido! Selecciona un modo para empezar.")

# ==============================================================================
# --- SECCIÓN DEL MINIJUEGO DE LECTURA ---
# ==============================================================================
if st.session_state.page == "Leer":
    if not st.session_state.practice_in_progress:
        st.header("📖 Preparar Modo de Lectura")
        st.markdown("Selecciona tu nivel de dificultad y pulsa 'Empezar'. El cronómetro comenzará de inmediato.")
        
        # --- ¡CAMBIO CLAVE 2! El slider del Modo Lectura ahora muestra los nombres ---
        st.session_state.reading_level = st.slider(
            "Elige tu nivel", 
            min_value=1, 
            max_value=4, 
            value=st.session_state.reading_level,
            format_func=lambda x: LEVEL_MAP.get(x, f"Nivel {x}") # Muestra el nombre, guarda el número
        )
        
        st.divider()
        if st.button("🚀 Empezar a Leer", use_container_width=True, type="primary"):
            st.session_state.session_history = []
            with st.spinner("Cargando texto adecuado..."): load_new_reading_item()
            if st.session_state.practice_text_info:
                st.session_state.session_history.append(st.session_state.practice_text_info)
                st.session_state.practice_in_progress = True
                st.rerun()
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

# ==============================================================================
# --- SECCIÓN DEL MINIJUEGO DE ROMANIZACIÓN ---
# ==============================================================================
elif st.session_state.page == "Romanización":
    if not st.session_state.romanization_practice_in_progress:
        st.header("✍️ Test de Romanización")
        st.markdown("Elige la romanización correcta para cada palabra o frase en coreano. ¡Presta atención a los detalles!")
        
        # --- ¡CAMBIO CLAVE 3! El slider del Test de Romanización también se limita y muestra nombres ---
        st.session_state.romanization_level = st.slider(
            "Elige tu nivel", 
            min_value=1, 
            max_value=4, 
            value=st.session_state.romanization_level,
            format_func=lambda x: LEVEL_MAP.get(x, f"Nivel {x}") # Muestra el nombre, guarda el número
        )

        st.divider()
        if st.button("🚀 Empezar Test", use_container_width=True, type="primary"):
            with st.spinner("Generando 10 preguntas..."): setup_romanization_game()
            if st.session_state.romanization_questions:
                st.session_state.romanization_practice_in_progress = True; st.rerun()
            else:
                st.error("No se pudieron cargar preguntas. Por favor, asegúrate de que la base de datos está poblada.")
    else:
        # El resto del código de la romanización no necesita cambios y se mantiene igual.
        if st.session_state.current_question_index >= len(st.session_state.romanization_questions):
            st.header("🏁 Resultados del Test"); correct_answers = 0; wrong_answers_details = []
            for i, q in enumerate(st.session_state.romanization_questions):
                if st.session_state.user_answers[i] == q['correct']: correct_answers += 1
                else: wrong_answers_details.append({"hangul": q['hangul'], "chosen": st.session_state.user_answers[i], "correct": q['correct']})
            st.success(f"**Aciertos: {correct_answers} de {len(st.session_state.romanization_questions)}**")
            if wrong_answers_details:
                st.error(f"**Fallos: {len(wrong_answers_details)} de {len(st.session_state.romanization_questions)}**"); st.divider(); st.subheader("Repaso de tus fallos:")
                for detail in wrong_answers_details:
                    st.markdown(f"Para **{detail['hangul']}**:"); st.markdown(f" - <span style='color:red;'>Elegiste: `{detail['chosen']}`</span>", unsafe_allow_html=True); st.markdown(f" - <span style='color:green;'>Correcta: `{detail['correct']}`</span>", unsafe_allow_html=True); st.markdown("---")
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