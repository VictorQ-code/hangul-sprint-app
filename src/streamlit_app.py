# src/streamlit_app.py

import streamlit as st
# Hacemos las importaciones absolutas para que funcione en cualquier entorno
from core_logic import reading

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Hangul Sprint",
    layout="centered" # Centra el contenido
)

# --- Título de la Aplicación ---
st.title("🏃 Hangul Sprint")
st.subheader("Modo de Práctica de Lectura")

# --- Lógica de la Sesión ---
# 'st.session_state' es un diccionario mágico de Streamlit
# que recuerda los valores entre interacciones del usuario.
if 'current_item' not in st.session_state:
    st.session_state.current_item = None
    st.session_state.options = []
    st.session_state.feedback = ""
    st.session_state.show_answer = False

def load_new_item():
    """Carga una nueva frase y reinicia el estado."""
    item_data = reading.start_reading_session(level=1)
    if not item_data.get("error"):
        st.session_state.current_item = item_data['practice_item']
        st.session_state.options = item_data['silent_mode_options']
        st.session_state.feedback = ""
        st.session_state.show_answer = False

def check_answer(chosen_option):
    """Comprueba la respuesta del usuario y da feedback."""
    correct_answer = st.session_state.current_item['roman']
    if chosen_option == correct_answer:
        st.session_state.feedback = "¡Correcto! 🎉"
    else:
        st.session_state.feedback = f"Incorrecto. La respuesta era: **{correct_answer}**"
    st.session_state.show_answer = True

# --- Interfaz de Usuario (UI) ---

# Cargar el primer item si no hay ninguno
if st.session_state.current_item is None:
    load_new_item()

# Botón para cargar la siguiente frase
if st.button("Siguiente Frase 🔁"):
    load_new_item()

# Mostrar la frase actual si existe
if st.session_state.current_item:
    # Mostramos la frase en un recuadro grande
    st.header(st.session_state.current_item['hangul'])

    # Crear columnas para los botones de opciones
    # Esto hace que se vea mejor en pantallas de móvil
    col1, col2 = st.columns(2)
    with col1:
        for i in range(0, len(st.session_state.options), 2):
            option = st.session_state.options[i]
            # 'disabled' evita que se pueda volver a contestar
            if st.button(option, key=f"opt_{i}", use_container_width=True, disabled=st.session_state.show_answer):
                check_answer(option)
    with col2:
        for i in range(1, len(st.session_state.options), 2):
            option = st.session_state.options[i]
            if st.button(option, key=f"opt_{i}", use_container_width=True, disabled=st.session_state.show_answer):
                check_answer(option)
    
    # Mostrar el feedback después de que el usuario conteste
    if st.session_state.feedback:
        if "Correcto" in st.session_state.feedback:
            st.success(st.session_state.feedback)
        else:
            st.error(st.session_state.feedback)

else:
    st.warning("No se pudieron cargar frases. Revisa la base de datos.")