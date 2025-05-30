import streamlit as st
import random
import os
import base64

# Directorio donde se encuentran los archivos .wav
WAV_DIRECTORY = "wav"

# Mapeo de nombres de notas a los nombres de archivos .wav
note_mapping = {
    "Do": "c1.wav",
    "Do#/Reb": "c1s.wav",
    "Re": "d1.wav",
    "Re#/Mib": "d1s.wav",
    "Mi": "e1.wav",
    "Fa": "f1.wav",
    "Fa#/Solb": "f1s.wav",
    "Sol": "g1.wav",
    "Sol#/Lab": "g1s.wav",
    "La": "a1.wav",
    "La#/Sib": "a1s.wav",
    "Si": "b1.wav",
}

# Lista de notas disponibles para adivinar
available_notes = list(note_mapping.keys())

# Función para reproducir una nota aleatoria
def play_random_note():
    note_name = random.choice(available_notes)  # Seleccionar una nota al azar
    note_file = os.path.join(WAV_DIRECTORY, note_mapping[note_name])
    return note_name, note_file

# Función para verificar la respuesta del usuario
def check_answer(user_input, correct_note):
    return user_input.lower() == correct_note.lower()

# Función para reproducar audio automáticamente
def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true">
            <source src="data:audio/wav;base64,{b64}" type="audio/wav">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

# Configuración de la aplicación Streamlit
st.title("Adivina la nota")
st.write("Escucha la nota y selecciona cuál crees que es. Juega 10 rondas y acumula puntos (10 puntos por respuesta correcta).")

# Inicializar variables de estado
if "note_played" not in st.session_state:
    st.session_state.note_played = None
if "round" not in st.session_state:
    st.session_state.round = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "game_over" not in st.session_state:
    st.session_state.game_over = False

# Botón para iniciar o continuar el juego
if not st.session_state.game_over:
    if st.button("Reproducir nota" if st.session_state.round == 0 else "Siguiente nota"):
        if st.session_state.round < 10:
            st.session_state.round += 1
            st.session_state.note_played, note_file = play_random_note()
            autoplay_audio(note_file)
        else:
            st.session_state.game_over = True

# Mostrar ronda actual y puntaje
if st.session_state.round > 0 and not st.session_state.game_over:
    st.write(f"Ronda {st.session_state.round}/10 | Puntaje: {st.session_state.score}")

# Selección de la respuesta del usuario y verificación
if st.session_state.note_played and not st.session_state.game_over:
    user_input = st.selectbox("¿Qué nota crees que se ha reproducido?", available_notes, key=f"select_{st.session_state.round}")

    if st.button("Adivinar"):
        if user_input:
            if check_answer(user_input, st.session_state.note_played):
                st.session_state.score += 10
                st.write("¡Correcto! Has adivinado la nota correctamente. +10 puntos.")
            else:
                st.write(f"Incorrecto. La nota correcta era '{st.session_state.note_played}'.")
            if st.session_state.round < 10:
                st.write("Haz clic en 'Siguiente nota' para continuar.")
            else:
                st.session_state.game_over = True

# Mostrar resultado final
if st.session_state.game_over:
    st.write(f"¡Juego terminado! Tu puntaje final es: {st.session_state.score}/100")
    if st.button("Jugar de nuevo"):
        st.session_state.round = 0
        st.session_state.score = 0
        st.session_state.note_played = None
        st.session_state.game_over = False
        st.rerun()
