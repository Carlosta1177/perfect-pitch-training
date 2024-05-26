import streamlit as st
import pygame.mixer
import random
import os

# Inicializar pygame.mixer
pygame.mixer.init()

# Directorio donde se encuentran los archivos .wav
WAV_DIRECTORY = "wav"

# Mapeo de nombres de notas a los nombres de archivos .wav
note_mapping = {
    "Do": "c1.wav",
    "Do#": "c1s.wav",
    "Re": "d1.wav",
    "Re#": "d1s.wav",
    "Mi": "e1.wav",
    "Fa": "f1.wav",
    "Fa#": "f1s.wav",
    "Sol": "g1.wav",
    "Sol#": "g1s.wav",
    "La": "a1.wav",
    "La#": "a1s.wav",
    "Si": "b1.wav",
}

# Lista de notas disponibles para adivinar
available_notes = list(note_mapping.keys())

# Variable de estado para la nota actual
if "note_played" not in st.session_state:
    st.session_state.note_played = None

# Función para reproducir una nota aleatoria
def play_random_note():
    note_name = random.choice(available_notes)  # Seleccionar una nota al azar
    note_file = os.path.join(WAV_DIRECTORY, note_mapping[note_name])
    pygame.mixer.Sound(note_file).play()  # Reproducir el archivo de sonido
    return note_name

# Función para reproducir la misma nota que la anterior
def play_same_note():
    if st.session_state.note_played:
        note_file = os.path.join(WAV_DIRECTORY, note_mapping[st.session_state.note_played])
        pygame.mixer.Sound(note_file).play()  # Reproducir el archivo de sonido

# Función para verificar la respuesta del usuario
def check_answer(user_input, correct_note):
    return user_input.lower() == correct_note.lower()

# Configuración de la aplicación Streamlit
st.title("Adivina la nota")
st.write("Escucha la nota y selecciona cuál crees que es.")

# Botón para reproducir la nota
if st.button("Reproducir nota"):
    st.session_state.note_played = play_random_note()

# Botón para volver a escuchar la misma nota
if st.session_state.note_played:
    if st.button("Volver a escuchar"):
        play_same_note()

# Selección de la respuesta del usuario
if st.session_state.note_played:
    user_input = st.selectbox("¿Qué nota crees que se ha reproducido?", available_notes)

    # Verificar respuesta y mostrar resultado
    if st.button("Adivinar"):
        if user_input:
            if check_answer(user_input, st.session_state.note_played):
                st.write("¡Correcto! Has adivinado la nota correctamente.")
            else:
                st.write(f"Incorrecto. La nota correcta era '{st.session_state.note_played}'.")
        else:
            st.write("Por favor, selecciona una respuesta antes de adivinar.")
