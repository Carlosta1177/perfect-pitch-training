import streamlit as st
import random
import time
import numpy as np
import matplotlib.pyplot as plt

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
    st.audio(f"https://piano-mp3.s3.amazonaws.com/{nota}.mp3")

def evaluar_respuesta(respuesta, nota_correcta):
    return respuesta.upper().strip() == nota_correcta

def resetear_juego():
    st.session_state.score = 0
    st.session_state.attempts = 0
    st.session_state.game_over = False
    st.session_state.history = []

def guardar_en_leaderboard(nombre, puntaje):
    st.session_state.leaderboard.append((nombre, puntaje))
    st.session_state.leaderboard = sorted(st.session_state.leaderboard, key=lambda x: x[1], reverse=True)[:10]

def mostrar_progreso():
    st.subheader("📈 Progreso del Usuario")
    intentos = list(range(1, len(st.session_state.history)+1))
    aciertos = [1 if correcto else 0 for _, _, correcto in st.session_state.history]
    plt.plot(intentos, np.cumsum(aciertos), marker='o')
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
    nota_actual = generar_nota(dificultad)
    reproducir_nota(nota_actual)

    respuesta = st.text_input("¿Qué nota escuchaste?", key=f"respuesta_{st.session_state.attempts}")

    if st.button("Enviar respuesta"):
        st.session_state.attempts += 1
        correcta = evaluar_respuesta(respuesta, nota_actual)
        if correcta:
            st.success("✅ ¡Correcto!")
            st.session_state.score += 10
        else:
            st.error(f"❌ Incorrecto. Era {nota_actual}")
        st.session_state.history.append((nota_actual, respuesta, correcta))

        if st.session_state.attempts >= 10:
            st.session_state.game_over = True
        else:
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

        if st.button("🔁 Jugar de nuevo"):
            resetear_juego()
            st.rerun()

