import streamlit as st
from streamlit_mic_recorder import speech_to_text
import time

# --- 1. PAGE CONFIGURATION & CUSTOM CSS ---
st.set_page_config(page_title="FanForge | FIFA 2026", page_icon="⚽", layout="wide")

st.markdown("""
    <style>
    .main {background-color: #FAFAFA;}
    .app-title {
        font-size: 2.5rem;
        font-weight: 900;
        color: #111827;
        margin-bottom: 0px;
        text-transform: uppercase;
        letter-spacing: -1px;
    }
    .app-subtitle {
        color: #6B7280;
        font-size: 1.1rem;
        font-weight: 500;
        margin-top: 0px;
        margin-bottom: 2rem;
    }
    .stButton>button {
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. BACKEND: MOCK GENAI ORCHESTRATION ---
def get_translated_welcome(language, time_context):
    translations = {
        "English": {"pre": "Welcome to the stadium! Kickoff is approaching.", "match": "Live match in progress! Feel the energy.", "post": "What a match! Have a safe trip home."},
        "Spanish": {"pre": "¡Bienvenido al estadio! El inicio se acerca.", "match": "¡Partido en vivo! Siente la energía.", "post": "¡Qué partido! Buen viaje a casa."},
        "French": {"pre": "Bienvenue au stade ! Le coup d'envoi approche.", "match": "Match en direct ! Ressentez l'énergie.", "post": "Quel match ! Bon retour chez vous."},
        "Hindi": {"pre": "स्टेडियम में आपका स्वागत है! मैच जल्द ही शुरू होने वाला है।", "match": "लाइव मैच चल रहा है! ऊर्जा महसूस करें।", "post": "क्या शानदार मैच था! आपकी घर वापसी सुरक्षित हो।"}
    }
    phase = "pre" if "Pre-Match" in time_context else "match" if "Match-Time" in time_context else "post"
    return translations.get(language, translations["English"])[phase]

def get_dynamic_actions(time_context):
    if "Pre-Match" in time_context:
        return [("🎟️ Find My Seat (AR Vision)", "primary", True), ("🍔 Express Food Pre-order", "secondary", False), ("👕 Merchandise Map", "secondary", False)]
    elif "Match-Time" in time_context:
        return [("📊 Live Player Stats", "primary", True), ("💺 Report Spill/Issue", "secondary", False), ("🥤 Order Drink to Seat", "secondary", False)]
    else:
        return [("🚊 Smart Egress & Transit Route", "primary", True), ("🚕 Call Ride-Share", "secondary", False), ("⭐ Match Highlights", "secondary", False)]

# --- 3. SIDEBAR: THE CONTEXT ENGINE ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/FIFA_World_Cup_2026_Logo.svg/1024px-FIFA_World_Cup_2026_Logo.svg.png", width=150)
    st.markdown("### ⚙️ Simulator Controls")
    language = st.selectbox("🌐 App Language", ["English", "Spanish", "French", "Hindi"])
    time_context = st.selectbox("⏱️ Match Phase", ["3 Hours Before Kickoff (Pre-Match)", "In-Stadium: 35th Minute (Match-Time)", "30 Mins Post-Match (Egress Phase)"])
    incident = st.toggle("🚨 Simulate Transit/Crowd Alert")

# --- 4. MAIN UI: THE FAN EXPERIENCE ---
st.markdown('<p class="app-title">⚽ FanForge</p>', unsafe_allow_html=True)
st.markdown(f'<p class="app-subtitle">Your Official Matchday Companion • {language}</p>', unsafe_allow_html=True)

if incident:
    st.error("🚨 **LIVE UPDATE:** High foot traffic detected at Gate B. Rerouting map suggestions to Gate C for 15-min faster entry.")

welcome_msg = get_translated_welcome(language, time_context)
st.success(f"**{welcome_msg}**")
st.divider()

# --- 5. THE MULTILINGUAL AI VOICE ASSISTANT ---
st.markdown("### 🎙️ FanForge Voice & Text Assistant")
st.caption("Click the microphone button to speak naturally, or type below.")

# Language ISO mapper for the speech recognizer engine
lang_codes = {"English": "en", "Spanish": "es", "French": "fr", "Hindi": "hi"}
target_code = lang_codes.get(language, "en")

# Unified Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Render browser microphone interface (Zero Setup, Free Transcription)
voice_text = speech_to_text(
    language=target_code,
    start_prompt="🎵 Tap to Speak",
    stop_prompt="🛑 Stop Recording",
    just_once=True,
    use_container_width=True,
    key="voice_input"
)

# Listen for keyboard input as fallback
text_input = st.chat_input(f"Or type your query here... ({language})")

# Resolve which input was given
active_prompt = voice_text if voice_text else text_input

if active_prompt:
    # Display the query in chat
    with st.chat_message("user"):
        st.markdown(active_prompt)
    st.session_state.messages.append({"role": "user", "content": active_prompt})
    
    # Process answer based on context
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        ai_reply = f"*(Processed in {language})* 📍 I heard your request! Based on your live location inside the venue, the nearest facilities matching your query are 40 meters away with normal capacity thresholds."
        response_placeholder.markdown(ai_reply)
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})

st.divider()

# --- 6. DYNAMIC QUICK ACTIONS ---
st.markdown("### ⚡ Quick Actions")
actions = get_dynamic_actions(time_context)

primary_action = actions[0]
if st.button(primary_action[0], type="primary", use_container_width=True):
    if primary_action[2]:
        st.balloons()
    st.toast(f"Launching {primary_action[0]}...", icon="🚀")

col1, col2 = st.columns(2)
with col1:
    if st.button(actions[1][0], use_container_width=True):
         st.toast(f"Opening {actions[1][0]}...")
with col2:
    if st.button(actions[2][0], use_container_width=True):
         st.toast(f"Opening {actions[2][0]}...")
