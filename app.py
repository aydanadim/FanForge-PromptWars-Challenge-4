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

# 2. Side-by-Side Map Buttons (Added unique keys to prevent element duplication)
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

st.divider()

# Render remaining standard quick actions underneath
col1, col2 = st.columns(2)
with col1:
    if st.button(actions[1][0], use_container_width=True):
         st.toast(f"Opening {actions[1][0]}...")
with col2:
    if st.button(actions[2][0], use_container_width=True):
         st.toast(f"Opening {actions[2][0]}...")
