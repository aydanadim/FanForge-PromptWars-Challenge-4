import streamlit as st
from streamlit_mic_recorder import speech_to_text
import cv2
import numpy as np
from PIL import Image

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

# --- 2. BACKEND: MULTILINGUAL INTENT-AWARE ENGINE ---
def get_translated_welcome(language, time_context):
    translations = {
        "English": {"pre": "Welcome to the stadium! Kickoff is approaching.", "match": "Live match in progress! Feel the energy.", "post": "What a match! Have a safe trip home."},
        "Spanish": {"pre": "¡Bienvenido al estadio! El inicio se acerca.", "match": "¡Partido en vivo! Siente la energía.", "post": "¡Qué partido! Buen viaje a casa."},
        "French": {"pre": "Bienvenue au stade ! Le coup d'envoi approche.", "match": "Match en direct ! Ressentez l'énergie.", "post": "Quel match ! Bon retour chez vous."},
        "Hindi": {"pre": "स्टेडियम में आपका स्वागत है! मैच जल्द ही शुरू होने वाला है।", "match": "लाइव मैच चल रहा है! ऊर्जा महसूस करें।", "post": "क्या शानदार मैच था! आपकी घर वापसी सुरक्षित हो।"}
    }
    phase = "pre" if "Pre-Match" in time_context else "match" if "Match-Time" in time_context else "post"
    return translations.get(language, translations["English"])[phase]

def get_smart_ai_response(prompt, language):
    p = prompt.lower()
    restroom_words = ["restroom", "bathroom", "washroom", "toilet", "toilettes", "baño", "sanitario", "wc", "शौचालय", "टॉयलेट", "बाथरूम"]
    food_words = ["food", "snack", "restaurant", "drink", "water", "hungry", "burger", "hotdog", "comida", "restaurante", "nourriture", "manger", "खाना", "भोजन", "नाश्ता", "रेस्टोरेंट", "भूख"]
    gate_words = ["gate", "exit", "entry", "entrance", "navigation", "map", "puerta", "salida", "porte", "entrée", "गेट", "द्वार", "रास्ता", "निकास", "प्रवेश"]
    score_words = ["score", "match", "win", "goal", "playing", "marcador", "resultado", "स्कोर", "मैच", "गोल", "रन"]

    knowledge_base = {
        "English": {
            "restroom": "🧻 **Facility Locator:** The nearest accessible restroom is 40 meters away behind Section 114. The queue is currently empty.",
            "food": "🍔 **Concessions:** Concession Stand C (2 mins away) has zero wait time for hotdogs, nachos, and cold beverages right now.",
            "gate": "🚶 **Navigation:** Gate B is a 4-minute walk from your current zone. Traffic flow is clear, making it the fastest exit strategy.",
            "score": "⚽ **Match Update:** The score is currently tied at 0-0 in the 35th minute. Team statistics are updating live.",
            "default": "🤖 **FanForge Engine:** I registered your request! Fetching real-time logistical maps for your exact section coordinates."
        },
        "Spanish": {
            "restroom": "🧻 **Localizador:** El baño más cercano está a 40 metros detrás de la Sección 114. Actualmente sin fila.",
            "food": "🍔 **Alimentos:** El puesto C (a 2 min) tiene tiempo de espera cero para hot dogs y bebidas heladas.",
            "gate": "🚶 **Navegación:** La Puerta B está a 4 minutos a pie. El flujo de personas está despejado para una salida rápida.",
            "score": "⚽ **Actualización:** El marcador está 0-0 en el minuto 35. Las estadísticas se actualizan en vivo.",
            "default": "🤖 **Motor FanForge:** ¡Recibী tu consulta! Buscando mapas logísticos en tiempo real para tu sección."
        },
        "French": {
            "restroom": "🧻 **Localisateur:** Les toilettes les plus proches sont à 40 mètres derrière la Section 114. Aucune attente.",
            "food": "🍔 **Restauration:** Le stand C (à 2 min) n'a aucune attente pour les hot-dogs et les boissons fraîches en ce moment.",
            "gate": "🚶 **Navigation:** La Porte B est à 4 minutes à pied. Le flux est fluide pour une évacuation rapide.",
            "score": "⚽ **Direct:** Le score est de 0-0 à la 35ème minute. Les statistiques du match s'actualisent.",
            "default": "🤖 **Assistant FanForge:** Requête bien reçue! Recherche des données logistiques en temps réel pour votre zone."
        },
        "Hindi": {
            "restroom": "🧻 **सुविधा केंद्र:** निकटतम शौचालय धारा 114 के ठीक पीछे 40 मीटर की दूरी पर है। अभी वहां कोई भीड़ नहीं है।",
            "food": "🍔 **खान-पान:** काउंटर C (2 मिनट की दूरी पर) पर अभी हॉटडॉग और ठंडे पेय पदार्थों के लिए बिल्कुल प्रतीक्षा समय नहीं है।",
            "gate": "🚶 **मार्गदर्शन:** गेट B आपके वर्तमान क्षेत्र से 4 मिनट की पैदल दूरी पर है। निकासी के लिए यह मार्ग बिल्कुल साफ है।",
            "score": "⚽ **मैच अपडेट:** 35वें मिनट में स्कोर अभी 0-0 से बराबर है। दोनों टीमों का मुकाबला कड़ा चल रहा है।",
            "default": "🤖 **फैनफोर्ज इंजन:** मुझे आपका अनुरोध मिल गया है! मैं आपके स्टैंड के अनुसार रीयल-टाइम जानकारी खोज रहा हूँ।"
        }
    }

    lang_responses = knowledge_base.get(language, knowledge_base["English"])

    if any(word in p for word in restroom_words):
        return lang_responses["restroom"]
    elif any(word in p for word in food_words):
        return lang_responses["food"]
    elif any(word in p for word in gate_words):
        return lang_responses["gate"]
    elif any(word in p for word in score_words):
        return lang_responses["score"]
    else:
        return lang_responses["default"]

