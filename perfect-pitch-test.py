import streamlit as st
import random
import time

# -------------------------------
# CONFIGURACIÓN INICIAL
# -------------------------------
st.set_page_config(page_title="Entrenador de Oído Absoluto", layout="centered")
st.title("🎵 Entrenador de Oído Absoluto")

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
    url = f"https://piano-mp3.s3.amazonaws.com/{nota}.mp3"
    st.audio(url, format="audio/mp3")

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

# -------------------------------
# INTERFAZ DE USUARIO
# -------------------------------
st.subheader("🎧 Escucha la nota y adivina cuál es")

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

        # 🔁 Modo repaso: volver a escuchar notas falladas
        st.subheader("🔁 Repaso de notas falladas")
        fallos = [nota for nota, respuesta, correcto in st.session_state.history if not correcto]
        if fallos:
            for nota in fallos:
                st.markdown(f"❌ Fallaste: {nota}")
                reproducir_nota(nota)
        else:
            st.info("¡No fallaste ninguna nota!")

        if st.button("🔄 Jugar de nuevo"):
            resetear_juego()
            st.rerun()
