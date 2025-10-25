import streamlit as st
import time
import pandas as pd
import re
import random
from core_logic import stats
# Romanizer todavía es útil si quieres romanizar una sola palabra al hacer clic
from korean_romanizer.romanizer import Romanizer

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

def load_new_reading_item():
    """Carga un nuevo item de lectura."""
    item = stats.get_practice_item(level=st.session_state.reading_level)
    if item:
        st.session_state.practice_text_info = item
        st.session_state.timer_running = False
        st.session_state.start_time = 0
        st.session_state.elapsed_time = 0
        st.session_state.selected_word = None
    else:
        st.session_state.practice_text_info = None
        st.error(f"No se encontraron textos para el nivel {st.session_state.reading_level}. Asegúrate de que la base de datos esté poblada.")

def generate_distractors(correct_romanization):
    """Genera 3 romanizaciones incorrectas pero similares a la correcta."""
    distractors = set()
    # Si la romanización es muy larga (una frase), generamos distractores más simples
    if len(correct_romanization.split()) > 3:
        words = correct_romanization.split()
        sample_word = random.choice(words)
        distractors.add(sample_word + " is wrong")
        distractors.add(correct_romanization.replace('a','e'))
    
    swaps = {
        'eo': 'o', 'o': 'eo', 'eu': 'u', 'u': 'eu', 'ae': 'e', 'e': 'ae',
        'g': 'k', 'k': 'g', 'd': 't', 't': 'd', 'b': 'p', 'p': 'b', 'j': 'ch', 'ch': 'j', 'r': 'l', 'l': 'r'
    }
    attempts = 0
    while len(distractors) < 3 and attempts < 50:
        new_roman = list(correct_romanization)
        if not new_roman: break
        idx = random.randint(0, len(new_roman) - 1)
        if idx > 0 and (new_roman[idx-1] + new_roman[idx]) in swaps:
            pair = new_roman[idx-1] + new_roman[idx]
            distractor = correct_romanization[:idx-1] + swaps[pair] + correct_romanization[idx+1:]
        elif new_roman[idx] in swaps:
            distractor = correct_romanization[:idx] + swaps[new_roman[idx]] + correct_romanization[idx+1:]
        else:
            attempts += 1
            continue
        if distractor != correct_romanization: distractors.add(distractor)
        attempts += 1
    while len(distractors) < 3: distractors.add(correct_romanization + random.choice([' annyeong', ' sarang', ' kamsahamnida']))
    return list(distractors)

# --- VERSIÓN CORREGIDA DE LA FUNCIÓN ---
def setup_romanization_game():
    """Prepara 10 preguntas para el juego de romanización usando los datos del CSV."""
    st.session_state.romanization_questions = []
    level = st.session_state.get('romanization_level', 1)
    
    items_fetched = 0
    attempts = 0
    # Bucle para asegurarse de que obtenemos 10 preguntas válidas
    while items_fetched < 10 and attempts < 50:
        item = stats.get_practice_item(level=level)
        attempts += 1 # Incrementar intentos para evitar bucles infinitos
        
        if item:
            # ¡CAMBIO CLAVE! Leemos la romanización y el hangul directamente del item.
            hangul_text = item['hangul']
            correct_romanization = item['roman']
            
            # Nos aseguramos de que no sean nulos o vacíos
            if not hangul_text or not correct_romanization:
                continue

            distractors = generate_distractors(correct_romanization)
            options = distractors + [correct_romanization]
            random.shuffle(options)
            
            st.session_state.romanization_questions.append({
                "hangul": hangul_text,
                "correct": correct_romanization,
                "options": options
            })
            items_fetched += 1
            
    st.session_state.user_answers = []
    st.session_state.current_question_index = 0
# ---------------------------------------------

# ==============================================================================
# --- BARRA LATERAL DE NAVEGACIÓN ---
# ==============================================================================
with st.sidebar:
    st.title("🏃 Hangul Sprint")
    st.session_state.page = st.radio(
        "Modos de Práctica",
        ["Leer", "Romanización", "Estadísticas (próximamente)"],
        index=["Leer", "Romanización", "Estadísticas (próximamente)"].index(st.session_state.page)
    )
    st.info("¡Bienvenido! Selecciona un modo para empezar.")

