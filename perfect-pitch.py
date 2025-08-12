import streamlit as st
import random
import time
import numpy as np
import matplotlib.pyplot as plt
import os

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

# Sidebar for settings and instructions
with st.sidebar:
    st.header("Configuración")
    max_attempts = st.selectbox("Número de rondas:", [5, 10, 15, 20, 50], index=1)
    st.markdown("---")
    st.header("Instrucciones")
    st.markdown("""
    - Selecciona la dificultad y el número de rondas.
    - Escucha la nota haciendo clic en el botón de reproducción del audio.
    - Elige la nota que crees que es del menú desplegable.
    - Envía tu respuesta y ve tu progreso.
    - Al final, ingresa tu nombre para la tabla de líderes.
    """)
    st.markdown("---")
    st.caption("Desarrollado con ❤️ por [Tu Nombre o xAI]")

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
    st.session_state.subscription = True  # Simulación de suscripción activa
if "nota_actual" not in st.session_state:
    st.session_state.nota_actual = None
if "feedback_message" not in st.session_state:
    st.session_state.feedback_message = None  # Store feedback message

# -------------------------------
# FUNCIONES
# -------------------------------
NOTAS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B", "C2"]

# Map note names to .wav filenames (added C2)
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

def generar_nota(dificultad):
    if dificultad == "Fácil":
        return random.choice(NOTAS[:7])  # C to G
    elif dificultad == "Media":
        return random.choice(NOTAS[:10])  # C to A
    else:
        return random.choice(NOTAS)  # All notes, including C2

def reproducir_nota(nota):
    try:
        file_name = NOTE_TO_FILE.get(nota)
        if not file_name:
            st.error(f"❌ Error: No se encontró archivo para la nota {nota}")
            return
        file_path = os.path.join("wav", file_name)
        if os.path.exists(file_path):
            st.audio(file_path, format="audio/wav", autoplay=True)  # Autoplay for better UX, browsers may block
        else:
            st.error(f"❌ Error: El archivo {file_path} no existe")
    except Exception as e:
        st.error(f"❌ Error al reproducir la nota {nota}: {str(e)}")

def evaluar_respuesta(respuesta, nota_correcta):
    # Support flats as equivalents
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

def guardar_en_leaderboard(nombre, puntaje):
    st.session_state.leaderboard.append((nombre, puntaje))
    st.session_state.leaderboard = sorted(st.session_state.leaderboard, key=lambda x: x[1], reverse=True)[:10]

def mostrar_progreso():
    st.subheader("📈 Progreso del Usuario")
    intentos = list(range(1, len(st.session_state.history) + 1))
    aciertos = [1 if correcto else 0 for _, _, correcto in st.session_state.history]
    fig, ax = plt.subplots()
    ax.plot(intentos, np.cumsum(aciertos), marker='o', color='#1f77b4')
    ax.set_xlabel("Intentos")
    ax.set_ylabel("Aciertos acumulados")
    ax.set_title("Evolución del rendimiento")
    st.pyplot(fig)
    # Add table for accessibility
    st.table({"Intento": intentos, "Acierto": aciertos})

# -------------------------------
# INTERFAZ DE USUARIO
# -------------------------------
if not st.session_state.subscription:
    st.warning("🔒 Esta funcionalidad está disponible solo para usuarios con suscripción activa.")
    st.stop()

# Main content in columns for better layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🎼 Escucha la nota y adivina cuál es")
    dificultad = st.selectbox("Selecciona la dificultad:", ["Fácil", "Media", "Difícil"])

    # Guía para el formato de las notas (updated to include flats support)
    st.info("""
    **Guía para las notas**: Selecciona la nota que escuches desde el menú desplegable. Las notas sostenidas (sharps) se indican con `#` (ej. `C#` para Do sostenido). Puedes usar bemoles (flats) como equivalentes (ej. `Db` para `C#`). Ejemplos:
    - `C`: Do
    - `C#` o `Db`: Do sostenido / Re bemol
    - `D`: Re
    - `D#` o `Eb`: Re sostenido / Mi bemol
    - `C2`: Do en octava superior
    """)

    if not st.session_state.game_over:
        if st.session_state.nota_actual is None:
            st.session_state.nota_actual = generar_nota(dificultad)

        reproducir_nota(st.session_state.nota_actual)

        # Display feedback if it exists
        if st.session_state.feedback_message:
            if "Correcto" in st.session_state.feedback_message:
                st.success(st.session_state.feedback_message)
            else:
                st.error(st.session_state.feedback_message)

        # Progress bar
        st.progress(st.session_state.attempts / max_attempts)

        # Use selectbox with flats included
        NOTAS_WITH_FLATS = ["C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B", "C2"]
        respuesta = st.selectbox("¿Qué nota escuchaste?", options=[""] + sorted(set(NOTAS_WITH_FLATS)), key=f"respuesta_{st.session_state.attempts}")
        if st.button("Enviar respuesta"):
            if respuesta:
                st.session_state.attempts += 1
                correcta = evaluar_respuesta(respuesta, st.session_state.nota_actual)
                if correcta:
                    st.session_state.feedback_message = "✅ ¡Correcto!"
                    st.session_state.score += 10
                    st.balloons()  # Fun effect on correct
                else:
                    st.session_state.feedback_message = f"❌ Incorrecto. Era {st.session_state.nota_actual}"
                st.session_state.history.append((st.session_state.nota_actual, respuesta, correcta))
                st.session_state.nota_actual = None
                if st.session_state.attempts >= max_attempts:
                    st.session_state.game_over = True
                time.sleep(2)  # Longer delay for feedback visibility
                st.rerun()
            else:
                st.warning("Por favor, selecciona una nota antes de enviar.")

with col2:
    if st.session_state.game_over:
        st.markdown(f"### 🏁 Juego Terminado - Puntaje Final: {st.session_state.score}/{max_attempts * 10}")
        if not st.session_state.player_name:
            nombre = st.text_input("Ingresa tu nombre para la tabla de ganadores:")
            if st.button("Guardar Puntaje"):
                if nombre.strip():
                    st.session_state.player_name = nombre.strip()
                    guardar_en_leaderboard(nombre.strip(), st.session_state.score)
                    st.success("✅ Puntaje guardado")
                    time.sleep(1)
                    st.rerun()
        else:
            st.subheader("🏆 Tabla de Ganadores")
            if st.session_state.leaderboard:
                for i, (player, score) in enumerate(st.session_state.leaderboard, 1):
                    st.markdown(
                        f'<div style="padding: 10px; border-radius: 5px; background-color: #f0f2f6; margin-bottom: 5px;"><strong>{i}. {player}</strong>: {score} puntos</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.info("Aún no hay puntajes registrados.")
            mostrar_progreso()
            if st.button("🔁 Jugar de nuevo", key="play_again"):
                resetear_juego()
                st.rerun()

# Custom CSS for better styling
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
    }
    .stSelectbox {
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)
