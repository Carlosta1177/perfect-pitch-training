import streamlit as st
import random
import time
import numpy as np
import matplotlib.pyplot as plt
import requests  # Added for URL validation

# -------------------------------
# CONFIGURACIÓN INICIAL
# -------------------------------
st.set_page_config(page_title="🎵 Entrenador Auditivo Pro", layout="centered")
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
    st.session_state.subscription = True  # Simulación de suscripción activa
if "nota_actual" not in st.session_state:
    st.session_state.nota_actual = None  # Store current note

# -------------------------------
# FUNCIONES
# -------------------------------
NOTAS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def generar_nota(dificultad):
    if dificultad == "Fácil":
        return random.choice(NOTAS[:7])
    elif dificultad == "Media":
        return random.choice(NOTAS[:10])
    else:
        return random.choice(NOTAS)

def reproducir_nota(nota):
    try:
        url = f"https://piano-mp3.s3.amazonaws.com/{nota}.mp3"
        # Verify URL accessibility
        response = requests.head(url, timeout=5)
        if response.status_code == 200:
            st.audio(url, format="audio/mp3")
        else:
            st.error(f"❌ Error: No se pudo cargar el audio para la nota {nota}. URL no accesible.")
    except requests.RequestException as e:
        st.error(f"❌ Error al intentar reproducir la nota {nota}: {str(e)}")

def evaluar_respuesta(respuesta, nota_correcta):
    return respuesta.upper().strip() == nota_correcta

def resetear_juego():
    st.session_state.score = 0
    st.session_state.attempts = 0
    st.session_state.game_over = False
    st.session_state.history = []
    st.session_state.player_name = ""
    st.session_state.nota_actual = None

def guardar_en_leaderboard(nombre, puntaje):
    st.session_state.leaderboard.append((nombre, puntaje))
    st.session_state.leaderboard = sorted(st.session_state.leaderboard, key=lambda x: x[1], reverse=True)[:10]

def mostrar_progreso():
    st.subheader("📈 Progreso del Usuario")
    intentos = list(range(1, len(st.session_state.history) + 1))
    aciertos = [1 if correcto else 0 for _, _, correcto in st.session_state.history]
    plt.figure()
    plt.plot(intentos, np.cumsum(aciertos), marker='o', color='#1f77b4')
    plt.xlabel("Intentos")
    plt.ylabel("Aciertos acumulados")
    plt.title("Evolución del rendimiento")
    st.pyplot(plt)

# -------------------------------
# INTERFAZ DE USUARIO
# -------------------------------
if not st.session_state.subscription:
    st.warning("🔒 Esta funcionalidad está disponible solo para usuarios con suscripción activa.")
    st.stop()

st.subheader("🎼 Escucha la nota y adivina cuál es")
dificultad = st.selectbox("Selecciona la dificultad:", ["Fácil", "Media", "Difícil"])

if not st.session_state.game_over:
    # Generate new note only if none exists
    if st.session_state.nota_actual is None:
        st.session_state.nota_actual = generar_nota(dificultad)

    # Add a button to play or replay the note
    if st.button("🎵 Reproducir Nota", key="play_note"):
        reproducir_nota(st.session_state.nota_actual)

    # Display the audio by default on first load
    reproducir_nota(st.session_state.nota_actual)

    respuesta = st.text_input("¿Qué nota escuchaste?", key=f"respuesta_{st.session_state.attempts}")
    if st.button("Enviar respuesta"):
        st.session_state.attempts += 1
        correcta = evaluar_respuesta(respuesta, st.session_state.nota_actual)
        if correcta:
            st.success("✅ ¡Correcto!")
            st.session_state.score += 10
        else:
            st.error(f"❌ Incorrecto. Era {st.session_state.nota_actual}")
        st.session_state.history.append((st.session_state.nota_actual, respuesta, correcta))
        st.session_state.nota_actual = None  # Reset note for next round
        if st.session_state.attempts >= 10:
            st.session_state.game_over = True
        st.rerun()

# -------------------------------
# RESULTADO FINAL Y LEADERBOARD
# -------------------------------
if st.session_state.game_over:
    st.markdown(f"### 🏁 Juego Terminado - Puntaje Final: {st.session_state.score}/100")
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
                    f'<div class="p-2 rounded bg-white shadow mb-1"><strong>{i}. {player}</strong>: {score} puntos</div>',
                    unsafe_allow_html=True
                )
        else:
            st.info("Aún no hay puntajes registrados.")
        mostrar_progreso()
        if st.button("🔁 Jugar de nuevo", key="play_again"):
            resetear_juego()
            st.rerun()
