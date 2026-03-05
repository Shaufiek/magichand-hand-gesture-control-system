# Import essential libraries
import cv2
import time
import os
import glob
import json
from main import HandDetector
from media_controller import MediaController

def main():
    """Main program that ties everything together"""
    print("GESTURE MEDIA CONTROL SYSTEM starting...")
    print("\n")
    print("-"*40)
    print("\n")
    
    # Load camera settings
    with open("config.json", 'r') as f:
        config = json.load(f)
    cam = config["camera"]
    
    # Start the VLC controller
    controller = MediaController()
    
    # Remind user about Important steps for VLC
    print("Important steps:")
    print("1. Open VLC manually")
    print("2. Load your music/files")
    print("3. Click on the VLC window")
    print("\n")
    print("-"*40)
    print("\n")
    input("Press 'Enter' when ready......")
    print("\n")
    print("-"*40)
    print("\n")
    
    # Start the camera
    cap = cv2.VideoCapture(cam["device_id"])
    if not cap.isOpened():
        # Try external camera if built-in fails
        cap = cv2.VideoCapture(1)
    
    # Set camera resolution from config
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam["frame_width"])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam["frame_height"])
    
    # Start the hand detector
    detector = HandDetector()
    
    # Show controls
    print("\n")
    print("-"*40)
    print("\n")
    print("Gestures:")
    print("  ✋ PLAY/PAUSE: Open your hands wide")
    print("  👊 STOP: Make a fist")
    print("  ✌️ NEXT: Show only 2 fingers up")
    print("  🤟 PREV: Show only 3 fingers up")
    print("  🤏 VOLUME: Pinching your tumb and index")
    print("\n")
    print("-"*40)
    print("\n")
    print("Press 'q' to quit")
    print("\n")
    print("-"*40)
    print("\n")
    
    # Main loop that runs until user quits
    while True:
        # Get camera frame
        ret, frame = cap.read()
        if not ret:
            continue
        
        # Detect gestures in this frame
        frame, data = detector.process_frame(frame, mirror=True)
        
        # Send commands to VLC based on gestures
        controller.handle_gesture(data)
        
        # Show camera feed
        cv2.imshow('Gesture Control', frame)
        
        # Check if user pressed 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("\nGESTURE MEDIA CONTROL SYSTEM Stopped.")

if __name__ == "__main__":
    main()