def get_dynamic_actions(time_context):
    if "Pre-Match" in time_context:
        return [("🎟️ Find My Seat (Scan Ticket)", "primary", True), ("🍔 Express Food Pre-order", "secondary", False), ("👕 Merchandise Map", "secondary", False)]
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

lang_codes = {"English": "en", "Spanish": "es", "French": "fr", "Hindi": "hi"}
target_code = lang_codes.get(language, "en")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "temp_voice_input" not in st.session_state:
    st.session_state.temp_voice_input = None
if "scanner_active" not in st.session_state:
    st.session_state.scanner_active = False

# Render Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Render microphone component
voice_text = speech_to_text(
    language=target_code,
    start_prompt="🎵 Tap to Speak",
    stop_prompt="🛑 Stop Recording",
    just_once=True,
    use_container_width=True,
    key="voice_input"
)

if voice_text:
    st.session_state.temp_voice_input = voice_text

# Voice Review Loop
if st.session_state.temp_voice_input:
    st.info(f"🔍 **Voice Transcription Review**\n\nHere is what I heard in **{language}**:\n\n> *\"{st.session_state.temp_voice_input}\"*")
    col_send, col_clear = st.columns(2)
    with col_send:
        if st.button("✅ Confirm & Send", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": st.session_state.temp_voice_input})
            ai_reply = get_smart_ai_response(st.session_state.temp_voice_input, language)
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            st.session_state.temp_voice_input = None
            st.rerun()
    with col_clear:
        if st.button("❌ Clear / Retry", use_container_width=True):
            st.session_state.temp_voice_input = None
            st.rerun()

# Text Input Fallback
text_input = st.chat_input(f"Or type your query here... ({language})")
if text_input:
    st.session_state.messages.append({"role": "user", "content": text_input})
    ai_reply = get_smart_ai_response(text_input, language)
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
    st.rerun()

st.divider()

# --- 6. DYNAMIC QUICK ACTIONS & INTEGRATED TICKET SCANNER ---
# --- 6. DYNAMIC QUICK ACTIONS & INTEGRATED TICKET SCANNER ---
st.markdown("### ⚡ Quick Actions")
actions = get_dynamic_actions(time_context)
primary_action = actions[0]

# Initialize map view session state if it doesn't exist
if "current_map_view" not in st.session_state:
    st.session_state.current_map_view = None
if "scanner_active" not in st.session_state:
    st.session_state.scanner_active = False

# 1. Primary "Find My Seat" Scan Button
if st.button(primary_action[0], type="primary", use_container_width=True):
    st.session_state.scanner_active = True
    st.session_state.current_map_view = None  # Clear open maps when scanning

# 2. Side-by-Side Map Buttons
col_map1, col_map2 = st.columns(2)
with col_map1:
    if st.button("🍔 Concessions Map", use_container_width=True, key="quick_action_concessions_map"):
        st.session_state.current_map_view = "concessions"
        st.session_state.scanner_active = False  # Close scanner if viewing map
with col_map2:
    if st.button("👕 Merchandise Map", use_container_width=True, key="quick_action_merchandise_map"):
        st.session_state.current_map_view = "merchandise"
        st.session_state.scanner_active = False  # Close scanner if viewing map

# --- MAP DISPLAY CONTAINER ---
if st.session_state.current_map_view == "concessions":
    st.write("---")
    st.subheader("🍔 Major Public Gate Concessions Map")
    st.image(
        "https://raw.githubusercontent.com/aydanadim/FanForge-PromptWars-Challenge-4/8f7b0375e747f0a9a54b8481905c8e1d11d57a64/Gemini_Generated_Image_8zemga8zemga8zem.png", 
        use_container_width=True
    )
    if st.button("❌ Close Map", key="close_concessions", use_container_width=True):
        st.session_state.current_map_view = None
        st.rerun()

elif st.session_state.current_map_view == "merchandise":
    st.write("---")
    st.subheader("👕 Major Public Gate Merchandise Map")
    st.image(
        "https://raw.githubusercontent.com/aydanadim/FanForge-PromptWars-Challenge-4/8f7b0375e747f0a9a54b8481905c8e1d11d57a64/Gemini_Generated_Image_bhrqwfbhrqwfbhrq.png", 
        use_container_width=True
    )
    if st.button("❌ Close Map", key="close_merchandise", use_container_width=True):
        st.session_state.current_map_view = None
        st.rerun()

# --- 🎫 THE SCANNER INTERFACE (Renders only when active) ---
if st.session_state.scanner_active:
    st.write("---")
    st.info("📷 **Ticket Scanner Active:** Hold your 6-digit barcode completely steady up to your camera.")
    
    uploaded_frame = st.camera_input("Scan Window", label_visibility="collapsed")
    
    if uploaded_frame:
        pil_image = Image.open(uploaded_frame)
        decoded_objects = decode(pil_image)
        
        if decoded_objects:
            st.success("🎉 **Barcode Read Successfully!**")
            raw_data = decoded_objects[0].data.decode('utf-8')
            
            if len(raw_data) == 6 and raw_data.isdigit():
                section_num = raw_data[:3]
                seat_num = raw_data[3:]
                section_slice = int(section_num[1:]) 
                
                if 1 <= section_slice <= 10:
                    direction, gate = "North Side", "Gate A"
                elif 11 <= section_slice <= 20:
                    direction, gate = "East Side", "Gate B"
                elif 21 <= section_slice <= 30:
                    direction, gate = "South Side", "Gate C"
                elif 31 <= section_slice <= 40:
                    direction, gate = "West Side", "Gate D"
                else:
                    direction, gate = "Main Concourse", "VIP Gate E"
                
                final_output = f"Your seat number is {seat_num} in section {section_num}. Based on your section, please proceed to the **{direction}** and enter through **{gate}**."
                
                st.session_state.messages.append({"role": "user", "content": f"[Scanned Barcode]: {raw_data}"})
                st.session_state.messages.append({"role": "assistant", "content": f"🎟️ **Ticket Processed:** {final_output}"})
                st.session_state.user_gate = gate 
            else:
                st.session_state.messages.append({"role": "assistant", "content": f"🎟️ **Ticket Processed:** Raw data found: {raw_data}."})
                
            st.balloons()
            st.session_state.scanner_active = False
            st.rerun()
        else:
            st.warning("⚠️ Scanner running, but no clear barcode alignment found yet. Please reposition the ticket.")

    if st.button("🛑 Cancel Scan & Close Camera", use_container_width=True):
        st.session_state.scanner_active = False
        st.rerun()
