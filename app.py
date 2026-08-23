# Web  interface for the  system using Streamlit

# Import esential libraries
import streamlit as st
import cv2
import time
import os
import json
from main import HandDetector
from media_controller import MediaController
import warnings
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['GLOG_minloglevel'] = '2'

#  Page configuration
st.set_page_config(
    page_title="MagicHand",
    layout="centered"
)

# Config manager functions
def load_config():
    """Load settings from config.json """
    with open("config.json", 'r') as f:
        return json.load(f)

def save_config(config):
    """Save settings  to  config.json"""
    with open("config.json", 'w') as f:
        json.dump(config, f, indent=4)

# Load config
config = load_config()

# Load  UI scale from  config
ui_scale = config.get("ui", {}).get("scale", 1.0)

LOGO_PATH = "magichand_logo.png"

def display_logo(size=200):
    """ Display the MagicHand logo """
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=int(size * ui_scale))
    else:
        st.markdown(f"<h1 style='font-size: {int((size//2) * ui_scale)}px; text-align: center;'>🖐️</h1>", unsafe_allow_html=True)

# Custom CSS with UI - scaling
st.markdown(f"""
<style>
    /* Bigger buttons */
    .stButton button {{
        font-size: {int(24 * ui_scale)}px !important;
        padding: {int(15 * ui_scale)}px {int(30 * ui_scale)}px !important;
        height: auto !important;
        min-height: {int(70 * ui_scale)}px !important;
        border-radius: 12px !important;
        font-weight: bold !important;
    }}
    
    /* Bigger text for headers */
    h1 {{
        font-size: {int(48 * ui_scale)}px !important;
        font-weight: bold !important;
    }}
    h2 {{
        font-size: {int(36 * ui_scale)}px !important;
        font-weight: bold !important;
    }}
    h3 {{
        font-size: {int(28 * ui_scale)}px !important;
        font-weight: bold !important;
    }}
    
    /* Bigger text for markdown */
    p, li, div {{
        font-size: {int(18 * ui_scale)}px !important;
        line-height: 1.6 !important;
    }}
    
    /* Bigger text for sidebar */
    .sidebar-content {{
        font-size: {int(18 * ui_scale)}px !important;
    }}
    .sidebar-content h1 {{
        font-size: {int(36 * ui_scale)}px !important;
    }}
    .sidebar-content h2 {{
        font-size: {int(28 * ui_scale)}px !important;
    }}
    .sidebar-content h3 {{
        font-size: {int(22 * ui_scale)}px !important;
    }}
    
    /* Bigger labels and select boxes */
    .stSelectbox label, .stSlider label, .stRadio label {{
        font-size: {int(18 * ui_scale)}px !important;
        font-weight: bold !important;
    }}
    .stSelectbox div, .stSlider div {{
        font-size: {int(18 * ui_scale)}px !important;
    }}
    
    /* Bigger slider values */
    .stSlider [data-testid="stSliderTickBar"] {{
        font-size: {int(16 * ui_scale)}px !important;
    }}
    
    /* Bigger radio buttons */
    .stRadio label {{
        font-size: {int(20 * ui_scale)}px !important;
        padding: {int(8 * ui_scale)}px 0 !important;
    }}
    
    /* Bigger checkbox and toggle */
    .stCheckbox label, .stToggle label {{
        font-size: {int(18 * ui_scale)}px !important;
    }}
    
    /* Bigger success/error/warning messages */
    .stAlert {{
        font-size: {int(18 * ui_scale)}px !important;
        padding: {int(15 * ui_scale)}px !important;
    }}
    
    /* Bigger caption */
    .stCaption {{
        font-size: {int(16 * ui_scale)}px !important;
    }}
    
    /* Bigger divider */
    hr {{
        margin: {int(25 * ui_scale)}px 0 !important;
    }}
    
    /* Bigger table text */
    table {{
        font-size: {int(18 * ui_scale)}px !important;
    }}
    th, td {{
        padding: {int(10 * ui_scale)}px !important;
    }}
</style>
""", unsafe_allow_html=True)

