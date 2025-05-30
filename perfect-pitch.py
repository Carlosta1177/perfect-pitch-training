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
    note_name = random.choice(available_notes)
    note_file = os.path.join(WAV_DIRECTORY, note_mapping[note_name])
    return note_name, note_file

# Función para verificar la respuesta del usuario
def check_answer(user_input, correct_note):
    return user_input.lower() == correct_note.lower()

# Función para reproducir audio automáticamente
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

# CSS para mejorar la interfaz
st.markdown("""
    <style>
    .main {
        background-image: url('https://www.transparenttextures.com/patterns/music-sheet.png');
        background-size: cover;
        padding: 20px;
        border-radius: 10px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .score-animation {
        font-size: 24px;
        font-weight: bold;
        color: #FFD700;
        animation: pulse 0.5s ease;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.2); }
        100% { transform: scale(1); }
    }
    .title {
        font-size: 36px;
        color: #2E2E2E;
        text-align: center;
        font-family: 'Arial', sans-serif;
    }
    .subtitle {
        font-size: 18px;
        color: #555;
        text-align: center;
        margin-bottom: 20px;
    }
    .feedback-correct {
        color: #28a745;
        font-size: 20px;
        font-weight: bold;
    }
    .feedback-incorrect {
        color: #dc3545;
        font-size: 20px;
        font-weight: bold;
    }
    .progress-bar {
        background-color: #e0e0e0;
        border-radius: 5px;
        overflow: hidden;
        height: 20px;
        margin: 10px 0;
    }
    .progress-fill {
        background-color: #4CAF50;
        height: 100%;
        transition: width 0.3s ease;
    }
    </style>
""", unsafe_allow_html=True)

# Configuración de la aplicación Streamlit
st.markdown('<div class="title">🎶 Adivina la Nota 🎶</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Escucha la nota y selecciona cuál crees que es. ¡Juega 10 rondas y acumula puntos (10 por acierto)!</div>', unsafe_allow_html=True)

# Inicializar variables de estado
if "note_played" not in st.session_state:
    st.session_state.note_played = None
if "round" not in st.session_state:
    st.session_state.round = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "leaderboard" not in st.session_state:
    st.session_state.leaderboard = []
if "name_submitted" not in st.session_state:
    st.session_state.name_submitted = False
if "player_name" not in st.session_state:
    st.session_state.player_name = ""

# Layout con columnas para una mejor organización
col1, col2 = st.columns([2, 1])

with col1:
    # Mostrar ronda actual y puntaje
    if st.session_state.round > 0 and not st.session_state.game_over:
        st.markdown(f'<div class="score-animation">Ronda {st.session_state.round}/10 | Puntaje: {st.session_state.score}</div>', unsafe_allow_html=True)
        progress = (st.session_state.round / 10) * 100
        st.markdown(f'<div class="progress-bar"><div class="progress-fill" style="width: {progress}%"></div></div>', unsafe_allow_html=True)

    # Botón para iniciar o continuar el juego
    if not st.session_state.game_over:
        button_label = "Reproducir nota" if st.session_state.round == 0 else "Siguiente nota"
        if st.button(button_label):
            if st.session_state.round < 10:
                st.session_state.round += 1
                st.session_state.note_played, note_file = play_random_note()
                autoplay_audio(note_file)
            else:
                st.session_state.game_over = True

    # Selección de la respuesta del usuario y verificación
    if st.session_state.note_played and not st.session_state.game_over:
        user_input = st.selectbox("¿Qué nota crees que se ha reproducido?", available_notes, key=f"select_{st.session_state.round}")

        if st.button("Adivinar"):
            if user_input:
                if check_answer(user_input, st.session_state.note_played):
                    st.session_state.score += 10
                    st.markdown('<div class="feedback-correct">🎉 ¡Correcto! +10 puntos.</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="feedback-incorrect">😕 Incorrecto. La nota era <b>{st.session_state.note_played}</b>.</div>', unsafe_allow_html=True)
                if st.session_state.round < 10:
                    st.write("Haz clic en 'Siguiente nota' para continuar.")
                else:
                    st.session_state.game_over = True

with col2:
    # Mostrar leaderboard
    if st.session_state.leaderboard:
        st.subheader("🏆 Mejores Puntajes")
        for i, (player, score) in enumerate(sorted(st.session_state.leaderboard, key=lambda x: x[1], reverse=True)[:5], 1):
            st.write(f"{i}. {player}: {score} puntos")

# Mostrar resultado final y solicitar nombre
if st.session_state.game_over and not st.session_state.name_submitted:
    st.markdown(f'<div class="score-animation">¡Juego terminado! Tu puntaje final es: {st.session_state.score}/100</div>', unsafe_allow_html=True)
    player_name = st.text_input("Ingresa tu nombre para la tabla de ganadores:")
    if st.button("Guardar puntaje"):
        if player_name.strip():
            st.session_state.player_name = player_name.strip()
            st.session_state.leaderboard.append((st.session_state.player_name, st.session_state.score))
            st.session_state.name_submitted = True
            st.rerun()
        else:
            st.error("Por favor, ingresa un nombre válido.")

# Mostrar resultado final con confetti si el puntaje es alto
if st.session_state.game_over and st.session_state.name_submitted:
    st.markdown(f'<div class="score-animation">¡Juego terminado, {st.session_state.player_name}! Tu puntaje final es: {st.session_state.score}/100</div>', unsafe_allow_html=True)
    if st.session_state.score >= 80:
        st.markdown("""
            <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
            <script>
            confetti({
                particleCount: 100,
                spread: 70,
                origin: { y: 0.6 }
            });
            </script>
        """, unsafe_allow_html=True)

    if st.button("Jugar de nuevo"):
        st.session_state.round = 0
        st.session_state.score = 0
        st.session_state.note_played = None
        st.session_state.game_over = False
        st.session_state.name_submitted = False
        st.session_state.player_name = ""
        st.rerun()
