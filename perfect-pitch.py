import streamlit as st
import random
import os
import base64
import uuid

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

# Función para cargar o inicializar el leaderboard (persistente)
@st.cache_data
def get_leaderboard():
    return []

# Función para actualizar el leaderboard
def update_leaderboard(player_name, score):
    leaderboard = get_leaderboard()
    leaderboard.append((player_name, score))
    get_leaderboard._cache[0] = sorted(leaderboard, key=lambda x: x[1], reverse=True)[:10]  # Mantener top 10

# Función para resetear el leaderboard
def reset_leaderboard():
    get_leaderboard._cache[0] = []

# Función para reproducir una nota aleatoria, evitando repetición consecutiva
def play_random_note():
    if "last_note" in st.session_state and st.session_state.last_note:
        possible_notes = [note for note in available_notes if note != st.session_state.last_note]
    else:
        possible_notes = available_notes
    note_name = random.choice(possible_notes)
    st.session_state.last_note = note_name
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
        audio_id = str(uuid.uuid4())  # ID único para evitar conflictos en la UI
        md = f"""
            <audio id="{audio_id}" controls autoplay="true" class="w-full max-w-xs mx-auto">
            <source src="data:audio/wav;base64,{b64}" type="audio/wav">
            </audio>
            <script>
            document.getElementById("{audio_id}").volume = 0.5;  // Ajustar volumen
            </script>
        """
        st.markdown(md, unsafe_allow_html=True)

# CSS mejorado con Tailwind y animaciones personalizadas
st.markdown("""
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        @keyframes fadeIn {
            0% { opacity: 0; transform: translateY(10px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        .animate-pulse { animation: pulse 0.5s ease; }
        .animate-fadeIn { animation: fadeIn 0.5s ease forwards; }
        .progress-bar {
            background-color: #e5e7eb;
            border-radius: 9999px;
            overflow: hidden;
            height: 1.5rem;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
        }
        .progress-fill {
            background: linear-gradient(to right, #10b981, #059669);
            height: 100%;
            transition: width 0.3s ease;
        }
        .custom-button {
            transition: all 0.3s ease;
            transform: perspective(1px) translateZ(0);
        }
        .custom-button:hover {
            transform: scale(1.05);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .feedback-correct {
            background: linear-gradient(to right, #10b981, #059669);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .feedback-incorrect {
            background: linear-gradient(to right, #ef4444, #b91c1c);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .leaderboard-item {
            transition: all 0.3s ease;
        }
        .leaderboard-item:hover {
            background-color: #f3f4f6;
            transform: translateX(5px);
        }
    </style>
""", unsafe_allow_html=True)

# Configuración de la aplicación Streamlit
st.markdown("""
    <div class="text-center mb-6 animate-fadeIn">
        <h1 class="text-4xl font-bold text-gray-800 mb-2">🎶 Adivina la Nota 🎶</h1>
        <p class="text-lg text-gray-600">Escucha la nota musical y selecciona la correcta. ¡Juega 10 rondas y acumula hasta 100 puntos!</p>
    </div>
""", unsafe_allow_html=True)

# Inicializar variables de estado
if "note_played" not in st.session_state:
    st.session_state.note_played = None
if "last_note" not in st.session_state:
    st.session_state.last_note = None
if "round" not in st.session_state:
    st.session_state.round = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "name_submitted" not in st.session_state:
    st.session_state.name_submitted = False
if "player_name" not in st.session_state:
    st.session_state.player_name = ""

# Layout con columnas
col1, col2 = st.columns([3, 2], gap="large")