#  Sidebar
with st.sidebar:
    #Logo  at top of sidebar
    col_logo_center = st.columns([1, 3, 1])
    with col_logo_center[1]: 
        display_logo(200)
    st.divider()
    

    # Navigation
    st.header("📍 Navigatie")

    page = st.radio(
        ".",
        ["🏠 Homepagina", "📖 Toelichting", "⚙️ Instellingen"],
        index=0,
        label_visibility="collapsed"
    )
    st.divider()
    
    if page == "🏠 Homepagina":
        st.header("📋 Instructies")
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        ### Stap 1: Open VLC - mediaspeler
        - Open VLC - mediaspeler  op je desktop
        - Laad  jouw muziek / video's
        
        ### Stap 2 : Start Camera
        - Click de " Start Camera" knop op de webapplicatie
        - Sta  voor jouw camera
        
        ### Stap 3: Maak Gebaren
        
        - **Click op  de VLC - mediaspeler venster** om hem als actief te  houden
        
        
        **Standaard Gebaar Handleiding**:

        | Gebaar | Actie |
        |---------|---------|
        | ✋ High-Five | Play / Pause |
        | 👊 Vuist | Stop |
        | ✌️ 2 Vingers |  Volgende Track |
        | 🤟 3 Vingers | Vorige Track |
        | 🤏 Duim en Wijsvinger Knijpen | Volume Omhoog / Omlaag |
        
        ### Step 4: Stop MagicHand
        -  Click " Stop Camera"
        """)
        
        st.divider()
        st.caption("Gemaakt met ❤️ voor eenvoudige media controlle")
        st.markdown("Contact: [visionx@gmail.com](mailto:visionx@gmail.com)")
        st.caption("**© MAGICHAND 2026**")

#   Homepage
if page == "🏠 Homepagina":
    #  Top header
    st.markdown("<br>", unsafe_allow_html=True)

    # Logo centered
    col_logo_center = st.columns([1, 1, 1])
    with col_logo_center[1]: 
        display_logo(200)

    # Subtitle centered below  logo
    st.markdown(f"""
    <div style='text-align: center;'>
        <p style='font-size: {int(28 * ui_scale)}px; font-weight: 300; color: #aaa; margin-top: -5px;'>
             controleer jouw muziek / video's met simpele hand gebaren
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    #Initialize sesion state
    if 'running' not in st.session_state:
        st.session_state.running = False
    if 'detector' not in st.session_state:
        st.session_state.detector = None
    if 'controller' not in st.session_state:
        st.session_state.controller = None
    if 'cap' not in st.session_state:
        st.session_state.cap = None
    if 'last_gesture' not in st.session_state:
        st.session_state.last_gesture = ""
    if 'volume' not in st.session_state:
        st.session_state.volume = 50
    if 'volume_direction' not in st.session_state:
        st.session_state.volume_direction = "" 
    if 'volume_display_time' not in st.session_state:
        st.session_state.volume_display_time = 0

    # Placeholder for camera feed
    frame_placeholder = st.empty()
    gesture_placeholder = st.empty()
    volume_placeholder = st.empty()
    status_placeholder = st.empty()

    # Control buttons
    col1, col2 = st.columns(2)

    with col1:
        start_btn = st.button("▶️ Start Camera", type="primary", use_container_width=True)
        
    with col2:
        stop_btn = st.button("⏹️ Stop Camera", use_container_width=True)

    # Camera Start
    if start_btn:
        st.session_state.running = True
        st.session_state.controller = MediaController()
        st.session_state.detector = HandDetector()
        
        # Open camera 
        cam = config["camera"]
        cap = cv2.VideoCapture(cam["device_id"])
        if not cap.isOpened():
            cap = cv2.VideoCapture(1)
        
        #  basis instellingen
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam["frame_width"])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam["frame_height"])
        
        st.session_state.cap = cap
        
        status_placeholder.success("Camera is begonnen. maak gebaren om je VLC - mediaspeler te controleren.")

    # Stop camera
    if stop_btn:
        st.session_state.running = False
        if st.session_state.cap:
            st.session_state.cap.release()
            st.session_state.cap = None
        status_placeholder.info("⏹️ Camera gestopt")
        frame_placeholder.empty()
        gesture_placeholder.empty()
        volume_placeholder.empty()
        st.rerun()

    # Main  loop
    if st.session_state.running and st.session_state.cap:
        cap = st.session_state.cap
        detector = st.session_state.detector
        controller = st.session_state.controller
        
        # Show reminder
        st.warning("⚠️ Zorg ervoor dat VLC - mediaspeler geopend is en als actieve venster is .")
        
        #Create a container for the video
        video_container = st.empty()
        gesture_text = st.empty()
        volume_text = st.empty()
        
        # Frame  processing loop
        try:
            while st.session_state.running:
                # Lees frame op de eenvoudige manier
                ret, frame = cap.read()
                if not ret:
                    # Kleine pauze en opnieuw proberen
                    time.sleep(0.02)
                    continue
                
                # Process  frame for  gestures
                processed_frame, data = detector.process_frame(frame, mirror=True)
                
                # Send commands to VLC
                controller.handle_gesture(data)
                
                # Get gesture and volume info
                gesture = data.get('gesture', 'UNKNOWN')
                pinch = data.get('pinch', {'active': False, 'volume': 50, 'direction': ''})
                
                # Map gesture to friendly name
                gesture_names = {
                    'OPEN_PALM': '✋ High-Five',
                    'FIST': '👊 Vuist',
                    'TWO_FINGERS': '✌️2 Vingers',
                    'THREE_FINGERS': '🤟 3 Vingers',
                    'UNKNOWN': '👋 Aan het wachten voor een gebaar...'
                }
                
                if pinch['active'] and gesture == 'UNKNOWN':
                    gesture_display = f"🤏 Duim en Wijsvinger aan het knijpen"
                else:
                    gesture_display = gesture_names.get(gesture, '👋 Aan het wachten voor een gebaar...')
                    
                # Update session volume
                st.session_state.volume = pinch['volume']
                
                #Track volume direction
                if pinch['active'] and pinch.get('direction', ''):
                    st.session_state.volume_direction = pinch['direction']
                    st.session_state.volume_display_time = time.time()
                
                # Convert  BGR to  RGB for Streamlit display
                frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                
                # Display  the frame
                video_container.image(frame_rgb, channels="RGB", use_container_width=True)
                
                # Display gesture
                gesture_text.markdown(f"""
                <div style='font-size: {int(36 * ui_scale)}px; font-weight: bold; padding: {int(10 * ui_scale)}px;'>
                    <span style='color: #4CBB17;'>Actieve Gebaar:</span> {gesture_display}
                </div>
                """, unsafe_allow_html=True)
                
                #  Show volume direction only when pinching
                if pinch['active'] and pinch.get('direction', '') and gesture == 'UNKNOWN':
                    direction = pinch['direction']
                    if direction == 'Higher':
                        volume_text.markdown(f"""
                        <div style="background-color: #1a1a2e; padding: {int(10 * ui_scale)}px; border-radius: 6px; text-align: center; border: 2px solid #00ff88;">
                            <p style="margin: 0; font-size: {int(24 * ui_scale)}px; font-weight: bold; color: #00ff88;">
                                🔊 VOLUME <span style="color: #ff6b6b; font-size: {int(30 * ui_scale)}px;">▲</span>
                            </p>
                            <p style="margin: 0; font-size: {int(10 * ui_scale)}px; color: #888;">Volume Omhoog</p>
                        </div>
                        """, unsafe_allow_html=True)
                    elif direction == 'Lower':
                        volume_text.markdown(f"""
                        <div style="background-color: #1a1a2e; padding: {int(10 * ui_scale)}px; border-radius: 6px; text-align: center; border: 2px solid #ff6b6b;">
                            <p style="margin: 0; font-size: {int(24 * ui_scale)}px; font-weight: bold; color: #ff6b6b;">
                                🔊 VOLUME <span style="color: #00ff88; font-size: {int(30 * ui_scale)}px;">▼</span>
                            </p>
                            <p style="margin: 0; font-size: {int(10 * ui_scale)}px; color: #888;">Volume Omlaag</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    # Show nothing  when not pinching
                    volume_text.markdown(f"", unsafe_allow_html=True)
                
                # Small delay to prevent CPU overload
                time.sleep(0.03)
                
        except Exception as e:
            status_placeholder.error(f"⚠️ Error: {e}")
            st.session_state.running = False
            if st.session_state.cap:
                st.session_state.cap.release()
                st.session_state.cap = None

    # Cleanup when session ends
    if not st.session_state.running and st.session_state.cap:
        st.session_state.cap.release()
        st.session_state.cap = None
        cv2.destroyAllWindows()

    #Show footer
    st.divider()
    st.caption("""
    **Tips :** 
    - Zorg ervoor dat je hand goed  verlicht is
    - Ga op ongeveer armlengte  afstand van de camera staan
    - Houd gebaren voor 1-2 seconden vast voor de camera
    -  Vergeet niet te blijven  op VLC - mediaspeler venster  tijdens het maken van gebaren
    """)
    
    # Copyright  footer
    st.divider()
    st.markdown("<div style='text-align: center;font-weight: bold;'>© MAGICHAND 2026</div>", unsafe_allow_html=True)

# Explanation page
elif page == "📖 Toelichting":
    st.title("📖 Toelichting")
    st.markdown("Bekijk instructies hieronder  hoe je MagicHand correct gebruikt .")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Video
    st.subheader("🎬 Uitlegvideo")
    st.markdown(" Bekijk deze volledige uitlegvideo van MagicHand :")
    
    #  video link
    video_url = "https://www.youtube.com/watch?v=GeHHho6uqrI"
    st.video(video_url)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Example pictures 
    st.subheader("✋ Voorbeeld afbeeldingen van de Gebaren 👊")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Make 2 rows with  2 photo 's per row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**✋ High-Five**")
        # Photopath
        st.image("high_five.png", use_container_width=True)
    
    with col2:
        st.markdown("**👊 Vuist**")
        st.image("fist.png", use_container_width=True)
        
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("**✌️ 2 Vingers**")
        st.image("two_fingers.png", use_container_width=True)
    
    with col4:
        st.markdown("**🤟 3 Vingers**")
        st.image("three_fingers.png", use_container_width=True)
        
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Make a single centered column for the pinch gesture
    col5, col6, col7 = st.columns([1, 2, 1])
    with col6:
        st.markdown("**🤏 Duim en Wijsvinger knijpen ( Volume Omhoog / Omlaag )**")
        st.image("pinching.png", use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("💡 Tip: Zorg voor  voldoende licht op je  hand en sta op armlengte afstand van de camera ")
    st.divider()
    st.markdown("<div style='text-align: center;font-weight: bold;'>© MAGICHAND 2026</div>", unsafe_allow_html=True)

# Settings pagina
elif page == "⚙️ Instellingen":
    st.title("⚙️ Instellingen")
    
    #  Load current config
    current_config = load_config()
    
    # Create a form for settings
    with st.form("settings_form"):
        st.subheader("📷 Camera Instellingen")
        
        col1, col2 = st.columns(2)
        with col1:
            device_id = st.selectbox(
                "Camera Apparaat",
                options=[0, 1],
                index=current_config["camera"]["device_id"],
                help=" 0 = ingebouwde camera , 1 = externe camera"
            )
        
        with col2:
            resolution = st.selectbox(
                "Resolutie",
                options=["320x240", "640x480", "1280x720"],
                index=["320x240", "640x480", "1280x720"].index(
                    f"{current_config['camera']['frame_width']}x{current_config['camera']['frame_height']}"
                ),
                help="lagere resolutie  = sneller , hogere resolutie = duidelijker"
            )
        
        st.divider()
        st.subheader(" ✌️ Gebaar voor Actie  in VLC - mediaspeler 👊")
        
        #Get current gesture mapping
        gestures = current_config.get("gestures", {})
        
        # Define  available commands
        command_options = ["PLAY_PAUSE", "STOP", "NEXT_TRACK", "PREVIOUS_TRACK"]
        command_labels = {
            "PLAY_PAUSE": "▶️ Play / Pause",
            "STOP": "⏹️ Stop",
            "NEXT_TRACK": "⏭️ Volgende Track",
            "PREVIOUS_TRACK": "⏮️ Vorige Track"
        }
        
        # Gesture mapping  with friendly names
        gesture_friendly = {
            "open_palm": "✋ High-Five",
            "fist": "👊 Vuist",
            "two_fingers": "✌️ 2 Vingers",
            "three_fingers": "🤟 3 Vingers"
        }
        
        # Show  dropdown for each gesture
        gesture_settings = {}
        col1, col2 = st.columns(2)
        
        for i, (gesture_key, gesture_name) in enumerate(gesture_friendly.items()):
            current_command = gestures.get(gesture_key, "PLAY_PAUSE")
            
            if i % 2 == 0:
                with col1:
                    gesture_settings[gesture_key] = st.selectbox(
                        f"{gesture_name}",
                        options=command_options,
                        index=command_options.index(current_command) if current_command in command_options else 0,
                        format_func=lambda x: command_labels.get(x, x),
                        key=f"gesture_{gesture_key}"
                    )
            else:
                with col2:
                    gesture_settings[gesture_key] = st.selectbox(
                        f"{gesture_name}",
                        options=command_options,
                        index=command_options.index(current_command) if current_command in command_options else 0,
                        format_func=lambda x: command_labels.get(x, x),
                        key=f"gesture_{gesture_key}"
                    )
        
        st.divider()
        st.subheader("⏱️ Wachttijd  Instellingen")
        
        col1, col2 = st.columns(2)
        with col1:
            gesture_cooldown = st.slider(
                "Gebaar Wachttijd ( seconden )",
                min_value=0.5,
                max_value=5.0,
                value=float(current_config["cooldowns"]["gesture_cooldown"]),
                step=0.5,
                help="Tijd tussen  hetzelfde gebaar voordat  het opnieuw kan worden geactiveerd"
            )
        
        with col2:
            volume_cooldown = st.slider(
                "Volume Wachttijd ( seconden )",
                min_value=0.01,
                max_value=0.2,
                value=float(current_config["cooldowns"]["volume_cooldown"]),
                step=0.01,
                help="Tijd tussen volume aanpassingen . Lager = sneller en hoger = soepeler"
            )
        
        col1, col2 = st.columns(2)
        with col1:
            stability_frames = st.slider(
                "Stabiliteit Frames",
                min_value=3,
                max_value=20,
                value=int(current_config["cooldowns"]["stability_frames"]),
                step=1,
                help="Aantal  frames dat een  gebaar vastgehouden moet worden voordat het triggert "
            )
        
        st.divider()
        st.subheader("🤏 Kneep Instellingen voor Volume")
        
        col1, col2 = st.columns(2)
        with col1:
            min_ratio = st.slider(
                "Minimale Pinch Ratio",
                min_value=0.05,
                max_value=0.5,
                value=float(current_config["pinch"]["min_ratio"]),
                step=0.01,
                help=" Waarde wanneer vingers volledig  geknepen zijn. Een lagere waarde  = gevoeliger "
            )
        
        with col2:
            max_ratio = st.slider(
                "Maximale  Pinch Ratio",
                min_value=0.3,
                max_value=1.0,
                value=float(current_config["pinch"]["max_ratio"]),
                step=0.01,
                help="Waarde wanneer  vingers volledig open zijn. Een hogere waarde = meer bereik"
            )
        
        col1, col2 = st.columns(2)
        with col1:
            smoothing = st.slider(
                "Smoothing ",
                min_value=0.0,
                max_value=1.0,
                value=float(current_config["pinch"]["smoothing"]),
                step=0.05,
                help="0 = onmiddelijk , 1 = heel langzaam"
            )
        
        with col2:
            step_size = st.slider(
                "Volume  Stap Grootte",
                min_value=1,
                max_value=10,
                value=int(current_config["pinch"]["step_size"]),
                step=1,
                help="Hoeveel volume verandert per stap. Hoe groter , hoe sneller"
            )
        
        st.divider()
        
        # UI- scale setting
        st.subheader("🔍 Weergave Instellingen")
        
        ui_scale_slider = st.slider(
            "UI - Schaalgrootte",
            min_value=0.8,
            max_value=2.0,
            value=float(current_config.get("ui", {}).get("scale", 1.0)),
            step=0.1,
            help="1.0 = normaal , 1.5  = groter , 2.0 = heel groot "
        )
        
        st.divider()
        
        # Save button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            save_btn = st.form_submit_button("💾 Instellingen Opslaan", type="primary", use_container_width=True)
    
    # Handle save
    if save_btn:
        #Build  new config
        width, height = map(int, resolution.split('x'))
        
        new_config = {
            "camera": {
                "device_id": device_id,
                "frame_width": width,
                "frame_height": height
            },
            "ui": {
                "scale": ui_scale_slider
            },
            "gestures": gesture_settings,
            "pinch": {
                "min_ratio": min_ratio,
                "max_ratio": max_ratio,
                "smoothing": smoothing,
                "step_size": step_size
            },
            "cooldowns": {
                "gesture_cooldown": gesture_cooldown,
                "volume_cooldown": volume_cooldown,
                "stability_frames": stability_frames
            }
        }
        
        # Save settings to config.json file
        save_config(new_config)
        
        #  Update the global config variable
        config = load_config()
        
        st.success("✅ Instellingen zijn  opgeslagen. ")
        st.info("Herstart de webapplicatie  om de  nieuwe instellingen te gebruiken . ")
        st.balloons()

    st.divider()
    st.markdown("<div style='text-align: center;font-weight: bold;'>© MAGICHAND 2026</div>", unsafe_allow_html=True)   
    
    