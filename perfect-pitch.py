import streamlit as st
import random
import time
import numpy as np
import matplotlib.pyplot as plt
import os
import json
from pathlib import Path

# -------------------------------
# CONFIGURACIÓN INICIAL
# -------------------------------
st.set_page_config(
    page_title="🎵 Entrenador Auditivo Pro",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.example.com/help',
        'Report a bug': 'https://www.example.com/bug',
        'About': "### Entrenador Auditivo Pro - ¡Mejora tu oído musical!"
    }
)
st.title("🎧 Entrenador Auditivo Pro con IA Adaptativa")

# -------------------------------
# VARIABLES DE SESIÓN
# -------------------------------
if "score" not in st.session_state:
    st.session_state.score = 0
if "attempts" not in st.session_state:
    st.session_state.attempts = 0
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "player_name" not in st.session_state:
    st.session_state.player_name = ""
if "leaderboard" not in st.session_state:
    st.session_state.leaderboard = []
if "history" not in st.session_state:
    st.session_state.history = []
if "subscription" not in st.session_state:
    st.session_state.subscription = True
if "nota_actual" not in st.session_state:
    st.session_state.nota_actual = None
if "feedback_message" not in st.session_state:
    st.session_state.feedback_message = None
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "language" not in st.session_state:
    st.session_state.language = "Español"

# -------------------------------
# PERSISTENCIA DE LEADERBOARD
# -------------------------------
LEADERBOARD_FILE = "leaderboard.json"

@st.cache_data
def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r") as f:
            return json.load(f)
    return []

@st.cache_data
def save_leaderboard(leaderboard):
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(leaderboard, f)

# Load leaderboard at start
st.session_state.leaderboard = load_leaderboard()

# -------------------------------
# FUNCIONES
# -------------------------------
NOTAS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B", "C2"]

# Map note names to .wav filenames
NOTE_TO_FILE = {
    "C": "c1.wav",
    "C#": "c1s.wav",
    "D": "d1.wav",
    "D#": "d1s.wav",
    "E": "e1.wav",
    "F": "f1.wav",
    "F#": "f1s.wav",
    "G": "g1.wav",
    "G#": "g1s.wav",
    "A": "a1.wav",
    "A#": "a1s.wav",
    "B": "b1.wav",
    "C2": "c2.wav"
}

# Traducciones
TEXTS = {
    "Español": {
        "header": "Configuración",
        "rounds_label": "Número de rondas:",
        "instructions": """
        - Selecciona la dificultad y el número de rondas.
        - Escucha la nota haciendo clic en el botón de reproducción del audio.
        - Elige la nota que crees que es del menú desplegable.
        - Envía tu respuesta y ve tu progreso.
        - Al final, ingresa tu nombre para la tabla de líderes.
        """,
        "guide": """
        **Guía para las notas**: Selecciona la nota que escuches desde el menú desplegable. Las notas sostenidas (sharps) se indican con `#` (ej. `C#` para Do sostenido). Puedes usar bemoles (flats) como equivalentes (ej. `Db` para `C#`). Ejemplos:
        - `C`: Do
        - `C#` o `Db`: Do sostenido / Re bemol
        - `D`: Re
        - `D#` o `Eb`: Re sostenido / Mi bemol
        - `C2`: Do en octava superior
        """,
        "game_title": "🎼 Escucha la nota y adivina cuál es",
        "select_note": "¿Qué nota escuchaste?",
        "submit": "Enviar respuesta",
        "game_over": "Juego Terminado - Puntaje Final: {score}/{total}",
        "enter_name": "Ingresa tu nombre para la tabla de ganadores:",
        "save_score": "Guardar Puntaje",
        "leaderboard": "🏆 Tabla de Ganadores",
        "no_scores": "Aún no hay puntajes registrados.",
        "progress": "📈 Progreso del Usuario",
        "play_again": "🔁 Jugar de nuevo",
        "select_note_warning": "Por favor, selecciona una nota antes de enviar.",
        "correct": "✅ ¡Correcto!",
        "incorrect": "❌ Incorrecto. Era {nota}",
        "score_saved": "✅ Puntaje guardado"
    },
    "English": {
        "header": "Settings",
        "rounds_label": "Number of rounds:",
        "instructions": """
        - Choose the difficulty and number of rounds.
        - Listen to the note by clicking the audio play button.
        - Select the note you think it is from the dropdown.
        - Submit your answer and track your progress.
        - At the end, enter your name for the leaderboard.
        """,
        "guide": """
        **Note Guide**: Select the note you hear from the dropdown. Sharp notes are indicated with `#` (e.g., `C#` for C sharp). Flats are equivalent (e.g., `Db` for `C#`). Examples:
        - `C`: C
        - `C#` or `Db`: C sharp / D flat
        - `D`: D
        - `D#` or `Eb`: D sharp / E flat
        - `C2`: C in higher octave
        """,
        "game_title": "🎼 Listen to the note and guess which it is",
        "select_note": "Which note did you hear?",
        "submit": "Submit Answer",
        "game_over": "Game Over - Final Score: {score}/{total}",
        "enter_name": "Enter your name for the leaderboard:",
        "save_score": "Save Score",
        "leaderboard": "🏆 Leaderboard",
        "no_scores": "No scores registered yet.",
        "progress": "📈 User Progress",
        "play_again": "🔁 Play Again",
        "select_note_warning": "Please select a note before submitting.",
        "correct": "✅ Correct!",
        "incorrect": "❌ Incorrect. It was {nota}",
        "score_saved": "✅ Score saved"
    }
}