# ==============================================================================
# --- SECCIÓN DEL MINIJUEGO DE LECTURA ---
# ==============================================================================
if st.session_state.page == "Leer":
    if not st.session_state.practice_in_progress:
        st.header("📖 Preparar Modo de Lectura")
        st.markdown("Selecciona tu nivel de dificultad y pulsa 'Empezar'. El cronómetro comenzará de inmediato.")
        st.session_state.reading_level = st.slider("Nivel de Dificultad", 1, 10, st.session_state.reading_level)
        st.divider()

        if st.button("🚀 Empezar a Leer", use_container_width=True, type="primary"):
            st.session_state.session_history = []
            with st.spinner("Cargando texto..."):
                load_new_reading_item()
            if st.session_state.practice_text_info:
                st.session_state.session_history.append(st.session_state.practice_text_info)
                st.session_state.practice_in_progress = True
                st.rerun()
    else:
        if st.session_state.practice_text_info:
            korean_text = st.session_state.practice_text_info['hangul']

            if not st.session_state.timer_running and st.session_state.elapsed_time == 0:
                st.session_state.start_time = time.time()
                st.session_state.timer_running = True
                st.rerun()

            if st.session_state.timer_running:
                st.info(" Cronómetro en marcha... ¡Haz clic en una palabra si necesitas ayuda!")
                words = korean_text.split()
                # Control para evitar demasiadas columnas si la frase es muy larga
                if len(words) > 10:
                    st.text_area("Frase de práctica:", korean_text, height=100)
                    st.warning("La frase es muy larga para mostrarla como botones. Haz clic abajo para finalizar.")
                else:
                    cols = st.columns([len(word) + 2 for word in words])
                    for i, word in enumerate(words):
                        if cols[i].button(word, key=f"word_{i}_{korean_text}", use_container_width=True):
                            st.session_state.selected_word = word if st.session_state.selected_word != word else None
                            st.rerun()

            if st.session_state.timer_running and st.session_state.selected_word:
                clean_word = re.sub(r'[^\w\s]', '', st.session_state.selected_word)
                # Para esta función específica de ayuda, sigue siendo útil calcular la romanización de una sola palabra
                romanized_word = Romanizer(clean_word).romanize()
                st.markdown(
                    f"<div style='color: #1c2833; text-align:center;font-size:22px;border:1px solid #007bff;padding:10px;border-radius:10px;background-color:#e7f3ff;margin-bottom:20px;'>"
                    f"<b>{st.session_state.selected_word}</b> se romaniza como: <b>{romanized_word}</b>"
                    "</div>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)

            if st.session_state.timer_running:
                col1, col2 = st.columns(2)
                if col1.button("⏹️ Finalizar Lectura", use_container_width=True, type="primary"):
                    st.session_state.elapsed_time = time.time() - st.session_state.start_time
                    st.session_state.timer_running = False
                    st.rerun()
                if col2.button("Cargar Otro Texto", use_container_width=True):
                    load_new_reading_item()
                    if st.session_state.practice_text_info:
                        st.session_state.session_history.append(st.session_state.practice_text_info)
                    st.rerun()
            
            if st.session_state.elapsed_time > 0:
                st.success(f"¡Sesión finalizada! Tiempo total: **{st.session_state.elapsed_time:.2f} segundos**")
                st.markdown(f"#### Frases leídas en esta sesión ({len(st.session_state.session_history)}):")
                for item in st.session_state.session_history:
                    st.markdown(f"<div style='font-size:20px;padding:10px;background-color:#333;border-radius:5px;margin-top:10px;'>{item['hangul']}</div>", unsafe_allow_html=True)
                    with st.expander(f"Ver Traducción de '{item['hangul'][:25]}...'"):
                        st.info(f"**{item.get('translation_en', 'Traducción no disponible.')}**")
                
                st.divider()
                if st.button("↩️ Practicar de Nuevo", use_container_width=True):
                    st.session_state.practice_in_progress = False
                    st.rerun()

# ==============================================================================
# --- SECCIÓN DEL MINIJUEGO DE ROMANIZACIÓN ---
# ==============================================================================
elif st.session_state.page == "Romanización":
    if not st.session_state.romanization_practice_in_progress:
        st.header("✍️ Test de Romanización")
        st.markdown("Elige la romanización correcta para cada palabra o frase en coreano. ¡Presta atención a los detalles!")
        st.session_state.romanization_level = st.slider("Nivel de Dificultad", 1, 10, st.session_state.romanization_level)
        st.divider()

        if st.button("🚀 Empezar Test", use_container_width=True, type="primary"):
            with st.spinner("Generando 10 preguntas..."):
                setup_romanization_game()
            if st.session_state.romanization_questions:
                st.session_state.romanization_practice_in_progress = True
                st.rerun()
            else:
                st.error("No se pudieron cargar preguntas. Por favor, asegúrate de que la base de datos está poblada e inténtalo de nuevo.")

    else:
        if st.session_state.current_question_index >= len(st.session_state.romanization_questions):
            st.header("🏁 Resultados del Test")
            correct_answers = 0
            wrong_answers_details = []

            for i, question in enumerate(st.session_state.romanization_questions):
                user_answer = st.session_state.user_answers[i]
                if user_answer == question['correct']:
                    correct_answers += 1
                else:
                    wrong_answers_details.append({
                        "hangul": question['hangul'],
                        "chosen": user_answer,
                        "correct": question['correct']
                    })
            
            st.success(f"**Aciertos: {correct_answers} de {len(st.session_state.romanization_questions)}**")
            
            if wrong_answers_details:
                st.error(f"**Fallos: {len(wrong_answers_details)} de {len(st.session_state.romanization_questions)}**")
                st.divider()
                st.subheader("Repaso de tus fallos:")
                for detail in wrong_answers_details:
                    st.markdown(f"Para **{detail['hangul']}**:")
                    st.markdown(f" - <span style='color:red;'>Elegiste: `{detail['chosen']}`</span>", unsafe_allow_html=True)
                    st.markdown(f" - <span style='color:green;'>Correcta: `{detail['correct']}`</span>", unsafe_allow_html=True)
                    st.markdown("---")

            st.divider()
            if st.button("↩️ Volver a Jugar", use_container_width=True):
                st.session_state.romanization_practice_in_progress = False
                st.rerun()
        
        else:
            total_questions = len(st.session_state.romanization_questions)
            current_index = st.session_state.current_question_index
            current_q = st.session_state.romanization_questions[current_index]

            st.progress((current_index + 1) / total_questions)
            st.subheader(f"Pregunta {current_index + 1} de {total_questions}")
            
            st.markdown(f"<div style='font-size:24px;text-align:center;padding:20px;background-color:#333;border-radius:10px;margin-bottom:25px;'>{current_q['hangul']}</div>", unsafe_allow_html=True)
            
            with st.form(key=f"form_q_{current_index}"):
                chosen_option = st.radio("Elige la romanización correcta:", options=current_q['options'], index=None)
                submitted = st.form_submit_button("Siguiente", use_container_width=True, type="primary")

                if submitted:
                    if chosen_option is not None:
                        st.session_state.user_answers.append(chosen_option)
                        st.session_state.current_question_index += 1
                        st.rerun()
                    else:
                        st.warning("Por favor, selecciona una opción.")