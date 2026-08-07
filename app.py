# Web interface for the system

# Import essential libraries
import streamlit as st
import cv2
import time
import os
import json
from main import HandDetector
from media_controller import MediaController

# Page configuration
st.set_page_config(
    page_title="MagicHand",
    layout="wide"
)

# Load config
with open("config.json", 'r') as f:
    config = json.load(f)

LOGO_PATH = "magichand_logo.png"

def display_logo(size=200):
    """Display the MagicHand logo"""
    # Check if logo file exists locally
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=size)
    else:
        # Fallback: show emoji if no logo found
        st.markdown(f"<h1 style='font-size: {size//2}px; text-align: center;'>🖐️</h1>", unsafe_allow_html=True)

# Top header
st.markdown("<br>", unsafe_allow_html=True)  # Small spacing at top

# Logo centered
col_logo_center = st.columns([1, 1, 1])
with col_logo_center[1]: 
    display_logo(200)

# Subtitle centered below logo
st.markdown("""
<div style='text-align: center;'>
    <p style='font-size: 22px; font-weight: 300; color: #aaa; margin-top: -5px;'>
         controleer jouw muziek/video's met simpele hand gebaren
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)  # Small spacing after header
    
with st.sidebar:
    # Logo at top of sidebar
    col_logo_center = st.columns([1, 5, 1])
    with col_logo_center[1]: 
        display_logo(200)
    st.divider()
    
    st.header("📋 Instructies")
    st.markdown("""
    ### Stap 1: Open VLC-mediaplayer
    - Open VLC-media player op je desktop
    - Laad jouw muziek/video's
    
    ### Stap 2 : Start Camera
    - Click de "Start Camera" knop op de web-app
    - Sta voor jouw camera
    
    ### Stap 3: Maak Gebaren
    
    - **Click op de VLC-mediaplayer venster** om hem als actief te houden
    
    | Gebaar | Actie |
    |---------|---------|
    | ✋ High-Five | Play / Pause |
    | 👊 Vuist | Stop |
    | ✌️ 2 Vingers | Volgende Track |
    | 🤟 3 Vingers | Vorige Track |
    | 🤏 Duim en Wijsvinger Knepen | Volume Controlle |
    
    ### Step 4: Stop MagicHand
    - Click "Stop Camera"
    """)
    
    st.divider()
    st.caption("Gemaakt met ❤️ voor eenvoudige media controlle")

# Initialize session state
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

# Start camera
if start_btn:
    st.session_state.running = True
    st.session_state.controller = MediaController()
    st.session_state.detector = HandDetector()
    
    # Open camera
    cam = config["camera"]
    cap = cv2.VideoCapture(cam["device_id"])
    if not cap.isOpened():
        cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam["frame_width"])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam["frame_height"])
    st.session_state.cap = cap
    
    status_placeholder.success("Camera is begonnen! maak gebaren om VLC-mediaplayer te controlleren.")

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

# Main loop 
if st.session_state.running and st.session_state.cap:
    cap = st.session_state.cap
    detector = st.session_state.detector
    controller = st.session_state.controller
    
    # Show  reminder
    st.warning("⚠️ Zorg ervoor dat VLC-mediaplayer geopend is en het venster actief is!")
    
    # Create a container for the video
    video_container = st.empty()
    gesture_text = st.empty()
    volume_text = st.empty()
    
    # Frame processing loop
    try:
        while st.session_state.running:
            # Read frame
            ret, frame = cap.read()
            if not ret:
                status_placeholder.error("⚠️ Camera error. a.u.b. restarten")
                break
            
            # Process frame for gestures
            processed_frame, data = detector.process_frame(frame, mirror=True)
            
            # Send commands to VLC
            controller.handle_gesture(data)
            
            # Get gesture and volume info
            gesture = data.get('gesture', 'UNKNOWN')
            pinch = data.get('pinch', {'active': False, 'volume': 50, 'direction': ''})
            
            # Map gesture to friendly name
            gesture_names = {
                'OPEN_PALM': '✋ PLAY / PAUSE',
                'FIST': '👊 STOP',
                'TWO_FINGERS': '✌️ VOLGENDE',
                'THREE_FINGERS': '🤟 VORIGE',
                'UNKNOWN': '👋 Aan het wachten voor gebaar...'
            }
            gesture_display = gesture_names.get(gesture, '👋 Aan het wachten...')
            
            # Update session volume
            st.session_state.volume = pinch['volume']
            
            # Track volume direction
            if pinch['active'] and pinch.get('direction', ''):
                st.session_state.volume_direction = pinch['direction']
                st.session_state.volume_display_time = time.time()
            
            # Convert BGR to RGB for Streamlit display
            frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            
            # Display the frame
            video_container.image(frame_rgb, channels="RGB", use_container_width=True)
            
            # Display gesture
            gesture_text.markdown(f"### 🎯 Gebaar: {gesture_display}")
            
            # Show volume direction only when pinching
            if pinch['active'] and pinch.get('direction', ''):
                direction = pinch['direction']
                if direction == 'Higher':
                    volume_text.markdown(f"""
                    <div style="background-color: #1a1a2e; padding: 15px; border-radius: 10px; text-align: center; border: 2px solid #00ff88;">
                        <p style="margin: 0; font-size: 28px; font-weight: bold; color: #00ff88;">
                            🔊 VOLUME <span style="color: #ff6b6b; font-size: 32px;">▲</span>
                        </p>
                        <p style="margin: 0; font-size: 14px; color: #888;">Volume omhoog</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif direction == 'Lower':
                    volume_text.markdown(f"""
                    <div style="background-color: #1a1a2e; padding: 15px; border-radius: 10px; text-align: center; border: 2px solid #ff6b6b;">
                        <p style="margin: 0; font-size: 28px; font-weight: bold; color: #ff6b6b;">
                            🔊 VOLUME <span style="color: #00ff88; font-size: 32px;">▼</span>
                        </p>
                        <p style="margin: 0; font-size: 14px; color: #888;">Volume omlaag</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                # Show waiting state when not pinching
                volume_text.markdown(f"""
                <div style="background-color: #1a1a2e; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #555;">
                    <p style="margin: 0; font-size: 18px; color: #888;">
                        🤏 Knijp duim en wijsvinger voor volume controle
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
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

# Show footer
st.divider()
st.caption("""
**Tips :** 
- Zorg ervoor dat je hand goed verlicht is
- Ga op ongeveer armlengte afstand van de camera staan
- Houd gebaren even vast
- Vergeet niet te blijven op VLC-venster tijdens het maken van gebaren!
""")