def generar_nota(dificultad):
    if dificultad == "Fácil" or dificultad == "Easy":
        return random.choice(NOTAS[:7])  # C to G
    elif dificultad == "Media" or dificultad == "Medium":
        return random.choice(NOTAS[:10])  # C to A
    else:
        return random.choice(NOTAS)  # All notes, including C2

@st.cache_data
def reproducir_nota(nota):
    try:
        file_name = NOTE_TO_FILE.get(nota)
        if not file_name:
            st.error(f"❌ Error: No file found for note {nota}")
            return
        file_path = os.path.join("wav", file_name)
        if os.path.exists(file_path):
            st.audio(file_path, format="audio/wav", autoplay=True)
        else:
            st.error(f"❌ Error: File {file_path} does not exist")
    except Exception as e:
        st.error(f"❌ Error playing note {nota}: {str(e)}")

def evaluar_respuesta(respuesta, nota_correcta):
    flat_to_sharp = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}
    respuesta_normalized = flat_to_sharp.get(respuesta, respuesta)
    return respuesta_normalized == nota_correcta

def resetear_juego():
    st.session_state.score = 0
    st.session_state.attempts = 0
    st.session_state.game_over = False
    st.session_state.history = []
    st.session_state.player_name = ""
    st.session_state.nota_actual = None
    st.session_state.feedback_message = None
    st.session_state.streak = 0

def guardar_en_leaderboard(nombre, puntaje):
    st.session_state.leaderboard.append((nombre, puntaje))
    st.session_state.leaderboard = sorted(st.session_state.leaderboard, key=lambda x: x[1], reverse=True)[:10]
    save_leaderboard(st.session_state.leaderboard)

def mostrar_progreso():
    lang = st.session_state.language
    st.subheader(TEXTS[lang]["progress"])
    intentos = list(range(1, len(st.session_state.history) + 1))
    aciertos = [1 if correcto else 0 for _, _, correcto in st.session_state.history]
    fig, ax = plt.subplots()
    ax.plot(intentos, np.cumsum(aciertos), marker='o', color='#1f77b4')
    ax.set_xlabel("Intentos" if lang == "Español" else "Attempts")
    ax.set_ylabel("Aciertos acumulados" if lang == "Español" else "Cumulative Correct")
    ax.set_title("Evolución del rendimiento" if lang == "Español" else "Performance Progress")
    fig.canvas.set_window_title("Progress Chart")  # For screen readers
    st.pyplot(fig)
    # Accessibility: Table of results
    st.table({"Intento" if lang == "Español" else "Attempt": intentos, "Acierto" if lang == "Español" else "Correct": aciertos})
    # Missed notes summary
    missed_notes = [nota for nota, _, correcto in st.session_state.history if not correcto]
    if missed_notes:
        st.subheader("Notas más falladas" if lang == "Español" else "Most Missed Notes")
        note_counts = {nota: missed_notes.count(nota) for nota in set(missed_notes)}
        st.write(note_counts)

# -------------------------------
# INTERFAZ DE USUARIO
# -------------------------------
if not st.session_state.subscription:
    st.warning("🔒 Esta funcionalidad está disponible solo para usuarios con suscripción activa." if st.session_state.language == "Español" else "🔒 This feature is only available for users with an active subscription.")
    st.stop()