with col1:
    # Mostrar ronda actual y puntaje
    if st.session_state.round > 0 and not st.session_state.game_over:
        st.markdown(f"""
            <div class="text-2xl font-semibold text-gray-800 mb-4 animate-pulse">
                Ronda {st.session_state.round}/10 | Puntaje: {st.session_state.score}
            </div>
        """, unsafe_allow_html=True)
        progress = (st.session_state.round / 10) * 100
        st.markdown(f"""
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress}%"></div>
            </div>
        """, unsafe_allow_html=True)

    # Botón para iniciar o continuar el juego
    if not st.session_state.game_over:
        button_label = "🎵 Reproducir Nota" if st.session_state.round == 0 else "🎵 Siguiente Nota"
        if st.button(button_label, key="play_note", help="Reproduce una nota musical"):
            if st.session_state.round < 10:
                st.session_state.round += 1
                st.session_state.note_played, note_file = play_random_note()
                autoplay_audio(note_file)
            else:
                st.session_state.game_over = True

    # Selección de la respuesta del usuario y verificación
    if st.session_state.note_played and not st.session_state.game_over:
        user_input = st.selectbox(
            "Selecciona la nota que crees que se ha reproducido:",
            [""] + available_notes,
            index=0,
            key=f"select_{st.session_state.round}",
            placeholder="Elige una nota..."
        )
        if st.button("✅ Adivinar", key="guess", help="Confirma tu selección"):
            if user_input:
                if check_answer(user_input, st.session_state.note_played):
                    st.session_state.score += 10
                    st.markdown('<div class="text-2xl font-bold feedback-correct animate-fadeIn">🎉 ¡Correcto! +10 puntos</div>', unsafe_allow_html=True)
                else:
                    st.markdown(
                        f'<div class="text-2xl font-bold feedback-incorrect animate-fadeIn">😕 Incorrecto. La nota era <b>{st.session_state.note_played}</b>.</div>',
                        unsafe_allow_html=True
                    )
                if st.session_state.round < 10:
                    st.markdown('<p class="text-gray-600 mt-2 animate-fadeIn">Haz clic en "Siguiente Nota" para continuar.</p>', unsafe_allow_html=True)
                else:
                    st.session_state.game_over = True

with col2:
    # Mostrar leaderboard
    leaderboard = get_leaderboard()
    st.markdown('<h2 class="text-2xl font-bold text-gray-800 mb-4">🏆 Mejores Puntajes</h2>', unsafe_allow_html=True)
    if leaderboard:
        for i, (player, score) in enumerate(leaderboard, 1):
            st.markdown(
                f'<div class="leaderboard-item p-3 rounded-lg bg-white shadow mb-2"><span class="font-semibold text-gray-700">{i}. {player}</span>: {score} puntos</div>',
                unsafe_allow_html=True
            )
    else:
        st.markdown('<p class="text-gray-600 italic">¡Sé el primero en aparecer aquí!</p>', unsafe_allow_html=True)
    if st.button("🗑️ Resetear Leaderboard", key="reset_leaderboard", help="Borra todos los puntajes"):
        reset_leaderboard()
        st.rerun()

# Mostrar resultado final y solicitar nombre
if st.session_state.game_over and not st.session_state.name_submitted:
    st.markdown(
        f'<div class="text-3xl font-bold text-gray-800 text-center mb-4 animate-pulse">¡Juego Terminado! Puntaje Final: {st.session_state.score}/100</div>',
        unsafe_allow_html=True
    )
    player_name = st.text_input(
        "Ingresa tu nombre para la tabla de ganadores:",
        placeholder="Tu nombre",
        key="player_name_input"
    )
    if st.button("💾 Guardar Puntaje", key="save_score", help="Registra tu puntaje"):
        if player_name.strip():
            st.session_state.player_name = player_name.strip()
            update_leaderboard(st.session_state.player_name, st.session_state.score)
            st.session_state.name_submitted = True
            st.rerun()
        else:
            st.markdown('<p class="text-red-500 animate-fadeIn">Por favor, ingresa un nombre válido.</p>', unsafe_allow_html=True)

# Mostrar resultado final con animación de confeti
if st.session_state.game_over and st.session_state.name_submitted:
    st.markdown(
        f'<div class="text-3xl font-bold text-gray-800 text-center mb-6 animate-pulse">¡Juego Terminado, {st.session_state.player_name}! Puntaje Final: {st.session_state.score}/100</div>',
        unsafe_allow_html=True
    )
    if st.session_state.score >= 80:
        st.markdown("""
            <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
            <script>
            confetti({
                particleCount: 150,
                spread: 90,
                origin: { y: 0.6 },
                colors: ['#10b981', '#059669', '#FFD700']
            });
            </script>
        """, unsafe_allow_html=True)

    if st.button("🔄 Jugar de Nuevo", key="play_again", help="Inicia un nuevo juego"):
        st.session_state.round = 0
        st.session_state.score = 0
        st.session_state.note_played = None
        st.session_state.last_note = None
        st.session_state.game_over = False
        st.session_state.name_submitted = False
        st.session_state.player_name = ""
        st.rerun()
