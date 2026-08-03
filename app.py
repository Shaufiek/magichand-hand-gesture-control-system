"""
Gesture Media Control - Web App
A simple web interface for the hand gesture control system
"""

import streamlit as st
import cv2
import time
import os
import json
from main import HandDetector
from media_controller import MediaController

# Page configuration
st.set_page_config(
    page_title="Gesture Media Control",
    page_icon="🖐️",
    layout="wide"
)

# Load config
with open("config.json", 'r') as f:
    config = json.load(f)

# Title and description
st.title("🖐️ Gesture Media Control")
st.markdown("Control VLC with hand gestures using your webcam")

# Sidebar with instructions
with st.sidebar:
    st.header("📋 Instructions")
    st.markdown("""
    ### Step 1: Open VLC
    - Open VLC manually
    - Load your music or videos
    - **Click on the VLC window** to make it active
    
    ### Step 2: Start Camera
    - Click the "Start Camera" button below
    - Stand in front of your webcam
    
    ### Step 3: Make Gestures
    
    | Gesture | Command |
    |---------|---------|
    | ✋ Open Palm | Play / Pause |
    | 👊 Fist | Stop |
    | ✌️ Two Fingers | Next Track |
    | 🤟 Three Fingers | Previous Track |
    | 🤏 Pinch | Volume Control |
    
    ### Step 4: Stop
    - Click "Stop Camera" or press 'q'
    """)
    
    st.divider()
    st.caption("Made with ❤️ for accessible media control")

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
    
    status_placeholder.success("✅ Camera started! Make gestures to control VLC.")

# Stop camera
if stop_btn:
    st.session_state.running = False
    if st.session_state.cap:
        st.session_state.cap.release()
        st.session_state.cap = None
    status_placeholder.info("⏹️ Camera stopped")
    frame_placeholder.empty()
    gesture_placeholder.empty()
    volume_placeholder.empty()
    st.rerun()

# Main loop (only when running)
if st.session_state.running and st.session_state.cap:
    cap = st.session_state.cap
    detector = st.session_state.detector
    controller = st.session_state.controller
    
    # Show VLC reminder
    st.warning("⚠️ Make sure VLC is open and the window is active!")
    
    # Create a container for the video
    video_container = st.empty()
    gesture_text = st.empty()
    volume_bar = st.empty()
    
    # Frame processing loop
    try:
        while st.session_state.running:
            # Read frame
            ret, frame = cap.read()
            if not ret:
                status_placeholder.error("⚠️ Camera error - please restart")
                break
            
            # Process frame for gestures
            processed_frame, data = detector.process_frame(frame, mirror=True)
            
            # Send commands to VLC
            controller.handle_gesture(data)
            
            # Get gesture and volume info
            gesture = data.get('gesture', 'UNKNOWN')
            pinch = data.get('pinch', {'active': False, 'volume': 50})
            
            # Map gesture to friendly name
            gesture_names = {
                'OPEN_PALM': '✋ PLAY/PAUSE',
                'FIST': '👊 STOP',
                'TWO_FINGERS': '✌️ NEXT',
                'THREE_FINGERS': '🤟 PREV',
                'UNKNOWN': '👋 Waiting...'
            }
            gesture_display = gesture_names.get(gesture, '👋 Waiting...')
            
            # Update session volume
            st.session_state.volume = pinch['volume']
            
            # Convert BGR to RGB for Streamlit display
            frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            
            # Display the frame
            video_container.image(frame_rgb, channels="RGB", use_container_width=True)
            
            # Display gesture
            gesture_text.markdown(f"### 🎯 Gesture: {gesture_display}")
            
            # Display volume bar
            volume = pinch['volume']
            if volume < 30:
                color = "red"
            elif volume < 70:
                color = "orange"
            else:
                color = "green"
            
            volume_bar.markdown(f"""
            <div style="background-color: #333; padding: 10px; border-radius: 10px;">
                <p style="margin: 0; font-weight: bold;">🔊 Volume: {volume}%</p>
                <div style="background-color: #555; border-radius: 5px; height: 20px; width: 100%;">
                    <div style="background-color: {color}; border-radius: 5px; height: 100%; width: {volume}%;"></div>
                </div>
                <p style="margin: 0; font-size: 12px; color: #888;">Pinch closer = quieter, further = louder</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Check for quit key (in browser)
            # Note: 'q' key detection works via the stop button
            
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
**Tips:** 
- Make sure your hand is well-lit
- Stand about arms-length from camera  
- Hold gestures for a moment
- Click VLC window first!
""")