# Sidebar
with st.sidebar:
    st.header(TEXTS[st.session_state.language]["header"])
    max_attempts = st.selectbox(TEXTS[st.session_state.language]["rounds_label"], [5, 10, 15, 20, 50], index=1)
    st.session_state.language = st.selectbox("Idioma / Language:", ["Español", "English"])
    st.markdown("---")
    st.markdown(TEXTS[st.session_state.language]["instructions"])
    st.markdown("---")
    st.caption("Desarrollado con ❤️ por [Tu Nombre o xAI]" if st.session_state.language == "Español" else "Developed with ❤️ by [Your Name or xAI]")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    lang = st.session_state.language
    dificultades = ["Fácil", "Media", "Difícil"] if lang == "Español" else ["Easy", "Medium", "Hard"]
    st.subheader(TEXTS[lang]["game_title"])
    dificultad = st.selectbox("Selecciona la dificultad:" if lang == "Español" else "Select difficulty:", dificultades)

    # Guía para las notas
    st.info(TEXTS[lang]["guide"], icon="ℹ️")

    if not st.session_state.game_over:
        if st.session_state.nota_actual is None:
            st.session_state.nota_actual = generar_nota(dificultad)

        reproducir_nota(st.session_state.nota_actual)

        # Display feedback with highlight effect
        if st.session_state.feedback_message:
            if "Correcto" in st.session_state.feedback_message or "Correct" in st.session_state.feedback_message:
                st.markdown(f'<div class="feedback success">{st.session_state.feedback_message}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="feedback error">{st.session_state.feedback_message}</div>', unsafe_allow_html=True)

        # Progress bar and streak counter
        st.progress(st.session_state.attempts / max_attempts)
        st.metric("Racha actual" if lang == "Español" else "Current Streak", st.session_state.streak)

        # Note selection
        NOTAS_WITH_FLATS = ["C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B", "C2"]
        respuesta = st.selectbox(
            TEXTS[lang]["select_note"],
            options=[""] + sorted(set(NOTAS_WITH_FLATS)),
            key=f"respuesta_{st.session_state.attempts}",
            help="Selecciona la nota que escuchaste" if lang == "Español" else "Select the note you heard"
        )
        if st.button(TEXTS[lang]["submit"], key="submit"):
            if respuesta:
                st.session_state.attempts += 1
                correcta = evaluar_respuesta(respuesta, st.session_state.nota_actual)
                if correcta:
                    st.session_state.feedback_message = TEXTS[lang]["correct"]
                    st.session_state.score += 10
                    st.session_state.streak += 1
                else:
                    st.session_state.feedback_message = TEXTS[lang]["incorrect"].format(nota=st.session_state.nota_actual)
                    st.session_state.streak = 0
                st.session_state.history.append((st.session_state.nota_actual, respuesta, correcta))
                st.session_state.nota_actual = None
                if st.session_state.attempts >= max_attempts:
                    st.session_state.game_over = True
                time.sleep(1.5)  # Feedback visibility
                st.rerun()
            else:
                st.warning(TEXTS[lang]["select_note_warning"])

with col2:
    lang = st.session_state.language
    if st.session_state.game_over:
        st.markdown(TEXTS[lang]["game_over"].format(score=st.session_state.score, total=max_attempts * 10))
        if not st.session_state.player_name:
            nombre = st.text_input(TEXTS[lang]["enter_name"])
            if st.button(TEXTS[lang]["save_score"]):
                if nombre.strip():
                    st.session_state.player_name = nombre.strip()
                    guardar_en_leaderboard(nombre.strip(), st.session_state.score)
                    st.success(TEXTS[lang]["score_saved"])
                    time.sleep(1)
                    st.rerun()
        else:
            st.subheader(TEXTS[lang]["leaderboard"])
            if st.session_state.leaderboard:
                for i, (player, score) in enumerate(st.session_state.leaderboard, 1):
                    st.markdown(
                        f'<div style="padding: 10px; border-radius: 5px; background-color: #e0e7ff; margin-bottom: 5px; color: #1f2a44;"><strong>{i}. {player}</strong>: {score} puntos</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.info(TEXTS[lang]["no_scores"])
            mostrar_progreso()
            if st.button(TEXTS[lang]["play_again"], key="play_again"):
                resetear_juego()
                st.rerun()

# Custom CSS for styling and accessibility
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px;
    }
    .stSelectbox {
        background-color: #b6becf;
        border-radius: 5px;
    }
    .stProgress > div > div {
        background-color: #4CAF50;
    }
    .feedback.success {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
        animation: fadeInOut 1.5s;
    }
    .feedback.error {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
        animation: fadeInOut 1.5s;
    }
    @keyframes fadeInOut {
        0% { opacity: 0; }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% { opacity: 0; }
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #1f2a44 !important;
    }
    /* Mobile responsiveness */
    @media (max-width: 600px) {
        .stColumn {
            width: 100% !important;
            margin-bottom: 10px;
        }
    }
</style>
""", unsafe_allow_html=True)
